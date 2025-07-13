#!/usr/bin/env python3
import base64
import io
import json
import requests
from flask import Flask, request, jsonify, Response
from PIL import Image
import logging
import time
import os
from datetime import datetime

# Настройка подробного логирования
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    format=log_format,
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)

# Логгер для мониторинга производительности
perf_logger = logging.getLogger('performance')
perf_logger.setLevel(logging.INFO)

# Логгер для SSL/TLS соединений
ssl_logger = logging.getLogger('ssl')
ssl_logger.setLevel(logging.INFO)

app = Flask(__name__)

# URL целевого API
TARGET_API_URL = "https://api-key.fusionbrain.ai"

def convert_png_to_jpeg(base64_png_data):
    """
    Конвертирует base64 PNG в base64 JPEG
    """
    start_time = time.time()
    try:
        logger.debug(f"Начало конвертации изображения, размер входных данных: {len(base64_png_data)} символов")
        
        # Декодируем base64
        png_data = base64.b64decode(base64_png_data)
        logger.debug(f"Декодированные PNG данные: {len(png_data)} байт")
        
        # Открываем изображение с помощью PIL
        image = Image.open(io.BytesIO(png_data))
        original_format = image.format
        original_mode = image.mode
        original_size = image.size
        
        logger.info(f"Загружено изображение: формат={original_format}, режим={original_mode}, размер={original_size}")
        
        # Конвертируем в RGB если нужно (PNG может иметь альфа-канал)
        if image.mode in ('RGBA', 'LA', 'P'):
            logger.info(f"Конвертация из режима {image.mode} в RGB с белым фоном")
            # Создаем белый фон для альфа-канала
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            logger.info(f"Конвертация из режима {image.mode} в RGB")
            image = image.convert('RGB')
        
        # Сохраняем как JPEG в буфер
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=95)
        output_buffer.seek(0)
        
        # Кодируем в base64
        jpeg_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        end_time = time.time()
        conversion_time = end_time - start_time
        
        logger.info(f"✅ Изображение успешно конвертировано: {original_format} -> JPEG")
        logger.info(f"📊 Размеры: входной={len(base64_png_data)} -> выходной={len(jpeg_base64)} символов")
        perf_logger.info(f"Время конвертации изображения: {conversion_time:.3f}s")
        
        return jpeg_base64
        
    except Exception as e:
        end_time = time.time()
        conversion_time = end_time - start_time
        logger.error(f"❌ Ошибка при конвертации изображения: {e}")
        logger.error(f"⏱️ Время до ошибки: {conversion_time:.3f}s")
        logger.error(f"📊 Размер входных данных: {len(base64_png_data)} символов")
        return base64_png_data  # Возвращаем оригинал если не удалось конвертировать

