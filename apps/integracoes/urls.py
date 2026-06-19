from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.integracoes.views import (
    IntegracaoHubspotViewSet,
    HubspotTicketConfigViewSet,
    HubspotCampoMapeadoViewSet,
    HubspotTicketLogViewSet,
    HubspotOpcoesFinalizacaoView
)


router = DefaultRouter()
router.register(r'hubspot', IntegracaoHubspotViewSet, basename='integracoes-hubspot')
router.register(r'hubspot-ticket-configs', HubspotTicketConfigViewSet, basename='hubspot-ticket-configs')
router.register(r'hubspot-campos', HubspotCampoMapeadoViewSet, basename='hubspot-campos')
router.register(r'hubspot-logs', HubspotTicketLogViewSet, basename='hubspot-logs')


urlpatterns = [
    path('', include(router.urls)),
    path('hubspot-opcoes-finalizacao/', HubspotOpcoesFinalizacaoView.as_view(), name='hubspot-opcoes-finalizacao'),
]

