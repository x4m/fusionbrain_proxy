#!/bin/bash

# Скрипт для генерации самоподписанного SSL сертификата
# для HTTPS поддержки FusionBrain API Proxy

echo "🔐 Генерация SSL сертификата для HTTPS..."

# Генерируем самоподписанный сертификат
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/C=RU/ST=Moscow/L=Moscow/O=FusionBrain Proxy/CN=localhost"

if [ -f "cert.pem" ] && [ -f "key.pem" ]; then
    echo "✅ SSL сертификат успешно создан!"
    echo "📁 Файлы созданы:"
    echo "   - cert.pem (сертификат)"
    echo "   - key.pem (приватный ключ)"
    echo ""
    echo "🚀 Теперь можно запустить сервер с HTTPS поддержкой:"
    echo "   python main.py"
    echo ""
    echo "🔗 Доступные URL:"
    echo "   HTTP:  http://localhost:8000"
    echo "   HTTPS: https://localhost:8000"
else
    echo "❌ Ошибка при создании SSL сертификата"
    exit 1
fi 