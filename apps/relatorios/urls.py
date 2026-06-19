from django.urls import path
from apps.relatorios.views import (
    RelatorioGeralSenhasView,
    RelatorioAtendimentosView,
    RelatorioColaboradoresView
)


urlpatterns = [
    path('geral/', RelatorioGeralSenhasView.as_view(), name='relatorio-geral-senhas'),
    path('atendimentos/', RelatorioAtendimentosView.as_view(), name='relatorio-atendimentos'),
    path('colaboradores/', RelatorioColaboradoresView.as_view(), name='relatorio-colaboradores'),
]


