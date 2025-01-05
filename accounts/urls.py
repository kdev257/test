from django.urls import path
from . import views

urlpatterns = [
    path('journal_entry/', views.create_journal_entry, name='journal_entry'),
]
