from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.unidades.models import UnidadeAtendimento
from apps.unidades.serializers import UnidadeAtendimentoSerializer
from apps.usuarios.permissions import PermissaoPorAcao


class UnidadeAtendimentoViewSet(viewsets.ModelViewSet):
    serializer_class = UnidadeAtendimentoSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'unidade.visualizar',
        'retrieve': 'unidade.visualizar',
        'create': 'unidade.criar',
        'update': 'unidade.editar',
        'partial_update': 'unidade.editar',
        'destroy': 'unidade.excluir',
    }

    def get_queryset(self):
        queryset = UnidadeAtendimento.objects.all()

        ativa = self.request.query_params.get('ativa')
        pesquisar = self.request.query_params.get('pesquisar')

        if ativa == 'true':
            queryset = queryset.filter(ativa=True)

        if ativa == 'false':
            queryset = queryset.filter(ativa=False)

        if pesquisar:
            queryset = queryset.filter(nome__icontains=pesquisar) | queryset.filter(codigo__icontains=pesquisar)

        return queryset.order_by('nome')

    def destroy(self, request, *args, **kwargs):
        unidade = self.get_object()
        unidade.ativa = False
        unidade.save(update_fields=['ativa', 'atualizada_em'])

        return Response(
            {'detail': 'Unidade de atendimento desativada com sucesso.'},
            status=status.HTTP_200_OK
        )