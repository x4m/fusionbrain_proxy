#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности конвертации PNG в JPEG
"""
import base64
import json
from main import convert_png_to_jpeg, process_response_data
from PIL import Image
import io

def create_test_png_base64():
    """
    Создает тестовое PNG изображение и возвращает его в формате base64
    """
    # Создаем простое изображение 100x100 с альфа-каналом
    image = Image.new('RGBA', (100, 100), (255, 0, 0, 128))  # Полупрозрачный красный
    
    # Сохраняем в буфер как PNG
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Кодируем в base64
    png_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return png_base64

def test_conversion():
    """
    Тестирует конвертацию PNG в JPEG
    """
    print("🧪 Тестирование конвертации PNG в JPEG...")
    
    # Создаем тестовый PNG
    png_base64 = create_test_png_base64()
    print(f"✅ Создан тестовый PNG (размер: {len(png_base64)} символов)")
    
    # Конвертируем в JPEG
    jpeg_base64 = convert_png_to_jpeg(png_base64)
    print(f"✅ Конвертирован в JPEG (размер: {len(jpeg_base64)} символов)")
    
    # Проверяем, что это действительно JPEG
    try:
        jpeg_data = base64.b64decode(jpeg_base64)
        jpeg_image = Image.open(io.BytesIO(jpeg_data))
        print(f"✅ Формат результата: {jpeg_image.format}")
        print(f"✅ Режим цвета: {jpeg_image.mode}")
        print(f"✅ Размер изображения: {jpeg_image.size}")
        
        if jpeg_image.format == 'JPEG' and jpeg_image.mode == 'RGB':
            print("🎉 Конвертация прошла успешно!")
        else:
            print("❌ Ошибка: неверный формат результата")
            
    except Exception as e:
        print(f"❌ Ошибка при проверке результата: {e}")

def test_json_processing():
    """
    Тестирует обработку JSON ответа
    """
    print("\n🧪 Тестирование обработки JSON ответа...")
    
    # Создаем тестовый PNG
    png_base64 = create_test_png_base64()
    
    # Создаем тестовый JSON ответ
    test_response = {
        "uuid": "test-uuid",
        "status": "success",
        "errorDescription": None,
        "result": {
            "files": [png_base64],
            "censored": False
        }
    }
    
    print("✅ Создан тестовый JSON с PNG изображением")
    
    # Обрабатываем ответ
    processed_json = process_response_data(json.dumps(test_response))
    processed_data = json.loads(processed_json)
    
    print("✅ JSON обработан")
    
    # Проверяем результат
    if 'result' in processed_data and 'files' in processed_data['result']:
        converted_file = processed_data['result']['files'][0]
        
        # Проверяем, что файл конвертирован
        try:
            converted_data = base64.b64decode(converted_file)
            converted_image = Image.open(io.BytesIO(converted_data))
            
            if converted_image.format == 'JPEG':
                print("🎉 JSON обработка прошла успешно!")
                print(f"✅ Изображение конвертировано в {converted_image.format}")
            else:
                print(f"❌ Ошибка: изображение не конвертировано, формат: {converted_image.format}")
                
        except Exception as e:
            print(f"❌ Ошибка при проверке конвертированного изображения: {e}")
    else:
        print("❌ Ошибка: поле files не найдено в обработанном JSON")

def test_invalid_data():
    """
    Тестирует обработку невалидных данных
    """
    print("\n🧪 Тестирование обработки невалидных данных...")
    
    # Тест с невалидным base64
    print("📝 Тест с невалидным base64...")
    result = convert_png_to_jpeg("invalid_base64_data")
    if result == "invalid_base64_data":
        print("✅ Невалидные данные корректно обработаны")
    else:
        print("❌ Ошибка при обработке невалидных данных")
    
    # Тест с невалидным JSON
    print("📝 Тест с невалидным JSON...")
    result = process_response_data("invalid json data")
    if result == "invalid json data":
        print("✅ Невалидный JSON корректно обработан")
    else:
        print("❌ Ошибка при обработке невалидного JSON")

if __name__ == '__main__':
    print("🚀 Запуск тестов конвертации изображений\n")
    
    test_conversion()
    test_json_processing()
    test_invalid_data()
    
    print("\n✨ Тестирование завершено!") 