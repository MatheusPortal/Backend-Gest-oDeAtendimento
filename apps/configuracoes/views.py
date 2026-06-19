from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.configuracoes.models import ConfiguracaoUnidade, PreferenciaFuncionario
from apps.configuracoes.serializers import (
    ConfiguracaoUnidadeSerializer,
    PreferenciaFuncionarioSerializer
)
from apps.unidades.models import UnidadeAtendimento
from apps.usuarios.permissions import PermissaoPorAcao
from apps.usuarios.services.permissoes import obter_funcionario_usuario


class ConfiguracaoUnidadeViewSet(viewsets.ModelViewSet):
    serializer_class = ConfiguracaoUnidadeSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'configuracao.visualizar',
        'retrieve': 'configuracao.visualizar',
        'create': 'configuracao.editar',
        'update': 'configuracao.editar',
        'partial_update': 'configuracao.editar',
        'destroy': 'configuracao.editar',
    }

    def get_queryset(self):
        queryset = ConfiguracaoUnidade.objects.select_related('unidade').all()

        unidade_id = self.request.query_params.get('unidade')
        ativo = self.request.query_params.get('ativo')

        if unidade_id:
            queryset = queryset.filter(unidade_id=unidade_id)

        if ativo == 'true':
            queryset = queryset.filter(ativo=True)

        if ativo == 'false':
            queryset = queryset.filter(ativo=False)

        return queryset.order_by('unidade__nome')

    def destroy(self, request, *args, **kwargs):
        configuracao = self.get_object()
        configuracao.ativo = False
        configuracao.save(update_fields=['ativo', 'atualizada_em'])

        return Response(
            {'detail': 'Configuração desativada com sucesso.'},
            status=status.HTTP_200_OK
        )


class MinhaPreferenciaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        funcionario = obter_funcionario_usuario(request.user)

        if not funcionario:
            raise PermissionDenied('Usuário não possui funcionário vinculado.')

        preferencia, created = PreferenciaFuncionario.objects.get_or_create(
            funcionario=funcionario
        )

        return Response(PreferenciaFuncionarioSerializer(preferencia).data)

    def patch(self, request):
        funcionario = obter_funcionario_usuario(request.user)

        if not funcionario:
            raise PermissionDenied('Usuário não possui funcionário vinculado.')

        preferencia, created = PreferenciaFuncionario.objects.get_or_create(
            funcionario=funcionario
        )

        serializer = PreferenciaFuncionarioSerializer(
            instance=preferencia,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class ConfiguracaoPainelPublicaView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        unidade_id = request.query_params.get('unidade')

        if not unidade_id:
            raise ValidationError({
                'unidade': 'Informe a unidade.'
            })

        try:
            unidade = UnidadeAtendimento.objects.get(id=unidade_id, ativa=True)
        except UnidadeAtendimento.DoesNotExist:
            return Response(
                {'detail': 'Unidade não encontrada ou inativa.'},
                status=status.HTTP_404_NOT_FOUND
            )

        configuracao, created = ConfiguracaoUnidade.objects.get_or_create(
            unidade=unidade,
            defaults={
                'ativo': True
            }
        )

        return Response({
            'unidade': {
                'id': unidade.id,
                'nome': unidade.nome,
                'codigo': unidade.codigo
            },
            'configuracao': ConfiguracaoUnidadeSerializer(configuracao).data
        })
    

