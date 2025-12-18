from django.contrib import admin
from books.models import Author, Book, Reader, BookLoan


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'country', 'birth_date']
    list_filter = ['country']
    search_fields = ['name', 'country']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'isbn', 'publication_year', 'pages', 'genre']
    list_filter = ['genre', 'publication_year', 'author']
    search_fields = ['title', 'isbn', 'author__name']
    list_select_related = ['author']


@admin.register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'registration_date']
    search_fields = ['name', 'email']
    list_filter = ['registration_date']


@admin.register(BookLoan)
class BookLoanAdmin(admin.ModelAdmin):
    list_display = [
        'book', 'reader', 'issue_date',
        'planned_return_date', 'actual_return_date', 'is_overdue'
    ]
    list_filter = ['issue_date', 'planned_return_date', 'actual_return_date']
    search_fields = ['book__title', 'reader__name']
    list_select_related = ['book', 'reader']
    readonly_fields = ['issue_date', 'is_overdue', 'is_active']
    
    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Просрочена'
