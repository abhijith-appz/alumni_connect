# ── alumni/api_urls.py ────────────────────────────────────────────────────────
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import AlumniProfileViewSet

router = DefaultRouter()
router.register(r'profiles', AlumniProfileViewSet, basename='alumni-profile')

urlpatterns = [path('', include(router.urls))]


# ── jobs/api_urls.py ──────────────────────────────────────────────────────────
# (inline for brevity — stored as separate file)
