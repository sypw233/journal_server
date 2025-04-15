from django.urls import path
from . import views

urlpatterns = [
    path('journal-entries/', views.journal_entry_list, name='journal_entry_list'),
    path('journal-entries/<int:pk>/', views.journal_entry_detail, name='journal_entry_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
]