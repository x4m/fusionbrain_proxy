# Changelog

Важные изменения в проекте FusionBrain API Proxy.

## [Текущая версия] - 2025-06-28

### 🚨 КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ - Сохранение формата ответов
**Коммит:** `a920b81`

**Проблема:**
- Устройства не могли разобрать ответы прокси-сервера
- Endpoint `/key/api/v1/pipelines`: 294 символа → 315 символов (+21 байт)
- Все JSON ответы проходили через `json.dumps()`, что изменяло форматирование

**Решение:**
- ✅ Возврат оригинального ответа если конвертация изображений не нужна
- ✅ JSON пересериализация только при реальной конвертации
- ✅ Сохранение пробелов, порядка ключей и форматирования
- ✅ Флаг `needs_processing` для отслеживания изменений

**Результат:**
- Полная совместимость с существующими устройствами
- Сохранение байт-в-байт соответствия для endpoint'ов без изображений

### 📊 Подробное логирование
**Коммит:** `50fc676`

**Добавлено:**
- Детальное логирование запросов (IP, User-Agent, размеры данных)
- Мониторинг производительности (время ответа API, конвертации)
- Маскирование чувствительных заголовков (Authorization, API keys)
- Конфигурируемые уровни логирования через `LOG_LEVEL`
- Логирование SSL/TLS операций

### 🐳 Docker поддержка  
**Коммит:** `c1a495a`

**Добавлено:**
- `Dockerfile` для контейнеризации
- `docker-compose.yml` для простого развертывания
- Инструкции по развертыванию на удаленных серверах

### 🔒 HTTPS поддержка
**Коммит:** `6b5f5c9`

**Добавлено:**
- Автоматическое определение SSL сертификатов
- Скрипт генерации сертификатов `generate_ssl.sh`
- Graceful fallback на HTTP при проблемах с SSL
- Одновременная работа HTTP и HTTPS на порту 8000

## Рекомендации по развертыванию

### Для новых установок:
```bash
git clone <repo>
cd hrenator
docker-compose up -d
```

### Для обновления существующих:
```bash
git pull origin main
docker-compose down
docker-compose up -d --build
```

### Отладка:
```bash
# Детальное логирование
export LOG_LEVEL=DEBUG
python main.py
```

## Совместимость

- ✅ Полная обратная совместимость с существующими клиентами
- ✅ Сохранение формата ответов для всех endpoint'ов  
- ✅ Конвертация изображений PNG → JPEG в поле `files`
- ✅ Поддержка всех HTTP методов и заголовков 