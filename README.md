# Система управления библиотекой (Library Management)

Практическая работа по декларативному программированию в Django.

## Описание проекта

Проект демонстрирует применение декларативного подхода в разработке на Django:
- Декларативное описание моделей данных
- Декларативные запросы через Django ORM
- Функциональная обработка данных
- Декларативная валидация в DRF

## Структура проекта

```
library_management/
├── books/                          # Основное приложение
│   ├── models.py                   # Декларативные модели
│   ├── serializers.py              # Декларативные сериализаторы DRF
│   ├── views.py                    # Декларативные API ViewSets
│   ├── urls.py                     # URL маршрутизация
│   ├── admin.py                    # Конфигурация админ-панели
│   ├── tests.py                    # Тесты
│   ├── services/
│   │   ├── library_queries.py      # Декларативные ORM запросы
│   │   └── data_processors.py      # Функциональная обработка данных
│   └── fixtures/
│       └── sample_data.json        # Тестовые данные
├── library_management/             # Настройки проекта
│   ├── settings.py
│   └── urls.py
├── pytest.ini                      # Конфигурация pytest
└── README.md
```

## Установка и запуск

### 1. Установка зависимостей

```bash
pip install django djangorestframework pytest pytest-django
```

### 2. Применение миграций

```bash
cd library_management
python3 manage.py makemigrations
python3 manage.py migrate
```

### 3. Загрузка тестовых данных

```bash
python3 manage.py loaddata books/fixtures/sample_data.json
```

### 4. Создание суперпользователя

```bash
python3 manage.py createsuperuser
```

### 5. Запуск сервера

```bash
python3 manage.py runserver
```

## Использованные декларативные конструкции

### Часть 1: Декларативное моделирование

**models.py**
- Использованы декларативные поля с параметрами `verbose_name`, `unique`, `db_index`
- Применены `ForeignKey` для описания связей
- Использованы `validators` для декларативной валидации на уровне БД
- Созданы кастомные `BookManager` и `BookQuerySet` для декларативного доступа к данным
- Применены `@property` для декларативных вычисляемых полей (`is_overdue`, `is_active`)
- Использованы `Meta` классы для описания индексов, сортировки и других настроек

### Часть 2: Декларативные запросы ORM

**services/library_queries.py**

1. **Запрос 1** (`get_books_after_2010_with_many_pages`):
   - Использован `filter()` для декларативной фильтрации по двум условиям

2. **Запрос 2** (`get_authors_with_book_count`):
   - Применен `annotate()` с `Count()` для добавления вычисляемого поля

3. **Запрос 3** (`get_top_authors_by_total_pages`):
   - Использован `annotate()` с `Sum()` для агрегации
   - Применен slicing `[:limit]` для ограничения результатов

4. **Запрос 4** (`get_readers_with_overdue_books`):
   - Использованы Q-объекты для комбинирования сложных условий
   - Применен `distinct()` для исключения дубликатов

5. **Запрос 5** (`get_books_with_availability_status`):
   - Использован `annotate()` с `Case/When` для декларативного вычисления статуса
   - Применены Q-объекты внутри условий

**Дополнительные запросы**:
- `get_books_with_loan_statistics`: множественные агрегации с условной фильтрацией через `filter=Q(...)`
- `get_popular_books`: использование F-объектов для сравнения полей

### Часть 3: Функциональная обработка данных

**services/data_processors.py**

- `calculate_reading_time`: чистая функция с использованием `map()` и lambda
- `calculate_reading_time_comprehension`: альтернатива через list comprehension
- `filter_books_by_genre`: использование `filter()` с lambda
- `group_books_by_author`: dict comprehension для группировки
- `calculate_total_pages`: применение `reduce()` для агрегации
- `get_books_statistics`: комбинация set comprehension и list comprehension
- `get_report_data`: масштабная функция с использованием list comprehension и dict comprehension
- `compose` и `pipe`: функции высшего порядка для композиции

### Часть 4: Декларативные сериализаторы и валидация

**serializers.py**

- Использован `ModelSerializer` для декларативного описания полей
- Применены `SerializerMethodField` и `source` для связанных данных
- Созданы методы `validate_*` для декларативной валидации отдельных полей
- Реализован метод `validate()` для комплексной валидации
- Специализированные сериализаторы для разных операций (`BookLoanCreateSerializer`, `BookLoanReturnSerializer`)

**views.py**

- Использованы `ModelViewSet` для декларативного описания CRUD операций
- Применен декоратор `@action` для дополнительных эндпоинтов
- Метод `get_serializer_class()` для декларативного выбора сериализатора

### Бонус 1: Кастомный Manager и QuerySet

**models.py**
- Создан `BookQuerySet` с методами: `available()`, `on_loan()`, `after_year()`, `thick_books()`
- Создан `BookManager`, предоставляющий декларативный интерфейс к QuerySet
- Пример использования: `Book.objects.available()`

### Бонус 2: Тесты

**tests.py**
- Использован pytest с fixtures для подготовки данных
- Декларативные тесты для всех запросов ORM
- Тесты для функциональных процессоров
- Тесты для кастомных менеджеров

## API Endpoints

### Books
- `GET /api/books/` - Список всех книг
- `GET /api/books/{id}/` - Детали книги
- `GET /api/books/available/` - Доступные книги
- `GET /api/books/with_status/` - Книги со статусом

### Authors
- `GET /api/authors/` - Список авторов
- `GET /api/authors/with_statistics/` - Авторы со статистикой

### Readers
- `GET /api/readers/` - Список читателей
- `GET /api/readers/with_active_loans/` - Читатели с активными выдачами

### Loans
- `GET /api/loans/` - Все выдачи
- `POST /api/loans/` - Создать выдачу
- `GET /api/loans/active/` - Активные выдачи
- `GET /api/loans/overdue/` - Просроченные выдачи
- `POST /api/loans/{id}/return_book/` - Вернуть книгу

### Reports
- `GET /api/reports/library_statistics/` - Общая статистика

## Запуск тестов

```bash
pytest
```

Или с подробным выводом:

```bash
pytest -v
```

## Админ-панель

Доступна по адресу: http://localhost:8000/admin/

Настроены все модели с фильтрацией, поиском и оптимизацией запросов.

## Ключевые преимущества декларативного подхода

1. **Читаемость**: Код описывает ЧТО нужно сделать, а не КАК
2. **Выразительность**: Django ORM генерирует оптимальные SQL запросы
3. **Поддерживаемость**: Легко понять бизнес-логику
4. **Безопасность**: Встроенная защита от SQL-инъекций
5. **Тестируемость**: Легко писать тесты для декларативного кода

## Философия проекта

Весь код проекта следует декларативному подходу:
- Модели декларативно описывают структуру данных
- ORM запросы декларативно описывают желаемый результат
- Сериализаторы декларативно описывают трансформацию данных
- Валидаторы декларативно описывают бизнес-правила
- ViewSets декларативно описывают API интерфейс

Минимальное использование императивных циклов и условий. Максимальное использование функциональных и декларативных конструкций Python и Django.
