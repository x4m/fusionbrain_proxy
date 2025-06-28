#!/usr/bin/env python3
import base64
import io
import json
import requests
from flask import Flask, request, jsonify, Response
from PIL import Image
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# URL целевого API
TARGET_API_URL = "https://api-key.fusionbrain.ai"

def convert_png_to_jpeg(base64_png_data):
    """
    Конвертирует base64 PNG в base64 JPEG
    """
    try:
        # Декодируем base64
        png_data = base64.b64decode(base64_png_data)
        
        # Открываем изображение с помощью PIL
        image = Image.open(io.BytesIO(png_data))
        
        # Конвертируем в RGB если нужно (PNG может иметь альфа-канал)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Создаем белый фон для альфа-канала
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Сохраняем как JPEG в буфер
        output_buffer = io.BytesIO()
        image.save(output_buffer, format='JPEG', quality=95)
        output_buffer.seek(0)
        
        # Кодируем в base64
        jpeg_base64 = base64.b64encode(output_buffer.getvalue()).decode('utf-8')
        
        return jpeg_base64
        
    except Exception as e:
        logger.error(f"Ошибка при конвертации изображения: {e}")
        return base64_png_data  # Возвращаем оригинал если не удалось конвертировать

def process_response_data(response_data):
    """
    Обрабатывает данные ответа, конвертируя PNG в JPEG если нужно
    """
    try:
        data = json.loads(response_data)
        
        # Проверяем наличие поля files в result
        if isinstance(data, dict) and 'result' in data and isinstance(data['result'], dict):
            if 'files' in data['result'] and isinstance(data['result']['files'], list):
                converted_files = []
                
                for file_data in data['result']['files']:
                    if isinstance(file_data, str):
                        # Конвертируем PNG в JPEG
                        converted_file = convert_png_to_jpeg(file_data)
                        converted_files.append(converted_file)
                        logger.info("Изображение конвертировано из PNG в JPEG")
                    else:
                        converted_files.append(file_data)
                
                data['result']['files'] = converted_files
        
        return json.dumps(data)
        
    except json.JSONDecodeError:
        # Если это не JSON, возвращаем как есть
        return response_data
    except Exception as e:
        logger.error(f"Ошибка при обработке ответа: {e}")
        return response_data

@app.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'])
def proxy(path):
    """
    Проксирует все запросы на целевой API
    """
    # Формируем URL для целевого API
    target_url = f"{TARGET_API_URL}/{path}" if path else TARGET_API_URL
    
    # Копируем параметры запроса
    params = request.args.to_dict()
    
    # Копируем заголовки, исключая некоторые служебные
    headers = {}
    for key, value in request.headers:
        if key.lower() not in ['host', 'content-length']:
            headers[key] = value
    
    # Получаем данные тела запроса
    data = None
    if request.method in ['POST', 'PUT', 'PATCH']:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.get_data()
    
    try:
        logger.info(f"Проксирование {request.method} запроса на {target_url}")
        
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
        
        # Обрабатываем ответ
        response_data = response.text
        
        # Проверяем Content-Type на JSON
        content_type = response.headers.get('content-type', '')
        if 'application/json' in content_type.lower():
            # Обрабатываем JSON ответ
            processed_response = process_response_data(response_data)
        else:
            processed_response = response_data
        
        # Копируем заголовки ответа
        response_headers = {}
        for key, value in response.headers.items():
            if key.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                response_headers[key] = value
        
        return Response(
            processed_response,
            status=response.status_code,
            headers=response_headers
        )
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка при выполнении запроса: {e}")
        return jsonify({"error": "Ошибка при обращении к внешнему API", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return jsonify({"error": "Внутренняя ошибка сервера", "details": str(e)}), 500

@app.route('/health')
def health_check():
    """
    Проверка состояния сервиса
    """
    return jsonify({"status": "healthy", "service": "FusionBrain API Proxy"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False) 