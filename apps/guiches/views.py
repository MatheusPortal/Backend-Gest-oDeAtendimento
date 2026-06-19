from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.guiches.models import GuicheAtendimento
from apps.guiches.serializers import GuicheAtendimentoSerializer
from apps.usuarios.permissions import PermissaoPorAcao
from apps.usuarios.services.permissoes import obter_funcionario_usuario


class GuicheAtendimentoViewSet(viewsets.ModelViewSet):
    serializer_class = GuicheAtendimentoSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'guiche.visualizar',
        'retrieve': 'guiche.visualizar',
        'create': 'guiche.criar',
        'update': 'guiche.editar',
        'partial_update': 'guiche.editar',
        'destroy': 'guiche.excluir',
        'vincular_meu_guiche': 'guiche.vincular',
        'desvincular_meu_guiche': 'guiche.vincular',
        'alternar_disponibilidade': 'guiche.vincular',
    }

    def get_queryset(self):
        queryset = GuicheAtendimento.objects.select_related(
            'unidade',
            'funcionario_atual'
        ).all()

        unidade_id = self.request.query_params.get('unidade')
        ativo = self.request.query_params.get('ativo')
        disponivel = self.request.query_params.get('disponivel')
        pesquisar = self.request.query_params.get('pesquisar')

        if unidade_id:
            queryset = queryset.filter(unidade_id=unidade_id)

        if ativo == 'true':
            queryset = queryset.filter(ativo=True)

        if ativo == 'false':
            queryset = queryset.filter(ativo=False)

        if disponivel == 'true':
            queryset = queryset.filter(disponivel=True)

        if disponivel == 'false':
            queryset = queryset.filter(disponivel=False)

        if pesquisar:
            queryset = queryset.filter(
                Q(numero__icontains=pesquisar) |
                Q(nome__icontains=pesquisar) |
                Q(unidade__nome__icontains=pesquisar) |
                Q(funcionario_atual__nome__icontains=pesquisar)
            )

        return queryset.order_by('unidade__nome', 'numero')

    def destroy(self, request, *args, **kwargs):
        guiche = self.get_object()
        guiche.ativo = False
        guiche.disponivel = False
        guiche.funcionario_atual = None
        guiche.save(update_fields=[
            'ativo',
            'disponivel',
            'funcionario_atual',
            'atualizado_em'
        ])

        return Response(
            {'detail': 'Guichê desativado com sucesso.'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'], url_path='vincular-meu-guiche')
    def vincular_meu_guiche(self, request, pk=None):
        guiche = self.get_object()
        funcionario = obter_funcionario_usuario(request.user)

        if not funcionario:
            raise PermissionDenied('Usuário não possui funcionário vinculado.')

        if not funcionario.ativo:
            raise PermissionDenied('Funcionário inativo.')

        if funcionario.unidade_id != guiche.unidade_id:
            raise ValidationError({
                'guiche': 'Este guichê pertence a outra unidade.'
            })

        if not guiche.ativo:
            raise ValidationError({
                'guiche': 'Este guichê está inativo.'
            })

        if guiche.funcionario_atual and guiche.funcionario_atual != funcionario:
            raise ValidationError({
                'guiche': 'Este guichê já está vinculado a outro funcionário.'
            })

        GuicheAtendimento.objects.filter(
            funcionario_atual=funcionario
        ).exclude(
            id=guiche.id
        ).update(
            funcionario_atual=None,
            disponivel=True
        )

        guiche.funcionario_atual = funcionario
        guiche.disponivel = True
        guiche.save(update_fields=[
            'funcionario_atual',
            'disponivel',
            'atualizado_em'
        ])

        return Response(GuicheAtendimentoSerializer(guiche).data)

    @action(detail=True, methods=['post'], url_path='desvincular-meu-guiche')
    def desvincular_meu_guiche(self, request, pk=None):
        guiche = self.get_object()
        funcionario = obter_funcionario_usuario(request.user)

        if not funcionario:
            raise PermissionDenied('Usuário não possui funcionário vinculado.')

        if guiche.funcionario_atual != funcionario and not request.user.is_superuser:
            raise PermissionDenied('Este guichê não está vinculado a você.')

        guiche.funcionario_atual = None
        guiche.disponivel = True
        guiche.save(update_fields=[
            'funcionario_atual',
            'disponivel',
            'atualizado_em'
        ])

        return Response(GuicheAtendimentoSerializer(guiche).data)

    @action(detail=True, methods=['post'], url_path='alternar-disponibilidade')
    def alternar_disponibilidade(self, request, pk=None):
        guiche = self.get_object()
        funcionario = obter_funcionario_usuario(request.user)

        if not request.user.is_superuser:
            if not funcionario:
                raise PermissionDenied('Usuário não possui funcionário vinculado.')

            if guiche.funcionario_atual != funcionario:
                raise PermissionDenied('Este guichê não está vinculado a você.')

        guiche.disponivel = not guiche.disponivel
        guiche.save(update_fields=[
            'disponivel',
            'atualizado_em'
        ])

        return Response(GuicheAtendimentoSerializer(guiche).data)
    

