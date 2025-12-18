# Система управления библиотекой

Практическая работа по декларативному программированию в Django.

## Установка

```bash
pip install django djangorestframework pytest pytest-django
python3 manage.py migrate
python3 manage.py loaddata books/fixtures/sample_data.json
python3 manage.py runserver
```

## Декларативные конструкции

**Часть 1: Модели** - Кастомные Manager/QuerySet, валидаторы, @property для is_overdue/is_active

**Часть 2: ORM запросы** - annotate(), aggregate(), Q, F, Case/When для 5 обязательных запросов

**Часть 3: Функциональная обработка** - map(), filter(), reduce(), list/dict comprehensions, compose/pipe

**Часть 4: DRF** - ModelSerializer, validate_* методы, специализированные сериализаторы, @action декоратор

**Бонус:** Кастомный BookManager с available()/on_loan() + 13 pytest тестов

## Тестирование

```bash
pytest -v
```

## API

- `/api/books/` - Книги (available, with_status)
- `/api/authors/` - Авторы (with_statistics)
- `/api/readers/` - Читатели (with_active_loans)
- `/api/loans/` - Выдачи (active, overdue, return_book)
- `/api/reports/library_statistics/` - Статистика