def process_response_data(response_data):
    """
    Обрабатывает данные ответа, конвертируя PNG в JPEG если нужно
    """
    start_time = time.time()
    try:
        logger.debug(f"Начало обработки ответа, размер данных: {len(response_data)} символов")
        
        data = json.loads(response_data)
        logger.debug("Ответ успешно разобран как JSON")
        
        # Флаг - нужна ли обработка
        needs_processing = False
        
        # Проверяем наличие поля files в result
        if isinstance(data, dict) and 'result' in data and isinstance(data['result'], dict):
            if 'files' in data['result'] and isinstance(data['result']['files'], list):
                files_count = len(data['result']['files'])
                logger.info(f"🖼️ Найдено {files_count} файл(ов) для обработки в поле 'files'")
                converted_files = []
                
                for idx, file_data in enumerate(data['result']['files']):
                    if isinstance(file_data, str):
                        logger.info(f"📋 Обработка файла {idx + 1}/{files_count}")
                        # Конвертируем PNG в JPEG
                        converted_file = convert_png_to_jpeg(file_data)
                        converted_files.append(converted_file)
                        if converted_file != file_data:
                            logger.info(f"✅ Файл {idx + 1} успешно конвертирован")
                            needs_processing = True
                        else:
                            logger.warning(f"⚠️ Файл {idx + 1} не был конвертирован (возможно ошибка)")
                    else:
                        logger.debug(f"📋 Файл {idx + 1} не является строкой, пропускаем")
                        converted_files.append(file_data)
                
                if needs_processing:
                    data['result']['files'] = converted_files
                    logger.info(f"🎯 Обработка завершена: {files_count} файл(ов)")
                else:
                    logger.debug("Файлы не требовали конвертации, возвращаем оригинальный ответ")
            else:
                logger.debug("Поле 'files' не найдено или не является списком")
        else:
            logger.debug("Структура ответа не содержит 'result.files'")
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        if needs_processing:
            # Только если была конвертация - пересериализуем JSON
            processed_response = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
            logger.debug(f"JSON пересериализован после конвертации")
            logger.debug(f"Размер обработанного ответа: {len(processed_response)} символов")
            perf_logger.info(f"Время обработки ответа: {processing_time:.3f}s")
            return processed_response
        else:
            # Если конвертация не нужна - возвращаем оригинал
            logger.debug("Конвертация не требуется, возвращаем оригинальный ответ")
            logger.debug(f"Размер оригинального ответа: {len(response_data)} символов")
            perf_logger.info(f"Время анализа ответа: {processing_time:.3f}s")
            return response_data
        
    except json.JSONDecodeError as e:
        logger.debug(f"Ответ не является JSON: {str(e)[:100]}...")
        logger.debug("Возвращаем данные без изменений")
        return response_data
    except Exception as e:
        end_time = time.time()
        processing_time = end_time - start_time
        logger.error(f"❌ Ошибка при обработке ответа: {e}")
        logger.error(f"⏱️ Время до ошибки: {processing_time:.3f}s")
        logger.error(f"📊 Размер данных: {len(response_data)} символов")
        return response_data

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def proxy(path):
    """
    Проксирует все запросы на целевой API
    """
    request_start_time = time.time()
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'unknown'))
    user_agent = request.headers.get('User-Agent', 'unknown')
    
    # Формируем URL для целевого API
    target_url = f"{TARGET_API_URL}/{path}" if path else TARGET_API_URL
    
    # Логируем входящий запрос
    logger.info(f"🔄 Входящий запрос: {request.method} {request.url}")
    logger.info(f"👤 Клиент: IP={client_ip}, UA={user_agent[:50]}...")
    logger.info(f"🎯 Цель: {target_url}")
    
    # Копируем параметры запроса
    params = request.args.to_dict()
    if params:
        logger.debug(f"📝 Параметры запроса: {params}")
    
    # Копируем заголовки, исключая некоторые служебные
    headers = {}
    sensitive_headers = ['authorization', 'x-api-key', 'cookie']
    for key, value in request.headers:
        if key.lower() not in ['host', 'content-length']:
            headers[key] = value
            # Логируем заголовки, скрывая чувствительные данные
            if key.lower() in sensitive_headers:
                logger.debug(f"📋 Заголовок: {key}: [СКРЫТО]")
            else:
                logger.debug(f"📋 Заголовок: {key}: {value}")
    
    # Получаем данные тела запроса
    data = None
    data_size = 0
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.is_json:
            data = request.get_json()
            data_size = len(json.dumps(data)) if data else 0
            logger.info(f"📄 JSON данные: {data_size} символов")
            
            # Логируем тело запроса в DEBUG режиме
            if logger.isEnabledFor(logging.DEBUG) and data:
                request_body = json.dumps(data, ensure_ascii=False, indent=2)
                max_request_log_size = 2000
                if len(request_body) <= max_request_log_size:
                    logger.debug(f"📤 Тело JSON запроса: {request_body}")
                else:
                    logger.debug(f"📤 Тело JSON запроса (первые {max_request_log_size} символов): {request_body[:max_request_log_size]}...")
        else:
            data = request.get_data()
            data_size = len(data) if data else 0
            logger.info(f"📄 Бинарные данные: {data_size} байт")
            
            # Логируем бинарные данные в DEBUG режиме (только размер и тип)
            if logger.isEnabledFor(logging.DEBUG) and data:
                content_type = request.headers.get('Content-Type', 'unknown')
                logger.debug(f"📤 Бинарное тело запроса: {data_size} байт, Content-Type: {content_type}")
                if data_size <= 200:  # Только маленькие бинарные данные
                    logger.debug(f"📤 Содержимое (hex): {data.hex()}")
    
    try:
        logger.info(f"🚀 Отправляем {request.method} запрос на {target_url}")
        api_start_time = time.time()
        
        # Выполняем запрос к целевому API
        if data is not None:
            if isinstance(data, dict):
                response = requests.request(
                    method=request.method,
                    url=target_url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=30
                )
            else:
                response = requests.request(
                    method=request.method,
                    url=target_url,
                    params=params,
                    data=data,
                    headers=headers,
                    timeout=30
                )
        else:
            response = requests.request(
                method=request.method,
                url=target_url,
                params=params,
                headers=headers,
                timeout=30
            )
        
        api_end_time = time.time()
        api_response_time = api_end_time - api_start_time
        
        logger.info(f"📥 Получен ответ: статус={response.status_code}, размер={len(response.text)} символов")
        perf_logger.info(f"Время ответа API: {api_response_time:.3f}s")
        
        # Обрабатываем ответ
        response_data = response.text
        
        # Логируем полное тело ответа в DEBUG режиме
        if logger.isEnabledFor(logging.DEBUG):
            max_log_size = 5000  # Максимальный размер для логирования
            if len(response_data) <= max_log_size:
                logger.debug(f"📄 Полное тело ответа: {response_data}")
            else:
                logger.debug(f"📄 Тело ответа (первые {max_log_size} символов): {response_data[:max_log_size]}...")
                logger.debug(f"📄 Тело ответа (последние 500 символов): ...{response_data[-500:]}")
            
            # Логируем заголовки ответа
            logger.debug("📋 Заголовки ответа:")
            for header_name, header_value in response.headers.items():
                logger.debug(f"   {header_name}: {header_value}")
        
        # Проверяем Content-Type на JSON
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type.lower():
            logger.info("🔄 Обрабатываем JSON ответ")
            # Обрабатываем JSON ответ
            processed_response = process_response_data(response_data)
            
            # Логируем обработанный ответ в DEBUG режиме если он изменился
            if logger.isEnabledFor(logging.DEBUG) and processed_response != response_data:
                logger.debug("🔄 Ответ был изменен после обработки")
                max_processed_log_size = 5000
                if len(processed_response) <= max_processed_log_size:
                    logger.debug(f"📄 Обработанный ответ: {processed_response}")
                else:
                    logger.debug(f"📄 Обработанный ответ (первые {max_processed_log_size} символов): {processed_response[:max_processed_log_size]}...")
                    logger.debug(f"📄 Обработанный ответ (последние 500 символов): ...{processed_response[-500:]}")
            elif logger.isEnabledFor(logging.DEBUG):
                logger.debug("🔄 Ответ не изменился после обработки")
        else:
            logger.debug(f"📄 Ответ не JSON (Content-Type: {content_type}), возвращаем как есть")
            processed_response = response_data
        
        # Копируем заголовки ответа
        response_headers = {}
        for key, value in response.headers.items():
            if key.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                response_headers[key] = value
        
        request_end_time = time.time()
        total_request_time = request_end_time - request_start_time
        
        logger.info(f"✅ Запрос завершен успешно: {response.status_code}")
        perf_logger.info(f"Общее время запроса: {total_request_time:.3f}s")
        perf_logger.info(f"Размеры: запрос={data_size}, ответ={len(processed_response)}")
        
        return Response(
            processed_response,
            status=response.status_code,
            headers=response_headers
        )
        
    except requests.exceptions.Timeout as e:
        request_end_time = time.time()
        total_request_time = request_end_time - request_start_time
        logger.error(f"⏰ Таймаут при обращении к API: {target_url}")
        logger.error(f"⏱️ Время до таймаута: {total_request_time:.3f}s")
        return jsonify({"error": "Таймаут при обращении к внешнему API", "details": str(e)}), 504
    except requests.exceptions.ConnectionError as e:
        request_end_time = time.time()
        total_request_time = request_end_time - request_start_time
        logger.error(f"🌐 Ошибка соединения с API: {target_url}")
        logger.error(f"⏱️ Время до ошибки: {total_request_time:.3f}s")
        logger.error(f"🔍 Детали: {str(e)}")
        return jsonify({"error": "Ошибка соединения с внешним API", "details": str(e)}), 502
    except requests.exceptions.RequestException as e:
        request_end_time = time.time()
        total_request_time = request_end_time - request_start_time
        logger.error(f"❌ Ошибка при выполнении запроса: {e}")
        logger.error(f"⏱️ Время до ошибки: {total_request_time:.3f}s")
        return jsonify({"error": "Ошибка при обращении к внешнему API", "details": str(e)}), 500
    except Exception as e:
        request_end_time = time.time()
        total_request_time = request_end_time - request_start_time
        logger.error(f"💥 Неожиданная ошибка: {e}")
        logger.error(f"⏱️ Время до ошибки: {total_request_time:.3f}s")
        logger.exception("Полная трассировка ошибки:")
        return jsonify({"error": "Внутренняя ошибка сервера", "details": str(e)}), 500

