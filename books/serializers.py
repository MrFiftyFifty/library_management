from rest_framework import serializers
from django.utils import timezone
from books.models import Book, Author, Reader, BookLoan


class AuthorSerializer(serializers.ModelSerializer):
    """Декларативный сериализатор для автора."""
    
    books_count = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Author
        fields = ['id', 'name', 'country', 'birth_date', 'books_count']
        read_only_fields = ['id']


class BookSerializer(serializers.ModelSerializer):
    """Декларативный сериализатор для книги."""
    
    author_name = serializers.CharField(source='author.name', read_only=True)
    genre_display = serializers.CharField(source='get_genre_display', read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'isbn', 'publication_year', 'pages',
            'author', 'author_name', 'genre', 'genre_display'
        ]
        read_only_fields = ['id']


class ReaderSerializer(serializers.ModelSerializer):
    """Декларативный сериализатор для читателя."""
    
    active_loans_count = serializers.IntegerField(read_only=True, required=False)
    
    class Meta:
        model = Reader
        fields = ['id', 'name', 'email', 'registration_date', 'active_loans_count']
        read_only_fields = ['id', 'registration_date']


class BookLoanSerializer(serializers.ModelSerializer):
    """
    Декларативный сериализатор для выдачи книги с валидацией.
    
    Включает декларативные поля из связанных моделей и бизнес-правила.
    """
    
    book_title = serializers.CharField(source='book.title', read_only=True)
    book_isbn = serializers.CharField(source='book.isbn', read_only=True)
    reader_name = serializers.CharField(source='reader.name', read_only=True)
    reader_email = serializers.CharField(source='reader.email', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BookLoan
        fields = [
            'id', 'book', 'book_title', 'book_isbn',
            'reader', 'reader_name', 'reader_email',
            'issue_date', 'planned_return_date', 'actual_return_date',
            'is_overdue', 'is_active'
        ]
        read_only_fields = ['id', 'issue_date']
    
    def validate_book(self, value):
        """
        Декларативная валидация: проверка, что книга не выдана другому читателю.
        """
        if self.instance is None:
            active_loan = BookLoan.objects.filter(
                book=value,
                actual_return_date__isnull=True
            ).exists()
            
            if active_loan:
                raise serializers.ValidationError(
                    "Эта книга уже выдана другому читателю и не может быть выдана повторно."
                )
        
        return value
    
    def validate_planned_return_date(self, value):
        """Декларативная валидация: дата возврата не может быть в прошлом."""
        if value < timezone.now().date():
            raise serializers.ValidationError(
                "Планируемая дата возврата не может быть в прошлом."
            )
        return value
    
    def validate(self, attrs):
        """
        Общая валидация на уровне объекта.
        
        Декларативно описываем бизнес-правила для всего объекта.
        """
        if self.instance is None:
            issue_date = timezone.now().date()
            planned_return_date = attrs.get('planned_return_date')
            
            if planned_return_date and planned_return_date <= issue_date:
                raise serializers.ValidationError(
                    "Планируемая дата возврата должна быть позже даты выдачи."
                )
        
        if 'actual_return_date' in attrs and attrs['actual_return_date']:
            if attrs['actual_return_date'] > timezone.now().date():
                raise serializers.ValidationError(
                    "Фактическая дата возврата не может быть в будущем."
                )
        
        return attrs


class BookLoanCreateSerializer(serializers.ModelSerializer):
    """Специализированный сериализатор для создания выдачи книги."""
    
    class Meta:
        model = BookLoan
        fields = ['book', 'reader', 'planned_return_date']
    
    def validate_book(self, value):
        """Декларативная проверка доступности книги."""
        active_loan = BookLoan.objects.filter(
            book=value,
            actual_return_date__isnull=True
        ).exists()
        
        if active_loan:
            raise serializers.ValidationError(
                f"Книга '{value.title}' уже выдана и недоступна."
            )
        
        return value
    
    def validate_planned_return_date(self, value):
        """Декларативная валидация даты возврата."""
        today = timezone.now().date()
        
        if value <= today:
            raise serializers.ValidationError(
                "Планируемая дата возврата должна быть позже сегодняшнего дня."
            )
        
        if value > today + timezone.timedelta(days=90):
            raise serializers.ValidationError(
                "Книгу нельзя выдать более чем на 90 дней."
            )
        
        return value


class BookLoanReturnSerializer(serializers.ModelSerializer):
    """Специализированный сериализатор для возврата книги."""
    
    class Meta:
        model = BookLoan
        fields = ['actual_return_date']
    
    def validate_actual_return_date(self, value):
        """Декларативная валидация даты возврата."""
        if value > timezone.now().date():
            raise serializers.ValidationError(
                "Дата возврата не может быть в будущем."
            )
        
        if self.instance and value < self.instance.issue_date:
            raise serializers.ValidationError(
                "Дата возврата не может быть раньше даты выдачи."
            )
        
        return value
    
    def validate(self, attrs):
        """Проверка, что книга еще не возвращена."""
        if self.instance and self.instance.actual_return_date:
            raise serializers.ValidationError(
                "Эта книга уже возвращена."
            )
        
        return attrs


class BookWithStatusSerializer(serializers.ModelSerializer):
    """Сериализатор книги со статусом доступности."""
    
    author_name = serializers.CharField(source='author.name', read_only=True)
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author_name', 'status']
