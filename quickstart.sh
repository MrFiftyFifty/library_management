#!/bin/bash

echo "Запуск системы управления библиотекой..."
echo ""

echo "1. Применение миграций..."
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

echo ""
echo "2. Загрузка тестовых данных..."
python3 manage.py loaddata books/fixtures/sample_data.json

echo ""
echo "3. Запуск тестов..."
pytest -v

echo ""
echo "Готово! Для запуска сервера выполните:"
echo "python3 manage.py runserver"
echo ""
echo "API будет доступен по адресу: http://localhost:8000/api/"
echo "Админ-панель: http://localhost:8000/admin/"
