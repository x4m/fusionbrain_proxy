#!/usr/bin/env python3
"""
Тест для проверки DEBUG логирования запросов и ответов
"""
import logging
import io
import json
from main import process_response_data, logger

def setup_debug_logging():
    """
    Настраивает DEBUG логирование для тестов
    """
    # Создаем захватчик логов
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    
    # Добавляем к основному логгеру
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    return log_capture, handler

def test_debug_response_logging():
    """
    Тестирует логирование ответов в DEBUG режиме
    """
    print("🧪 Тестирование DEBUG логирования ответов...")
    
    log_capture, handler = setup_debug_logging()
    
    # Тестовый ответ без изображений
    test_response = '{"status":"success","data":[{"id":"1","name":"test"}]}'
    
    # Обрабатываем ответ
    processed = process_response_data(test_response)
    
    # Получаем логи
    log_output = log_capture.getvalue()
    
    # Проверяем что логирование работает
    if "Начало обработки ответа" in log_output:
        print("✅ DEBUG логирование ответов работает")
        
        # Проверяем что есть сообщение о том что ответ не изменился
        if "Конвертация не требуется" in log_output:
            print("✅ Логируется информация о неизменном ответе")
        else:
            print("⚠️ Не найдено сообщение о неизменном ответе")
            
        success = True
    else:
        print("❌ DEBUG логирование ответов не работает")
        success = False
    
    # Очищаем
    logger.removeHandler(handler)
    logger.setLevel(logging.INFO)
    
    return success

def test_debug_image_processing_logging():
    """
    Тестирует логирование при обработке изображений
    """
    print("\n🧪 Тестирование DEBUG логирования конвертации изображений...")
    
    log_capture, handler = setup_debug_logging()
    
    # Тестовый ответ с изображением
    fake_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    test_response = f'{{"uuid":"test","status":"success","result":{{"files":["{fake_image}"],"censored":false}}}}'
    
    # Обрабатываем ответ
    processed = process_response_data(test_response)
    
    # Получаем логи
    log_output = log_capture.getvalue()
    
    success = True
    
    # Проверяем различные сообщения DEBUG логирования
    debug_checks = [
        ("Начало обработки ответа", "начало обработки"),
        ("Найдено", "поиск файлов"),
        ("Загружено изображение", "информация об изображении"),
        ("Конвертация из режима", "процесс конвертации"),
        ("JSON пересериализован", "пересериализация")
    ]
    
    for check_text, description in debug_checks:
        if check_text in log_output:
            print(f"✅ Логируется {description}")
        else:
            print(f"⚠️ Не найдено логирование: {description}")
            success = False
    
    # Очищаем
    logger.removeHandler(handler)
    logger.setLevel(logging.INFO)
    
    return success

def test_log_level_control():
    """
    Тестирует что DEBUG логирование работает только на нужном уровне
    """
    print("\n🧪 Тестирование контроля уровня логирования...")
    
    # Тест с INFO уровнем
    log_capture_info = io.StringIO()
    handler_info = logging.StreamHandler(log_capture_info)
    handler_info.setLevel(logging.INFO)
    
    logger.setLevel(logging.INFO)
    logger.addHandler(handler_info)
    
    test_response = '{"status":"success","data":[{"id":"1"}]}'
    process_response_data(test_response)
    
    log_output_info = log_capture_info.getvalue()
    
    # На INFO уровне не должно быть DEBUG сообщений
    debug_present_in_info = "Начало обработки ответа" in log_output_info
    
    logger.removeHandler(handler_info)
    
    # Тест с DEBUG уровнем
    log_capture_debug = io.StringIO()
    handler_debug = logging.StreamHandler(log_capture_debug)
    handler_debug.setLevel(logging.DEBUG)
    
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler_debug)
    
    process_response_data(test_response)
    
    log_output_debug = log_capture_debug.getvalue()
    
    # На DEBUG уровне должны быть DEBUG сообщения
    debug_present_in_debug = "Начало обработки ответа" in log_output_debug
    
    logger.removeHandler(handler_debug)
    logger.setLevel(logging.INFO)
    
    if not debug_present_in_info and debug_present_in_debug:
        print("✅ Контроль уровня логирования работает корректно")
        return True
    else:
        print("❌ Проблема с контролем уровня логирования")
        print(f"   DEBUG в INFO режиме: {debug_present_in_info}")
        print(f"   DEBUG в DEBUG режиме: {debug_present_in_debug}")
        return False

if __name__ == '__main__':
    print("🚀 Тестирование DEBUG логирования\n")
    
    tests_passed = 0
    total_tests = 3
    
    if test_debug_response_logging():
        tests_passed += 1
        
    if test_debug_image_processing_logging():
        tests_passed += 1
        
    if test_log_level_control():
        tests_passed += 1
    
    print(f"\n📊 Результаты: {tests_passed}/{total_tests} тестов пройдено")
    
    if tests_passed == total_tests:
        print("🎉 DEBUG логирование работает корректно!")
    else:
        print("⚠️ Есть проблемы с DEBUG логированием")
        
    print("\n💡 Для включения DEBUG логирования используйте:")
    print("   export LOG_LEVEL=DEBUG")
    print("   python main.py") 