from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Author(models.Model):
    """Декларативное описание автора книги."""
    
    name = models.CharField(
        max_length=200,
        verbose_name="Имя автора",
        db_index=True
    )
    country = models.CharField(
        max_length=100,
        verbose_name="Страна",
        db_index=True
    )
    birth_date = models.DateField(
        verbose_name="Дата рождения",
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторы"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'country']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.country})"


class BookQuerySet(models.QuerySet):
    """Декларативные методы для выборки книг."""
    
    def available(self):
        """Книги, доступные для выдачи."""
        from django.db.models import Q, Count
        return self.annotate(
            active_loans=Count('bookloan', filter=Q(bookloan__actual_return_date__isnull=True))
        ).filter(active_loans=0)
    
    def on_loan(self):
        """Книги, находящиеся на руках у читателей."""
        from django.db.models import Q
        return self.filter(
            bookloan__actual_return_date__isnull=True
        ).distinct()
    
    def after_year(self, year):
        """Книги, изданные после указанного года."""
        return self.filter(publication_year__gt=year)
    
    def thick_books(self, min_pages=300):
        """Книги с количеством страниц больше указанного."""
        return self.filter(pages__gt=min_pages)


class BookManager(models.Manager):
    """Кастомный менеджер для декларативного доступа к книгам."""
    
    def get_queryset(self):
        return BookQuerySet(self.model, using=self._db)
    
    def available(self):
        return self.get_queryset().available()
    
    def on_loan(self):
        return self.get_queryset().on_loan()
    
    def after_year(self, year):
        return self.get_queryset().after_year(year)
    
    def thick_books(self, min_pages=300):
        return self.get_queryset().thick_books(min_pages)


class Book(models.Model):
    """Декларативное описание книги с бизнес-правилами на уровне БД."""
    
    GENRE_CHOICES = [
        ('fiction', 'Художественная литература'),
        ('non_fiction', 'Научная литература'),
        ('fantasy', 'Фэнтези'),
        ('sci_fi', 'Научная фантастика'),
        ('mystery', 'Детектив'),
        ('romance', 'Роман'),
        ('thriller', 'Триллер'),
        ('biography', 'Биография'),
        ('history', 'История'),
        ('other', 'Другое'),
    ]
    
    title = models.CharField(
        max_length=300,
        verbose_name="Название",
        db_index=True
    )
    isbn = models.CharField(
        max_length=13,
        unique=True,
        verbose_name="ISBN",
        db_index=True
    )
    publication_year = models.IntegerField(
        verbose_name="Год издания",
        validators=[
            MinValueValidator(1450),
            MaxValueValidator(2100)
        ],
        db_index=True
    )
    pages = models.IntegerField(
        verbose_name="Количество страниц",
        validators=[MinValueValidator(1)]
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
        verbose_name="Автор",
        related_name='books'
    )
    genre = models.CharField(
        max_length=20,
        choices=GENRE_CHOICES,
        verbose_name="Жанр",
        db_index=True
    )
    
    objects = BookManager()
    
    class Meta:
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        ordering = ['-publication_year', 'title']
        indexes = [
            models.Index(fields=['publication_year', 'pages']),
            models.Index(fields=['author', 'genre']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.publication_year})"


class Reader(models.Model):
    """Декларативное описание читателя библиотеки."""
    
    name = models.CharField(
        max_length=200,
        verbose_name="Имя читателя",
        db_index=True
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        db_index=True
    )
    registration_date = models.DateField(
        auto_now_add=True,
        verbose_name="Дата регистрации"
    )
    
    class Meta:
        verbose_name = "Читатель"
        verbose_name_plural = "Читатели"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.email})"


class BookLoan(models.Model):
    """Декларативное описание факта выдачи книги читателю."""
    
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        verbose_name="Книга",
        related_name='bookloan'
    )
    reader = models.ForeignKey(
        Reader,
        on_delete=models.CASCADE,
        verbose_name="Читатель",
        related_name='loans'
    )
    issue_date = models.DateField(
        auto_now_add=True,
        verbose_name="Дата выдачи",
        db_index=True
    )
    planned_return_date = models.DateField(
        verbose_name="Планируемая дата возврата",
        db_index=True
    )
    actual_return_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Фактическая дата возврата",
        db_index=True
    )
    
    class Meta:
        verbose_name = "Выдача книги"
        verbose_name_plural = "Выдачи книг"
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['book', 'actual_return_date']),
            models.Index(fields=['reader', 'actual_return_date']),
            models.Index(fields=['planned_return_date', 'actual_return_date']),
        ]
    
    def __str__(self):
        status = "возвращена" if self.actual_return_date else "на руках"
        return f"{self.book.title} → {self.reader.name} ({status})"
    
    @property
    def is_overdue(self):
        """Декларативное свойство для определения просроченности."""
        if self.actual_return_date:
            return False
        return timezone.now().date() > self.planned_return_date
    
    @property
    def is_active(self):
        """Декларативное свойство для проверки активности выдачи."""
        return self.actual_return_date is None
