from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.usuarios.views import (
    UsuarioLogadoView,
    FuncionarioViewSet,
    PerfilAcessoViewSet,
    PermissaoSistemaViewSet
)


router = DefaultRouter()
router.register(r'funcionarios', FuncionarioViewSet, basename='funcionarios')
router.register(r'perfis', PerfilAcessoViewSet, basename='perfis')
router.register(r'permissoes', PermissaoSistemaViewSet, basename='permissoes')


urlpatterns = [
    path('me/', UsuarioLogadoView.as_view(), name='usuario-logado'),
    path('', include(router.urls)),
]