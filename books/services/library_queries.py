from django.db.models import Q, F, Count, Sum, Case, When, Value, CharField
from django.utils import timezone
from books.models import Book, Author, Reader, BookLoan


def get_books_after_2010_with_many_pages():
    """
    Запрос 1: Все книги, выпущенные после 2010 года, с количеством страниц больше 300.
    
    Декларативный подход: описываем условия фильтрации, не указывая как именно выполнять запрос.
    """
    return Book.objects.filter(
        publication_year__gt=2010,
        pages__gt=300
    )


def get_authors_with_book_count():
    """
    Запрос 2: Количество книг каждого автора.
    
    Использует annotate() для декларативного добавления вычисляемого поля.
    """
    return Author.objects.annotate(
        books_count=Count('books')
    ).order_by('-books_count')


def get_top_authors_by_total_pages(limit=5):
    """
    Запрос 3: Топ-5 самых популярных авторов по общему количеству страниц в их книгах.
    
    Декларативно описываем агрегацию и сортировку.
    """
    return Author.objects.annotate(
        total_pages=Sum('books__pages')
    ).order_by('-total_pages')[:limit]


def get_readers_with_overdue_books():
    """
    Запрос 4: Список читателей с просроченными книгами.
    
    Использует Q-объекты для декларативного описания сложных условий:
    - фактическая дата возврата NULL (книга не возвращена)
    - И планируемая дата возврата меньше сегодняшней даты
    """
    today = timezone.now().date()
    
    return Reader.objects.filter(
        Q(loans__actual_return_date__isnull=True) &
        Q(loans__planned_return_date__lt=today)
    ).distinct()


def get_books_with_availability_status():
    """
    Запрос 5: Для каждой книги вычислить статус доступности.
    
    Декларативное описание бизнес-логики через annotate() с Case/When:
    - "в наличии" - нет активных выдач
    - "просрочена" - есть активная выдача с просроченной датой
    - "выдана" - есть активная выдача в срок
    """
    today = timezone.now().date()
    
    return Book.objects.annotate(
        status=Case(
            When(
                Q(bookloan__actual_return_date__isnull=True) &
                Q(bookloan__planned_return_date__lt=today),
                then=Value('просрочена')
            ),
            When(
                bookloan__actual_return_date__isnull=True,
                then=Value('выдана')
            ),
            default=Value('в наличии'),
            output_field=CharField()
        )
    ).distinct()


def get_books_with_loan_statistics():
    """
    Дополнительный запрос: Книги со статистикой выдач.
    
    Декларативно описываем множественные агрегации и условные подсчёты.
    """
    return Book.objects.annotate(
        total_loans=Count('bookloan'),
        active_loans=Count(
            'bookloan',
            filter=Q(bookloan__actual_return_date__isnull=True)
        ),
        overdue_loans=Count(
            'bookloan',
            filter=Q(
                bookloan__actual_return_date__isnull=True,
                bookloan__planned_return_date__lt=timezone.now().date()
            )
        )
    )


def get_popular_books(min_loans=3):
    """
    Дополнительный запрос: Популярные книги с минимальным количеством выдач.
    
    Использует F-объект для сравнения с аннотированным полем.
    """
    return Book.objects.annotate(
        loan_count=Count('bookloan')
    ).filter(
        loan_count__gte=min_loans
    ).order_by('-loan_count')


def get_readers_with_active_loans():
    """
    Дополнительный запрос: Читатели с активными выдачами и количеством книг на руках.
    """
    return Reader.objects.annotate(
        active_loans_count=Count(
            'loans',
            filter=Q(loans__actual_return_date__isnull=True)
        )
    ).filter(
        active_loans_count__gt=0
    ).order_by('-active_loans_count')
