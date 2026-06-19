from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.guiches.views import GuicheAtendimentoViewSet


router = DefaultRouter()
router.register(r'guiches', GuicheAtendimentoViewSet, basename='guiches')


urlpatterns = [
    path('', include(router.urls)),
]