@app.route('/health')
def health_check():
    """
    Проверка состояния сервиса
    """
    return jsonify({"status": "healthy", "service": "FusionBrain API Proxy"})

if __name__ == '__main__':
    import ssl
    import os
    import sys
    
    # Логируем информацию о запуске
    logger.info("=" * 60)
    logger.info("🚀 FusionBrain API Proxy - запуск сервера")
    logger.info("=" * 60)
    logger.info(f"📅 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"🐍 Python версия: {sys.version.split()[0]}")
    logger.info(f"📂 Рабочая директория: {os.getcwd()}")
    logger.info(f"🎯 Целевой API: {TARGET_API_URL}")
    logger.info(f"📊 Уровень логирования: {log_level}")
    
    # Проверяем наличие SSL сертификатов
    cert_file = 'cert.pem'
    key_file = 'key.pem'
    
    if os.path.exists(cert_file) and os.path.exists(key_file):
        try:
            # Проверяем валидность сертификатов
            ssl_logger.info("🔍 Проверка SSL сертификатов...")
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_file, key_file)
            
            ssl_logger.info(f"📋 Сертификат загружен: {cert_file}")
            ssl_logger.info(f"🔐 Приватный ключ загружен: {key_file}")
            
            logger.info("🔒 Запуск сервера с поддержкой HTTPS на порту 8000")
            logger.info("📋 HTTP:  http://localhost:8000")
            logger.info("🔐 HTTPS: https://localhost:8000")
            logger.info("⚠️  Для HTTPS используется самоподписанный сертификат")
            logger.info("🌐 Готов к приёму соединений...")
            logger.info("=" * 60)
            
            app.run(host='0.0.0.0', port=8000, debug=False, ssl_context=context)
            
        except ssl.SSLError as e:
            ssl_logger.error(f"❌ Ошибка SSL сертификата: {e}")
            logger.error("🔒 Не удалось запустить HTTPS, переключаемся на HTTP")
            logger.info("📋 HTTP: http://localhost:8000")
            logger.info("🌐 Готов к приёму соединений...")
            logger.info("=" * 60)
            app.run(host='0.0.0.0', port=8000, debug=False)
        except Exception as e:
            ssl_logger.error(f"❌ Неожиданная ошибка при настройке SSL: {e}")
            logger.error("🔒 Не удалось запустить HTTPS, переключаемся на HTTP")
            logger.info("📋 HTTP: http://localhost:8000")
            logger.info("🌐 Готов к приёму соединений...")
            logger.info("=" * 60)
            app.run(host='0.0.0.0', port=8000, debug=False)
    else:
        logger.warning("⚠️  SSL сертификаты не найдены")
        logger.info("💡 Для генерации сертификатов выполните: ./generate_ssl.sh")
        logger.info("📋 Запуск только HTTP сервера")
        logger.info("📋 HTTP: http://localhost:8000")
        logger.info("🌐 Готов к приёму соединений...")
        logger.info("=" * 60)
        app.run(host='0.0.0.0', port=8000, debug=False) 