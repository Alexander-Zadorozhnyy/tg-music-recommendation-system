#!/bin/bash
# Скрипт для запуска Music Search API

echo "Запуск Music Search API..."
echo "Документация будет доступна по адресу: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
