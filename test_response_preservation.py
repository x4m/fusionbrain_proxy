#!/usr/bin/env python3
"""
Тест для проверки сохранения оригинального формата ответов
без поля files или с файлами, не требующими конвертации
"""
from main import process_response_data
import json

def test_preserve_original_response():
    """
    Тестирует, что ответы без поля files возвращаются без изменений
    """
    print("🧪 Тестирование сохранения оригинального ответа...")
    
    # Тестовый ответ без поля files (как /pipelines endpoint)
    original_response = '{"status":"success","data":[{"id":"1","name":"pipeline1"},{"id":"2","name":"pipeline2"}]}'
    
    print(f"📝 Оригинальный ответ: {len(original_response)} символов")
    print(f"📄 Содержимое: {original_response}")
    
    # Обрабатываем через наш процессор
    processed_response = process_response_data(original_response)
    
    print(f"📝 Обработанный ответ: {len(processed_response)} символов")
    print(f"📄 Содержимое: {processed_response}")
    
    # Проверяем, что ответы идентичны
    if original_response == processed_response:
        print("✅ Тест пройден: ответ не изменился")
        return True
    else:
        print("❌ Тест провален: ответ изменился")
        print(f"Разница в размере: {len(processed_response) - len(original_response)} символов")
        return False

def test_preserve_response_with_empty_files():
    """
    Тестирует ответ с пустым массивом files
    """
    print("\n🧪 Тестирование ответа с пустым массивом files...")
    
    original_response = '{"uuid":"test","status":"success","result":{"files":[],"censored":false}}'
    
    print(f"📝 Оригинальный ответ: {len(original_response)} символов")
    
    processed_response = process_response_data(original_response)
    
    print(f"📝 Обработанный ответ: {len(processed_response)} символов")
    
    if original_response == processed_response:
        print("✅ Тест пройден: ответ с пустым files не изменился")
        return True
    else:
        print("❌ Тест провален: ответ с пустым files изменился")
        return False

def test_response_formatting_preservation():
    """
    Тестирует сохранение форматирования JSON
    """
    print("\n🧪 Тестирование сохранения форматирования JSON...")
    
    # JSON с нестандартным форматированием
    original_response = '{ "status" : "success" , "data" : [ { "id" : "1" } ] }'
    
    print(f"📝 Оригинальный ответ: {len(original_response)} символов")
    print(f"📄 Форматирование: {repr(original_response)}")
    
    processed_response = process_response_data(original_response)
    
    print(f"📝 Обработанный ответ: {len(processed_response)} символов")
    print(f"📄 Форматирование: {repr(processed_response)}")
    
    if original_response == processed_response:
        print("✅ Тест пройден: форматирование сохранено")
        return True
    else:
        print("❌ Тест провален: форматирование изменилось")
        return False

def test_response_with_image_conversion():
    """
    Тестирует, что при конвертации изображений ответ действительно изменяется
    """
    print("\n🧪 Тестирование конвертации изображений...")
    
    # Создаем простой base64 для имитации изображения
    fake_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    original_response = f'{{"uuid":"test","status":"success","result":{{"files":["{fake_png_base64}"],"censored":false}}}}'
    
    print(f"📝 Оригинальный ответ: {len(original_response)} символов")
    
    processed_response = process_response_data(original_response)
    
    print(f"📝 Обработанный ответ: {len(processed_response)} символов")
    
    if original_response != processed_response:
        print("✅ Тест пройден: ответ с изображением был обработан")
        
        # Проверяем, что структура JSON сохранилась
        try:
            original_data = json.loads(original_response)
            processed_data = json.loads(processed_response)
            
            if (original_data['uuid'] == processed_data['uuid'] and
                original_data['status'] == processed_data['status']):
                print("✅ Структура JSON сохранена")
                return True
            else:
                print("❌ Структура JSON нарушена")
                return False
        except Exception as e:
            print(f"❌ Ошибка при парсинге JSON: {e}")
            return False
    else:
        print("❌ Тест провален: ответ с изображением не был обработан")
        return False

if __name__ == '__main__':
    print("🚀 Запуск тестов сохранения формата ответов\n")
    
    tests_passed = 0
    total_tests = 4
    
    if test_preserve_original_response():
        tests_passed += 1
    
    if test_preserve_response_with_empty_files():
        tests_passed += 1
        
    if test_response_formatting_preservation():
        tests_passed += 1
        
    if test_response_with_image_conversion():
        tests_passed += 1
    
    print(f"\n📊 Результаты: {tests_passed}/{total_tests} тестов пройдено")
    
    if tests_passed == total_tests:
        print("🎉 Все тесты успешно пройдены!")
    else:
        print("⚠️ Некоторые тесты провалились")
        
    print("\n💡 Теперь устройства должны получать ответы в оригинальном формате")
    print("   когда конвертация изображений не требуется.") 