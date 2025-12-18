from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone

from books.models import Book, Author, Reader, BookLoan
from books.serializers import (
    BookSerializer,
    AuthorSerializer,
    ReaderSerializer,
    BookLoanSerializer,
    BookLoanCreateSerializer,
    BookLoanReturnSerializer,
    BookWithStatusSerializer
)
from books.services.library_queries import (
    get_books_with_availability_status,
    get_authors_with_book_count,
    get_readers_with_active_loans
)
from books.services.data_processors import get_report_data


class AuthorViewSet(viewsets.ModelViewSet):
    """
    Декларативный ViewSet для авторов.
    
    Автоматически предоставляет CRUD операции.
    """
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    
    @action(detail=False, methods=['get'])
    def with_statistics(self, request):
        """Декларативный эндпоинт для получения авторов со статистикой книг."""
        authors = get_authors_with_book_count()
        serializer = self.get_serializer(authors, many=True)
        return Response(serializer.data)


class BookViewSet(viewsets.ModelViewSet):
    """
    Декларативный ViewSet для книг.
    
    Предоставляет стандартные операции и дополнительные действия.
    """
    queryset = Book.objects.select_related('author').all()
    serializer_class = BookSerializer
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Декларативный эндпоинт для получения доступных книг."""
        books = Book.objects.available()
        serializer = self.get_serializer(books, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def with_status(self, request):
        """Декларативный эндпоинт для получения книг со статусом доступности."""
        books = get_books_with_availability_status()
        serializer = BookWithStatusSerializer(books, many=True)
        return Response(serializer.data)


class ReaderViewSet(viewsets.ModelViewSet):
    """
    Декларативный ViewSet для читателей.
    """
    queryset = Reader.objects.all()
    serializer_class = ReaderSerializer
    
    @action(detail=False, methods=['get'])
    def with_active_loans(self, request):
        """Декларативный эндпоинт для читателей с активными выдачами."""
        readers = get_readers_with_active_loans()
        serializer = self.get_serializer(readers, many=True)
        return Response(serializer.data)


class BookLoanViewSet(viewsets.ModelViewSet):
    """
    Декларативный ViewSet для выдачи книг.
    
    Использует разные сериализаторы для разных действий.
    """
    queryset = BookLoan.objects.select_related('book', 'reader').all()
    serializer_class = BookLoanSerializer
    
    def get_serializer_class(self):
        """
        Декларативный выбор сериализатора в зависимости от действия.
        """
        if self.action == 'create':
            return BookLoanCreateSerializer
        elif self.action == 'return_book':
            return BookLoanReturnSerializer
        return BookLoanSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Декларативное создание выдачи книги.
        
        Логика валидации описана в сериализаторе.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        loan = BookLoan.objects.select_related('book', 'reader').get(
            pk=serializer.instance.pk
        )
        output_serializer = BookLoanSerializer(loan)
        
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    def return_book(self, request, pk=None):
        """
        Декларативный эндпоинт для возврата книги.
        
        Использует специализированный сериализатор с валидацией.
        """
        loan = self.get_object()
        
        if loan.actual_return_date:
            return Response(
                {'error': 'Книга уже возвращена'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        data = request.data.copy()
        if 'actual_return_date' not in data:
            data['actual_return_date'] = timezone.now().date()
        
        serializer = self.get_serializer(loan, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        output_serializer = BookLoanSerializer(loan)
        return Response(output_serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Декларативный эндпоинт для активных выдач."""
        active_loans = self.queryset.filter(actual_return_date__isnull=True)
        serializer = self.get_serializer(active_loans, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Декларативный эндпоинт для просроченных выдач."""
        today = timezone.now().date()
        overdue_loans = self.queryset.filter(
            actual_return_date__isnull=True,
            planned_return_date__lt=today
        )
        serializer = self.get_serializer(overdue_loans, many=True)
        return Response(serializer.data)


class ReportViewSet(viewsets.ViewSet):
    """
    Декларативный ViewSet для отчетов.
    
    Использует функциональные преобразования данных.
    """
    
    @action(detail=False, methods=['get'])
    def library_statistics(self, request):
        """
        Декларативный эндпоинт для получения общей статистики библиотеки.
        
        Данные формируются через функциональные преобразования.
        """
        report_data = get_report_data()
        return Response(report_data)
