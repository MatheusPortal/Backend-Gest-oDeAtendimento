from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.configuracoes.views import (
    ConfiguracaoUnidadeViewSet,
    MinhaPreferenciaView,
    ConfiguracaoPainelPublicaView
)


router = DefaultRouter()
router.register(r'unidades', ConfiguracaoUnidadeViewSet, basename='configuracoes-unidades')


urlpatterns = [
    path('', include(router.urls)),
    path('minhas-preferencias/', MinhaPreferenciaView.as_view(), name='minhas-preferencias'),
    path('painel/', ConfiguracaoPainelPublicaView.as_view(), name='configuracao-painel-publica'),
]
