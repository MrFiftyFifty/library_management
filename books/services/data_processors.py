from functools import reduce
from operator import add
from typing import List, Tuple, Dict, Any


def calculate_reading_time(book_list, pages_per_hour: int = 50) -> List[Tuple[str, float]]:
    """
    Чистая функция для расчета времени чтения книг.
    
    Использует функциональный подход с map() и lambda-выражениями.
    Не изменяет входные данные (иммутабельность).
    
    Args:
        book_list: QuerySet или список книг
        pages_per_hour: Скорость чтения (страниц в час)
    
    Returns:
        Список кортежей (название книги, время чтения в часах)
    """
    return list(map(
        lambda book: (book.title, round(book.pages / pages_per_hour, 2)),
        book_list
    ))


def calculate_reading_time_comprehension(book_list, pages_per_hour: int = 50) -> List[Tuple[str, float]]:
    """
    Альтернативная реализация через списковое включение (list comprehension).
    
    Демонстрирует декларативный подход без явных циклов.
    """
    return [
        (book.title, round(book.pages / pages_per_hour, 2))
        for book in book_list
    ]


def filter_books_by_genre(book_list, genres: List[str]) -> List[Any]:
    """
    Чистая функция фильтрации книг по жанрам.
    
    Использует filter() и lambda для декларативной фильтрации.
    """
    return list(filter(
        lambda book: book.genre in genres,
        book_list
    ))


def group_books_by_author(book_list) -> Dict[str, List[str]]:
    """
    Группировка книг по авторам через dict comprehension.
    
    Декларативно описываем желаемую структуру данных.
    """
    authors = {book.author.name for book in book_list}
    
    return {
        author: [book.title for book in book_list if book.author.name == author]
        for author in authors
    }


def calculate_total_pages(book_list) -> int:
    """
    Вычисление общего количества страниц через reduce.
    
    Функциональный подход к агрегации данных.
    """
    return reduce(
        lambda total, book: total + book.pages,
        book_list,
        0
    )


def get_books_statistics(book_list) -> Dict[str, Any]:
    """
    Сбор статистики по книгам через функциональные преобразования.
    
    Комбинирует несколько функциональных подходов.
    """
    if not book_list:
        return {
            'total_books': 0,
            'total_pages': 0,
            'average_pages': 0,
            'genres': []
        }
    
    pages = [book.pages for book in book_list]
    
    return {
        'total_books': len(book_list),
        'total_pages': sum(pages),
        'average_pages': round(sum(pages) / len(pages), 2),
        'genres': list({book.genre for book in book_list})
    }


def transform_queryset_to_dict(queryset, fields: List[str]) -> List[Dict[str, Any]]:
    """
    Преобразование QuerySet в список словарей.
    
    Использует list comprehension для декларативной трансформации.
    """
    return [
        {field: getattr(obj, field) for field in fields}
        for obj in queryset
    ]


def get_report_data() -> Dict[str, Any]:
    """
    Формирование данных для отчета.
    
    Использует функциональные преобразования и dict comprehension.
    Объединяет результаты различных запросов в единую структуру.
    """
    from books.services.library_queries import (
        get_books_after_2010_with_many_pages,
        get_authors_with_book_count,
        get_top_authors_by_total_pages,
        get_readers_with_overdue_books,
        get_books_with_availability_status
    )
    
    recent_thick_books = list(get_books_after_2010_with_many_pages())
    authors_stats = list(get_authors_with_book_count())
    top_authors = list(get_top_authors_by_total_pages())
    overdue_readers = list(get_readers_with_overdue_books())
    books_status = list(get_books_with_availability_status())
    
    return {
        'recent_thick_books': {
            'count': len(recent_thick_books),
            'books': [
                {
                    'title': book.title,
                    'author': book.author.name,
                    'year': book.publication_year,
                    'pages': book.pages
                }
                for book in recent_thick_books
            ]
        },
        'authors_statistics': [
            {
                'name': author.name,
                'country': author.country,
                'books_count': author.books_count
            }
            for author in authors_stats
        ],
        'top_authors': [
            {
                'name': author.name,
                'total_pages': author.total_pages or 0
            }
            for author in top_authors
        ],
        'overdue_readers': [
            {
                'name': reader.name,
                'email': reader.email
            }
            for reader in overdue_readers
        ],
        'books_availability': {
            status: len([b for b in books_status if b.status == status])
            for status in ['в наличии', 'выдана', 'просрочена']
        }
    }


def compose(*functions):
    """
    Композиция функций для декларативного построения цепочек обработки.
    
    Пример функционального программирования высшего порядка.
    """
    return reduce(
        lambda f, g: lambda x: f(g(x)),
        functions,
        lambda x: x
    )


def pipe(value, *functions):
    """
    Pipeline для последовательного применения функций.
    
    Декларативно описываем поток преобразований данных.
    """
    return reduce(
        lambda v, func: func(v),
        functions,
        value
    )
