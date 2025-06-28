# FusionBrain API Proxy

Прокси-сервис для api-key.fusionbrain.ai с автоматической конвертацией PNG в JPEG.

## Описание

Этот сервис принимает HTTP запросы и пересылает их в api-key.fusionbrain.ai. Если в ответе присутствует JSON с ключом `files`, содержащий base64-кодированные PNG изображения, сервис автоматически конвертирует их в JPEG формат.

## Функциональность

- ✅ Проксирование всех HTTP методов (GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS)
- ✅ Сохранение всех заголовков и параметров запроса
- ✅ Автоматическая конвертация PNG → JPEG в поле `files`
- ✅ Обработка альфа-канала PNG (замена на белый фон)
- ✅ Логирование операций
- ✅ Health check endpoint

## Установка

1. Установите Python 3.7+
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## Запуск

### Режим разработки
```bash
python main.py
```

### Продакшн режим
```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

Сервис будет доступен по адресу: `http://localhost:8000`

## Использование

Отправляйте запросы на ваш прокси-сервер вместо api-key.fusionbrain.ai:

```bash
# Вместо этого:
curl https://api-key.fusionbrain.ai/some/endpoint

# Используйте:
curl http://localhost:8000/some/endpoint
```

## Примеры

### Обычный запрос
```bash
curl -X GET http://localhost:8000/api/v1/status
```

### POST запрос с JSON
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"prompt": "красивый пейзаж"}'
```

### Проверка состояния сервиса
```bash
curl http://localhost:8000/health
```

## Обработка изображений

Когда API возвращает ответ в формате:
```json
{
  "uuid": "string",
  "status": "string", 
  "errorDescription": "string",
  "result": {
    "files": ["base64_png_data"],
    "censored": false
  }
}
```

Сервис автоматически:
1. Декодирует base64 PNG данные
2. Конвертирует PNG в JPEG (качество 95%)
3. Обрабатывает альфа-канал (заменяет на белый фон)
4. Кодирует обратно в base64
5. Возвращает модифицированный JSON

## Логирование

Сервис логирует:
- Входящие запросы
- Операции конвертации изображений
- Ошибки при обработке

## Порты

По умолчанию сервис запускается на порту 8000. Вы можете изменить это в файле `main.py` или при запуске через gunicorn.

## Требования

- Python 3.7+
- Flask 2.3.3
- requests 2.31.0
- Pillow 10.0.1
- gunicorn 21.2.0 (для продакшн)

## Безопасность

⚠️ **Важно**: Этот сервис пересылает все заголовки, включая токены авторизации. Убедитесь, что вы используете его в безопасной среде и не логируете чувствительные данные. 