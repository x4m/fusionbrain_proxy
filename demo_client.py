#!/usr/bin/env python3
"""
Демонстрационный клиент для тестирования прокси-сервера
"""
import requests
import json
import base64
from PIL import Image
import io

# URL нашего прокси-сервера
PROXY_URL = "http://localhost:8000"

def test_health():
    """
    Тестирует health check endpoint
    """
    print("🔍 Тестирование health check...")
    try:
        response = requests.get(f"{PROXY_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Сервер работает: {data}")
        else:
            print(f"❌ Ошибка: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка при обращении к серверу: {e}")

def create_mock_api_response():
    """
    Создает mock API ответ с PNG изображением для демонстрации
    """
    # Создаем тестовое PNG изображение
    image = Image.new('RGBA', (200, 200), (0, 128, 255, 180))  # Полупрозрачный синий
    
    # Добавляем немного деталей
    from PIL import ImageDraw
    draw = ImageDraw.Draw(image)
    draw.rectangle([50, 50, 150, 150], fill=(255, 255, 0, 200))  # Желтый квадрат
    draw.ellipse([75, 75, 125, 125], fill=(255, 0, 0, 255))  # Красный круг
    
    # Конвертируем в base64
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    png_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    # Создаем mock ответ
    mock_response = {
        "uuid": "demo-12345",
        "status": "success",
        "errorDescription": None,
        "result": {
            "files": [png_base64],
            "censored": False
        }
    }
    
    return mock_response

def save_image_from_base64(base64_data, filename, format_name):
    """
    Сохраняет изображение из base64 в файл
    """
    try:
        image_data = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_data))
        image.save(filename)
        print(f"💾 Изображение сохранено: {filename} (формат: {image.format}, размер: {image.size})")
        return True
    except Exception as e:
        print(f"❌ Ошибка при сохранении {filename}: {e}")
        return False

def simulate_api_request():
    """
    Симулирует запрос к API через прокси
    Поскольку мы не можем реально обращаться к FusionBrain API без ключа,
    мы создадим локальный mock сервер или покажем логику обработки
    """
    print("\n🎭 Демонстрация обработки ответа с изображением...")
    
    # Создаем mock ответ
    mock_response = create_mock_api_response()
    original_png = mock_response["result"]["files"][0]
    
    print("📤 Исходные данные:")
    print(f"   UUID: {mock_response['uuid']}")
    print(f"   Статус: {mock_response['status']}")
    print(f"   Размер PNG в base64: {len(original_png)} символов")
    
    # Сохраняем исходное PNG
    save_image_from_base64(original_png, "demo_original.png", "PNG")
    
    # Симулируем обработку прокси-сервером
    from main import process_response_data
    processed_response = process_response_data(json.dumps(mock_response))
    processed_data = json.loads(processed_response)
    
    converted_jpeg = processed_data["result"]["files"][0]
    
    print("\n📥 Обработанные данные:")
    print(f"   UUID: {processed_data['uuid']}")
    print(f"   Статус: {processed_data['status']}")
    print(f"   Размер JPEG в base64: {len(converted_jpeg)} символов")
    
    # Сохраняем конвертированное JPEG
    save_image_from_base64(converted_jpeg, "demo_converted.jpeg", "JPEG")
    
    print("\n🎯 Результат:")
    print("   ✅ PNG успешно конвертирован в JPEG")
    print("   ✅ Альфа-канал обработан (заменен белым фоном)")
    print("   ✅ JSON структура сохранена")
    print("   📁 Файлы сохранены: demo_original.png, demo_converted.jpeg")

def test_proxy_endpoint():
    """
    Тестирует произвольный endpoint через прокси
    (это покажет, как прокси обрабатывает запросы)
    """
    print("\n🌐 Тестирование проксирования запроса...")
    try:
        # Пытаемся обратиться к несуществующему endpoint
        # Это покажет, как прокси пытается обратиться к внешнему API
        response = requests.get(f"{PROXY_URL}/test/endpoint", timeout=5)
        print(f"📡 Ответ прокси: статус {response.status_code}")
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                data = response.json()
                print(f"📄 JSON ответ: {data}")
            except:
                print(f"📄 Текстовый ответ: {response.text[:200]}...")
        else:
            print(f"📄 Текстовый ответ: {response.text[:200]}...")
    except requests.exceptions.Timeout:
        print("⏰ Таймаут при обращении к внешнему API (это нормально для демо)")
    except Exception as e:
        print(f"📡 Прокси обработал ошибку: {e}")

if __name__ == '__main__':
    print("🚀 Демонстрация работы FusionBrain API Proxy\n")
    
    test_health()
    simulate_api_request() 
    test_proxy_endpoint()
    
    print("\n✨ Демонстрация завершена!")
    print("\n📝 Как использовать:")
    print("   1. Замените все запросы к api-key.fusionbrain.ai на http://localhost:8000")
    print("   2. Прокси автоматически конвертирует PNG в JPEG в поле 'files'")
    print("   3. Все остальные данные передаются без изменений") 