from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.usuarios.models import Funcionario
from apps.usuarios.serializers import (
    UsuarioLogadoSerializer,
    FuncionarioSerializer,
    FuncionarioInputSerializer,
    PerfilAcessoSerializer,
    PermissaoSistemaSerializer,
    AtualizarPermissoesFuncionarioSerializer
)

from apps.usuarios.permissions import PermissaoPorAcao

from django.db import transaction
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied

from apps.usuarios.models import (
    PerfilAcesso,
    PermissaoSistema,
    PerfilPermissao,
    FuncionarioPermissao
)
from apps.usuarios.services.permissoes import (
    obter_permissoes_usuario,
    usuario_tem_permissao
)


class UsuarioLogadoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioLogadoSerializer({
            'id': request.user.id,
            'username': request.user.username,
            'email': request.user.email,
            'is_superuser': request.user.is_superuser,
            'acesso_total': request.user.is_superuser,
            'funcionario': request.user,
            'permissoes': request.user
        })

        return Response(serializer.data)


class FuncionarioViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'colaborador.visualizar',
        'retrieve': 'colaborador.visualizar',
        'create': 'colaborador.criar',
        'update': 'colaborador.editar',
        'partial_update': 'colaborador.editar',
        'destroy': 'colaborador.excluir',
        'permissoes': 'permissao.visualizar',
    }

    @action(detail=True, methods=['get', 'put', 'patch'], url_path='permissoes')
    def permissoes(self, request, pk=None):
        funcionario = self.get_object()

        if request.method == 'GET':
            return Response(self._montar_permissoes_funcionario(funcionario))

        if not self._usuario_pode_alterar_permissoes(request.user, funcionario):
            raise PermissionDenied('Você não tem permissão para alterar permissões deste funcionário.')

        serializer = AtualizarPermissoesFuncionarioSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            for item in serializer.validated_data['permissoes']:
                FuncionarioPermissao.objects.update_or_create(
                    funcionario=funcionario,
                    permissao=item['permissao'],
                    defaults={
                        'permitido': item['permitido']
                    }
                )

        return Response(self._montar_permissoes_funcionario(funcionario))


    def _usuario_pode_alterar_permissoes(self, user, funcionario_alvo):
        if user.is_superuser:
            return True

        if funcionario_alvo.perfil.nome == PerfilAcesso.Perfis.SUPERVISOR:
            return usuario_tem_permissao(user, 'permissao.atribuir_supervisor')

        if funcionario_alvo.perfil.nome == PerfilAcesso.Perfis.COLABORADOR:
            return usuario_tem_permissao(user, 'permissao.atribuir_colaborador')

        return False


    def _montar_permissoes_funcionario(self, funcionario):
        permissoes_perfil = set(
            PerfilPermissao.objects.filter(
                perfil=funcionario.perfil,
                permissao__ativa=True
            ).values_list('permissao_id', flat=True)
        )

        permissoes_individuais = {
            item.permissao_id: item
            for item in FuncionarioPermissao.objects.filter(
                funcionario=funcionario,
                permissao__ativa=True
            ).select_related('permissao')
        }

        permissoes = []

        for permissao in PermissaoSistema.objects.filter(ativa=True).order_by('modulo', 'codigo'):
            individual = permissoes_individuais.get(permissao.id)

            vem_do_perfil = permissao.id in permissoes_perfil

            if individual:
                permitido = individual.permitido
                origem = 'individual'
            elif vem_do_perfil:
                permitido = True
                origem = 'perfil'
            else:
                permitido = False
                origem = 'nenhuma'

            permissoes.append({
                'id': permissao.id,
                'codigo': permissao.codigo,
                'nome': permissao.nome,
                'descricao': permissao.descricao,
                'modulo': permissao.modulo,
                'modulo_nome': permissao.get_modulo_display(),
                'permitido': permitido,
                'origem': origem,
                'vem_do_perfil': vem_do_perfil,
                'configuracao_individual': {
                    'id': individual.id,
                    'permitido': individual.permitido
                } if individual else None
            })

        return {
            'funcionario': {
                'id': funcionario.id,
                'nome': funcionario.nome,
                'matricula': funcionario.matricula,
                'perfil': funcionario.perfil.nome,
                'perfil_nome': funcionario.perfil.get_nome_display(),
                'unidade': funcionario.unidade.nome if funcionario.unidade else None,
                'ativo': funcionario.ativo
            },
            'permissoes_efetivas': obter_permissoes_usuario(funcionario.user),
            'permissoes': permissoes
        }


    def get_queryset(self):
        queryset = Funcionario.objects.select_related(
            'user',
            'perfil',
            'unidade'
        ).all()

        ativo = self.request.query_params.get('ativo')
        perfil = self.request.query_params.get('perfil')
        unidade = self.request.query_params.get('unidade')
        pesquisar = self.request.query_params.get('pesquisar')

        if ativo == 'true':
            queryset = queryset.filter(ativo=True)

        if ativo == 'false':
            queryset = queryset.filter(ativo=False)

        if perfil:
            queryset = queryset.filter(perfil__nome=perfil)

        if unidade:
            queryset = queryset.filter(unidade_id=unidade)

        if pesquisar:
            queryset = queryset.filter(
                Q(nome__icontains=pesquisar) |
                Q(matricula__icontains=pesquisar) |
                Q(user__username__icontains=pesquisar) |
                Q(user__email__icontains=pesquisar)
            )

        return queryset.order_by('nome')


    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return FuncionarioInputSerializer

        return FuncionarioSerializer


    def create(self, request, *args, **kwargs):
        serializer = FuncionarioInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        funcionario = serializer.save()

        return Response(
            FuncionarioSerializer(funcionario).data,
            status=status.HTTP_201_CREATED
        )


    def update(self, request, *args, **kwargs):
        funcionario = self.get_object()

        serializer = FuncionarioInputSerializer(
            instance=funcionario,
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        funcionario = serializer.save()

        return Response(FuncionarioSerializer(funcionario).data)


    def partial_update(self, request, *args, **kwargs):
        funcionario = self.get_object()

        serializer = FuncionarioInputSerializer(
            instance=funcionario,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)

        funcionario = serializer.save()

        return Response(FuncionarioSerializer(funcionario).data)


    def destroy(self, request, *args, **kwargs):
        funcionario = self.get_object()

        funcionario.ativo = False
        funcionario.save(update_fields=['ativo', 'atualizado_em'])

        funcionario.user.is_active = False
        funcionario.user.save(update_fields=['is_active'])

        return Response(
            {'detail': 'Funcionário desativado com sucesso.'},
            status=status.HTTP_200_OK
        )

  
class PerfilAcessoViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PerfilAcessoSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'permissao.visualizar',
        'retrieve': 'permissao.visualizar',
    }

    def get_queryset(self):
        return PerfilAcesso.objects.filter(ativo=True).order_by('nome')



class PermissaoSistemaViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PermissaoSistemaSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'permissao.visualizar',
        'retrieve': 'permissao.visualizar',
    }

    def get_queryset(self):
        queryset = PermissaoSistema.objects.filter(ativa=True)

        modulo = self.request.query_params.get('modulo')
        pesquisar = self.request.query_params.get('pesquisar')

        if modulo:
            queryset = queryset.filter(modulo=modulo)

        if pesquisar:
            queryset = queryset.filter(
                Q(codigo__icontains=pesquisar) |
                Q(nome__icontains=pesquisar) |
                Q(descricao__icontains=pesquisar)
            )

        return queryset.order_by('modulo', 'codigo')


