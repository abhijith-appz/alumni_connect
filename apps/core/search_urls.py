# apps/core/search_urls.py
from django.urls import path
from apps.accounts.views import quick_search

urlpatterns = [
    path('', quick_search, name='quick_search'),
]
