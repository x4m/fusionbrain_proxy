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

### Режим разработки (с HTTPS поддержкой)
```bash
# Генерация SSL сертификата
./generate_ssl.sh

# Запуск сервера
python main.py
```

### Режим разработки (только HTTP)
```bash
# Если SSL сертификаты не нужны, просто запустите:
python main.py
```

### Продакшн режим

#### С Gunicorn
```bash
# Для HTTPS в продакшн используйте reverse proxy (nginx/apache)
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

#### С Docker
```bash
# Сборка и запуск
docker-compose up -d

# Или напрямую с Docker
docker build -t fusionbrain-proxy .
docker run -d -p 8000:8000 --name fusionbrain-proxy fusionbrain-proxy
```

#### Развертывание на удаленном сервере
```bash
# 1. Клонируем репозиторий
git clone <your-repo-url>
cd hrenator

# 2. Запускаем с Docker (рекомендуется)
docker-compose up -d

# 3. Или устанавливаем зависимости и запускаем напрямую
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./generate_ssl.sh
python main.py
```

**Доступные адреса:**
- HTTP:  `http://localhost:8000`
- HTTPS: `https://localhost:8000` (при наличии SSL сертификатов)

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

Сервис поддерживает подробное логирование:

### Уровни логирования
- **INFO** (по умолчанию) - основные операции
- **DEBUG** - детальная отладочная информация
- **WARNING** - предупреждения
- **ERROR** - ошибки

### Настройка уровня логирования
```bash
# Через переменную окружения
export LOG_LEVEL=DEBUG
python main.py

# Или в Docker
docker run -e LOG_LEVEL=DEBUG -p 8000:8000 fusionbrain-proxy
```

### Что логируется
- 🔄 **Входящие запросы**: метод, URL, IP клиента, User-Agent
- 📊 **Производительность**: время ответа API, общее время запроса
- 🖼️ **Конвертация изображений**: детали процесса PNG → JPEG
- 🌐 **Сетевые операции**: соединения, таймауты, ошибки
- 🔐 **SSL/TLS**: загрузка сертификатов, ошибки шифрования
- 📄 **Размеры данных**: входящие и исходящие данные

## Порты

По умолчанию сервис запускается на порту 8000. Вы можете изменить это в файле `main.py` или при запуске через gunicorn.

## Требования

- Python 3.7+
- Flask >= 2.3.0
- requests >= 2.31.0
- Pillow >= 10.0.0
- gunicorn >= 21.0.0 (для продакшн)

## Переменные окружения

| Переменная | Значение по умолчанию | Описание |
|------------|----------------------|----------|
| `LOG_LEVEL` | `INFO` | Уровень логирования (DEBUG, INFO, WARNING, ERROR) |
| `PYTHONUNBUFFERED` | - | Отключает буферизацию вывода Python |

### Пример использования
```bash
# Детальное логирование
export LOG_LEVEL=DEBUG
python main.py

# Продакшн режим с минимальным логированием
export LOG_LEVEL=WARNING
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

## HTTPS поддержка

Сервис поддерживает HTTPS для безопасной передачи данных:

### Автоматическая генерация SSL сертификата
```bash
./generate_ssl.sh
```

### Ручная генерация SSL сертификата
```bash
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 \
  -subj "/C=RU/ST=Moscow/L=Moscow/O=FusionBrain Proxy/CN=localhost"
```

### Файлы сертификатов
- `cert.pem` - SSL сертификат
- `key.pem` - приватный ключ

⚠️ **Важно**: Сертификаты не включены в git и генерируются на каждом сервере отдельно.

## Безопасность

⚠️ **Важно**: 
- Этот сервис пересылает все заголовки, включая токены авторизации
- Используйте HTTPS для защиты передаваемых данных
- Убедитесь, что вы используете его в безопасной среде
- Не логируйте чувствительные данные 