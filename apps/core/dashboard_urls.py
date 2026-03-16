# ── core/dashboard_urls.py ───────────────────────────────────────────────────
"""
Single /dashboard/ URL that redirects each user type to their correct dashboard.
"""
from django.urls import path
from apps.core.views import dashboard_redirect

urlpatterns = [
    path('', dashboard_redirect),
]


# ── core/search_urls.py ───────────────────────────────────────────────────────
# (create as separate file below)
