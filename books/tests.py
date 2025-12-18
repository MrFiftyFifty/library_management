import pytest
from datetime import date, timedelta
from django.utils import timezone
from books.models import Author, Book, Reader, BookLoan
from books.services.library_queries import (
    get_books_after_2010_with_many_pages,
    get_authors_with_book_count,
    get_top_authors_by_total_pages,
    get_readers_with_overdue_books,
    get_books_with_availability_status
)
from books.services.data_processors import (
    calculate_reading_time,
    calculate_reading_time_comprehension,
    group_books_by_author,
    get_books_statistics
)


@pytest.fixture
def sample_authors(db):
    """Фикстура для создания тестовых авторов."""
    authors = [
        Author.objects.create(name="Лев Толстой", country="Россия", birth_date=date(1828, 9, 9)),
        Author.objects.create(name="Федор Достоевский", country="Россия", birth_date=date(1821, 11, 11)),
        Author.objects.create(name="George Orwell", country="UK", birth_date=date(1903, 6, 25)),
    ]
    return authors


@pytest.fixture
def sample_books(db, sample_authors):
    """Фикстура для создания тестовых книг."""
    books = [
        Book.objects.create(
            title="Война и мир",
            isbn="1234567890123",
            publication_year=2015,
            pages=1225,
            author=sample_authors[0],
            genre="fiction"
        ),
        Book.objects.create(
            title="Анна Каренина",
            isbn="1234567890124",
            publication_year=2012,
            pages=864,
            author=sample_authors[0],
            genre="fiction"
        ),
        Book.objects.create(
            title="Преступление и наказание",
            isbn="1234567890125",
            publication_year=2011,
            pages=430,
            author=sample_authors[1],
            genre="fiction"
        ),
        Book.objects.create(
            title="1984",
            isbn="1234567890126",
            publication_year=2008,
            pages=328,
            author=sample_authors[2],
            genre="sci_fi"
        ),
    ]
    return books


@pytest.fixture
def sample_readers(db):
    """Фикстура для создания тестовых читателей."""
    readers = [
        Reader.objects.create(name="Иван Иванов", email="ivan@example.com"),
        Reader.objects.create(name="Петр Петров", email="petr@example.com"),
    ]
    return readers


@pytest.fixture
def sample_loans(db, sample_books, sample_readers):
    """Фикстура для создания тестовых выдач."""
    today = timezone.now().date()
    
    loans = [
        BookLoan.objects.create(
            book=sample_books[0],
            reader=sample_readers[0],
            planned_return_date=today + timedelta(days=14)
        ),
        BookLoan.objects.create(
            book=sample_books[2],
            reader=sample_readers[1],
            planned_return_date=today - timedelta(days=5),
        ),
    ]
    return loans


@pytest.mark.django_db
class TestDeclarativeQueries:
    """Тесты для декларативных запросов ORM."""
    
    def test_books_after_2010_with_many_pages(self, sample_books):
        """Запрос 1: Книги после 2010 года с более чем 300 страницами."""
        result = list(get_books_after_2010_with_many_pages())
        
        assert all(book.publication_year > 2010 for book in result)
        assert all(book.pages > 300 for book in result)
        
        titles = [book.title for book in result]
        assert "Война и мир" in titles
        assert "Анна Каренина" in titles
    
    def test_authors_with_book_count(self, sample_books):
        """Запрос 2: Количество книг каждого автора."""
        result = list(get_authors_with_book_count())
        
        assert len(result) == 3
        
        tolstoy = next(a for a in result if a.name == "Лев Толстой")
        assert tolstoy.books_count == 2
        
        dostoevsky = next(a for a in result if a.name == "Федор Достоевский")
        assert dostoevsky.books_count == 1
    
    def test_top_authors_by_total_pages(self, sample_books):
        """Запрос 3: Топ авторов по общему количеству страниц."""
        result = list(get_top_authors_by_total_pages(limit=2))
        
        assert len(result) == 2
        
        assert result[0].name == "Лев Толстой"
        assert result[0].total_pages == 2089
    
    def test_readers_with_overdue_books(self, sample_loans):
        """Запрос 4: Читатели с просроченными книгами."""
        result = list(get_readers_with_overdue_books())
        
        assert len(result) == 1
        assert result[0].name == "Петр Петров"
    
    def test_books_with_availability_status(self, sample_loans):
        """Запрос 5: Книги со статусом доступности."""
        result = list(get_books_with_availability_status())
        
        statuses = {book.title: book.status for book in result}
        
        assert statuses["Война и мир"] == "выдана"
        assert statuses["Преступление и наказание"] == "просрочена"


@pytest.mark.django_db
class TestCustomManagers:
    """Тесты для кастомных менеджеров и QuerySet."""
    
    def test_available_books(self, sample_loans):
        """Тест декларативного метода available()."""
        available = list(Book.objects.available())
        
        assert len(available) == 2
        
        titles = [book.title for book in available]
        assert "Анна Каренина" in titles
        assert "1984" in titles
    
    def test_on_loan_books(self, sample_loans):
        """Тест декларативного метода on_loan()."""
        on_loan = list(Book.objects.on_loan())
        
        titles = [book.title for book in on_loan]
        assert "Война и мир" in titles
        assert "Преступление и наказание" in titles


@pytest.mark.django_db
class TestFunctionalProcessors:
    """Тесты для функциональных процессоров данных."""
    
    def test_calculate_reading_time(self, sample_books):
        """Тест функции расчета времени чтения с map()."""
        result = calculate_reading_time(sample_books, pages_per_hour=100)
        
        assert len(result) == 4
        assert result[0] == ("Война и мир", 12.25)
        assert result[1] == ("Анна Каренина", 8.64)
    
    def test_calculate_reading_time_comprehension(self, sample_books):
        """Тест функции расчета времени чтения с list comprehension."""
        result = calculate_reading_time_comprehension(sample_books, pages_per_hour=100)
        
        assert len(result) == 4
        assert result[0] == ("Война и мир", 12.25)
    
    def test_group_books_by_author(self, sample_books):
        """Тест группировки книг по авторам."""
        result = group_books_by_author(sample_books)
        
        assert len(result) == 3
        assert len(result["Лев Толстой"]) == 2
        assert "Война и мир" in result["Лев Толстой"]
        assert "Анна Каренина" in result["Лев Толстой"]
    
    def test_get_books_statistics(self, sample_books):
        """Тест получения статистики по книгам."""
        result = get_books_statistics(sample_books)
        
        assert result['total_books'] == 4
        assert result['total_pages'] == 2847
        assert result['average_pages'] == 711.75
        assert 'fiction' in result['genres']
        assert 'sci_fi' in result['genres']


@pytest.mark.django_db
class TestModelProperties:
    """Тесты для декларативных свойств моделей."""
    
    def test_loan_is_overdue_property(self, sample_loans):
        """Тест свойства is_overdue."""
        active_loan = sample_loans[0]
        overdue_loan = sample_loans[1]
        
        assert not active_loan.is_overdue
        assert overdue_loan.is_overdue
    
    def test_loan_is_active_property(self, sample_loans):
        """Тест свойства is_active."""
        loan = sample_loans[0]
        
        assert loan.is_active
        
        loan.actual_return_date = timezone.now().date()
        loan.save()
        
        assert not loan.is_active
