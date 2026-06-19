from rest_framework.permissions import BasePermission
from apps.usuarios.services.permissoes import usuario_tem_permissao


class PermissaoPorAcao(BasePermission):
    message = 'Você não tem permissão para executar esta ação.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        permissoes_por_acao = getattr(view, 'permissoes_por_acao', {})
        acao = getattr(view, 'action', None)

        codigo_permissao = permissoes_por_acao.get(acao)

        if not codigo_permissao:
            return False

        return usuario_tem_permissao(request.user, codigo_permissao)