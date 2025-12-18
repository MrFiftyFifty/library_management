from django.urls import path, include
from rest_framework.routers import DefaultRouter
from books.views import (
    AuthorViewSet,
    BookViewSet,
    ReaderViewSet,
    BookLoanViewSet,
    ReportViewSet
)

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')
router.register(r'readers', ReaderViewSet, basename='reader')
router.register(r'loans', BookLoanViewSet, basename='loan')
router.register(r'reports', ReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]
