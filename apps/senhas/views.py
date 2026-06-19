from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.senhas.models import PrioridadeSenha, Senha
from apps.senhas.serializers import (
    PrioridadeSenhaSerializer,
    SenhaSerializer,
    GerarSenhaSerializer,
    PainelSenhaSerializer,
    HistoricoSenhaSerializer
)
from apps.categorias.models import CategoriaSenha
from apps.categorias.serializers import CategoriaSenhaSerializer
from apps.usuarios.permissions import PermissaoPorAcao

from apps.senhas.services.fila import (
    listar_fila,
    chamar_proxima_senha,
    obter_senha_atual
)

from apps.senhas.services.operacoes import (
    iniciar_atendimento_senha,
    pular_senha,
    retornar_senha_pulada,
    cancelar_senha,
    finalizar_senha_simples
)

from django.utils import timezone
from apps.unidades.models import UnidadeAtendimento

from rest_framework.exceptions import ValidationError
from apps.usuarios.models import Funcionario

from apps.senhas.services.redirecionamento import (
    listar_colaboradores_disponiveis,
    redirecionar_senha_para_colaborador,
    redirecionar_senha_para_fila
)

from apps.senhas.services.exclusoes import (
    excluir_todas_senhas_pendentes,
    excluir_senhas_por_categoria
)


class PrioridadeSenhaViewSet(viewsets.ModelViewSet):
    serializer_class = PrioridadeSenhaSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'prioridade.visualizar',
        'retrieve': 'prioridade.visualizar',
        'create': 'prioridade.criar',
        'update': 'prioridade.editar',
        'partial_update': 'prioridade.editar',
        'destroy': 'prioridade.excluir',
    }

    def get_queryset(self):
        queryset = PrioridadeSenha.objects.all()

        ativo = self.request.query_params.get('ativo')
        visivel_na_geracao = self.request.query_params.get('visivel_na_geracao')
        pesquisar = self.request.query_params.get('pesquisar')

        if ativo == 'true':
            queryset = queryset.filter(ativo=True)

        if ativo == 'false':
            queryset = queryset.filter(ativo=False)

        if visivel_na_geracao == 'true':
            queryset = queryset.filter(visivel_na_geracao=True)

        if visivel_na_geracao == 'false':
            queryset = queryset.filter(visivel_na_geracao=False)

        if pesquisar:
            queryset = queryset.filter(
                Q(nome__icontains=pesquisar) |
                Q(codigo__icontains=pesquisar)
            )

        return queryset.order_by('-peso', 'nome')

    def destroy(self, request, *args, **kwargs):
        prioridade = self.get_object()
        prioridade.ativo = False
        prioridade.save(update_fields=['ativo', 'atualizado_em'])

        return Response(
            {'detail': 'Prioridade de senha desativada com sucesso.'},
            status=status.HTTP_200_OK
        )


class SenhaViewSet(viewsets.ModelViewSet):
    serializer_class = SenhaSerializer

    permissoes_por_acao = {
        'list': 'senha.visualizar_fila',
        'retrieve': 'senha.visualizar_fila',
        'create': 'senha.visualizar_fila',
        'update': 'senha.visualizar_fila',
        'partial_update': 'senha.visualizar_fila',
        'destroy': 'senha.excluir_individual',

        'fila': 'senha.visualizar_fila',
        'senha_atual': 'senha.visualizar_fila',
        'chamar_proxima': 'senha.chamar',
        'historico': 'senha.visualizar_fila',

        'iniciar_atendimento': 'atendimento.iniciar',
        'pular': 'senha.pular',
        'retornar_pulada': 'senha.retornar_pulada',
        'cancelar': 'senha.cancelar',
        'finalizar_simples': 'atendimento.finalizar',
        'finalizar_atendimento': 'atendimento.finalizar',
        'colaboradores_disponiveis': 'senha.redirecionar_colaborador',
        'redirecionar_colaborador': 'senha.redirecionar_colaborador',
        'redirecionar_fila': 'senha.redirecionar_fila',
        'excluir_todas': 'senha.excluir_todas',
        'excluir_por_categoria': 'senha.excluir_por_categoria',

    }

    @action(detail=False, methods=['get'], url_path='colaboradores-disponiveis')
    def colaboradores_disponiveis(self, request):
        unidade_id = request.query_params.get('unidade')

        if not unidade_id:
            raise ValidationError({
                'unidade': 'Informe a unidade.'
            })

        try:
            unidade = UnidadeAtendimento.objects.get(id=unidade_id, ativa=True)
        except UnidadeAtendimento.DoesNotExist:
            raise ValidationError({
                'unidade': 'Unidade não encontrada ou inativa.'
            })

        colaboradores = listar_colaboradores_disponiveis(unidade)

        dados = []

        for colaborador in colaboradores:
            dados.append({
                'id': colaborador.id,
                'nome': colaborador.nome,
                'matricula': colaborador.matricula,
                'username': colaborador.user.username,
                'email': colaborador.user.email,
                'unidade': {
                    'id': colaborador.unidade.id,
                    'nome': colaborador.unidade.nome,
                    'codigo': colaborador.unidade.codigo
                } if colaborador.unidade else None
            })

        return Response({
            'unidade': {
                'id': unidade.id,
                'nome': unidade.nome,
                'codigo': unidade.codigo
            },
            'total': len(dados),
            'colaboradores': dados
        })


    @action(detail=True, methods=['post'], url_path='redirecionar-colaborador')
    def redirecionar_colaborador(self, request, pk=None):
        senha = self.get_object()

        colaborador_destino_id = request.data.get('colaborador_destino')
        motivo = request.data.get('motivo')

        if not colaborador_destino_id:
            raise ValidationError({
                'colaborador_destino': 'Informe o colaborador de destino.'
            })

        senha = redirecionar_senha_para_colaborador(
            user=request.user,
            senha=senha,
            colaborador_destino_id=colaborador_destino_id,
            motivo=motivo
        )

        return Response(SenhaSerializer(senha).data)


    @action(detail=True, methods=['post'], url_path='redirecionar-fila')
    def redirecionar_fila(self, request, pk=None):
        senha = self.get_object()

        motivo = request.data.get('motivo')

        senha = redirecionar_senha_para_fila(
            user=request.user,
            senha=senha,
            motivo=motivo
        )

        return Response(SenhaSerializer(senha).data)


    @action(detail=False, methods=['post'], url_path='excluir-todas')
    def excluir_todas(self, request):
        unidade_id = request.data.get('unidade') or request.query_params.get('unidade')

        total = excluir_todas_senhas_pendentes(unidade_id=unidade_id)

        return Response({
            'detail': 'Senhas pendentes canceladas com sucesso.',
            'total_canceladas': total
        })


    @action(detail=False, methods=['post'], url_path='excluir-por-categoria')
    def excluir_por_categoria(self, request):
        categoria_id = request.data.get('categoria') or request.query_params.get('categoria')
        unidade_id = request.data.get('unidade') or request.query_params.get('unidade')

        total = excluir_senhas_por_categoria(
            categoria_id=categoria_id,
            unidade_id=unidade_id
        )

        return Response({
            'detail': 'Senhas da categoria canceladas com sucesso.',
            'categoria': categoria_id,
            'total_canceladas': total
        })


    @action(detail=False, methods=['get'], url_path='historico')
    def historico(self, request):
        queryset = Senha.objects.select_related(
            'categoria',
            'prioridade',
            'unidade',
            'colaborador_chamou',
            'colaborador_finalizou'
        ).all()

        unidade_id = request.query_params.get('unidade')
        categoria_id = request.query_params.get('categoria')
        prioridade_id = request.query_params.get('prioridade')
        status_senha = request.query_params.get('status')
        humor = request.query_params.get('humor')
        cpf = request.query_params.get('cpf')
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        pesquisar = request.query_params.get('pesquisar')

        if unidade_id:
            queryset = queryset.filter(unidade_id=unidade_id)

        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        if prioridade_id:
            queryset = queryset.filter(prioridade_id=prioridade_id)

        if status_senha:
            queryset = queryset.filter(status=status_senha)

        if humor:
            queryset = queryset.filter(humor=humor)

        if cpf:
            queryset = queryset.filter(cpf__icontains=cpf)

        if data_inicio:
            queryset = queryset.filter(gerada_em__date__gte=data_inicio)

        if data_fim:
            queryset = queryset.filter(gerada_em__date__lte=data_fim)

        if pesquisar:
            queryset = queryset.filter(
                Q(codigo__icontains=pesquisar) |
                Q(cpf__icontains=pesquisar) |
                Q(categoria__nome__icontains=pesquisar) |
                Q(unidade__nome__icontains=pesquisar)
            )

        queryset = queryset.order_by('-gerada_em')

        serializer = HistoricoSenhaSerializer(queryset, many=True)

        return Response({
            'total': queryset.count(),
            'senhas': serializer.data
        })


    @action(detail=False, methods=['get'], url_path='painel')
    def painel(self, request):
        unidade_id = request.query_params.get('unidade')

        if not unidade_id:
            return Response(
                {'unidade': 'Informe a unidade.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            unidade = UnidadeAtendimento.objects.get(id=unidade_id, ativa=True)
        except UnidadeAtendimento.DoesNotExist:
            return Response(
                {'detail': 'Unidade não encontrada ou inativa.'},
                status=status.HTTP_404_NOT_FOUND
            )

        senha_atual = Senha.objects.select_related(
            'categoria',
            'prioridade',
            'unidade',
            'guiche'
        ).filter(
            unidade=unidade,
            status__in=[
                Senha.Status.CHAMADA,
                Senha.Status.EM_ATENDIMENTO
            ]
        ).order_by('-chamada_em').first()

        historico_chamadas = Senha.objects.select_related(
            'categoria',
            'prioridade',
            'unidade',
            'guiche'
        ).filter(
            unidade=unidade,
            chamada_em__isnull=False
        ).exclude(
            id=senha_atual.id if senha_atual else None
        ).order_by('-chamada_em')[:5]

        proximas_senhas = Senha.objects.select_related(
            'categoria',
            'prioridade',
            'unidade',
            'guiche'
        ).filter(
            unidade=unidade,
            status=Senha.Status.AGUARDANDO
        ).order_by(
            '-prioridade__peso',
            'gerada_em'
        )[:5]

        agora = timezone.localtime()

        return Response({
            'unidade': {
                'id': unidade.id,
                'nome': unidade.nome,
                'codigo': unidade.codigo
            },
            'horario_atual': agora.strftime('%H:%M:%S'),
            'data_atual': agora.strftime('%d/%m/%Y'),
            'senha_atual': PainelSenhaSerializer(senha_atual).data if senha_atual else None,
            'historico_chamadas': PainelSenhaSerializer(historico_chamadas, many=True).data,
            'proximas_senhas': PainelSenhaSerializer(proximas_senhas, many=True).data
        })

    
    @action(detail=True, methods=['post'], url_path='finalizar-atendimento')
    def finalizar_atendimento(self, request, pk=None):
        senha = self.get_object()

        serializer = FinalizarAtendimentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        atendimento = finalizar_atendimento_completo(
            user=request.user,
            senha=senha,
            dados=serializer.validated_data
        )

        return Response(
            AtendimentoSerializer(atendimento).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'], url_path='iniciar-atendimento')
    def iniciar_atendimento(self, request, pk=None):
        senha = iniciar_atendimento_senha(request.user, pk)

        return Response(
            SenhaSerializer(senha).data,
            status=status.HTTP_200_OK
        )


    @action(detail=True, methods=['post'], url_path='pular')
    def pular(self, request, pk=None):
        senha = pular_senha(request.user, pk)

        return Response(
            SenhaSerializer(senha).data,
            status=status.HTTP_200_OK
        )


    @action(detail=True, methods=['post'], url_path='retornar-pulada')
    def retornar_pulada(self, request, pk=None):
        senha = retornar_senha_pulada(request.user, pk)

        return Response(
            SenhaSerializer(senha).data,
            status=status.HTTP_200_OK
        )


    @action(detail=True, methods=['post'], url_path='cancelar')
    def cancelar(self, request, pk=None):
        senha = cancelar_senha(request.user, pk)

        return Response(
            SenhaSerializer(senha).data,
            status=status.HTTP_200_OK
        )


    @action(detail=True, methods=['post'], url_path='finalizar-simples')
    def finalizar_simples(self, request, pk=None):
        senha = finalizar_senha_simples(request.user, pk)

        return Response(
            SenhaSerializer(senha).data,
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], url_path='fila')
    def fila(self, request):
        unidade_id = request.query_params.get('unidade')

        unidade, funcionario = self._obter_contexto_para_view(request, unidade_id)

        queryset = listar_fila(unidade)

        serializer = SenhaSerializer(queryset, many=True)

        return Response({
            'unidade': {
                'id': unidade.id,
                'nome': unidade.nome,
                'codigo': unidade.codigo
            },
            'total': queryset.count(),
            'senhas': serializer.data
        })


    @action(detail=False, methods=['get'], url_path='senha-atual')
    def senha_atual(self, request):
        unidade_id = request.query_params.get('unidade')

        senha = obter_senha_atual(request.user, unidade_id)

        if not senha:
            return Response({
                'detail': 'Nenhuma senha atual encontrada.'
            })

        return Response(SenhaSerializer(senha).data)


    @action(detail=False, methods=['post'], url_path='chamar-proxima')
    def chamar_proxima(self, request):
        unidade_id = request.data.get('unidade') or request.query_params.get('unidade')
        guiche_id = request.data.get('guiche') or request.query_params.get('guiche')

        senha = chamar_proxima_senha(
            user=request.user,
            unidade_id=unidade_id,
            guiche_id=guiche_id
        )

        return Response(SenhaSerializer(senha).data)


    def _obter_contexto_para_view(self, request, unidade_id=None):
        from apps.senhas.services.fila import obter_contexto_operacao
        return obter_contexto_operacao(request.user, unidade_id)


    def get_permissions(self):
        if self.action in ['gerar', 'opcoes_geracao', 'painel']:
            return [AllowAny()]

        return [IsAuthenticated(), PermissaoPorAcao()]


    def get_queryset(self):
        queryset = Senha.objects.select_related(
            'categoria',
            'prioridade',
            'unidade',
            'colaborador_atual',
            'colaborador_chamou',
            'colaborador_finalizou'
        ).all()

        status_senha = self.request.query_params.get('status')
        unidade_id = self.request.query_params.get('unidade')
        categoria_id = self.request.query_params.get('categoria')
        prioridade_id = self.request.query_params.get('prioridade')
        cpf = self.request.query_params.get('cpf')
        pesquisar = self.request.query_params.get('pesquisar')

        if status_senha:
            queryset = queryset.filter(status=status_senha)

        if unidade_id:
            queryset = queryset.filter(unidade_id=unidade_id)

        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        if prioridade_id:
            queryset = queryset.filter(prioridade_id=prioridade_id)

        if cpf:
            queryset = queryset.filter(cpf__icontains=cpf)

        if pesquisar:
            queryset = queryset.filter(
                Q(codigo__icontains=pesquisar) |
                Q(cpf__icontains=pesquisar) |
                Q(categoria__nome__icontains=pesquisar) |
                Q(unidade__nome__icontains=pesquisar)
            )

        return queryset.order_by('-prioridade__peso', 'gerada_em')


    @action(detail=False, methods=['get'], url_path='opcoes-geracao')
    def opcoes_geracao(self, request):
        categorias = CategoriaSenha.objects.filter(ativa=True).order_by('nome')
        prioridades = PrioridadeSenha.objects.filter(
            ativo=True,
            visivel_na_geracao=True
        ).order_by('-peso', 'nome')

        return Response({
            'categorias': CategoriaSenhaSerializer(categorias, many=True).data,
            'prioridades': PrioridadeSenhaSerializer(prioridades, many=True).data,
            'humores': [
                {
                    'codigo': Senha.Humor.FELIZ,
                    'nome': 'Feliz',
                    'emoji': '😄'
                },
                {
                    'codigo': Senha.Humor.NEUTRO,
                    'nome': 'Neutro',
                    'emoji': '😐'
                },
                {
                    'codigo': Senha.Humor.TRISTE,
                    'nome': 'Triste',
                    'emoji': '😟'
                }
            ]
        })


    @action(detail=False, methods=['post'], url_path='gerar')
    def gerar(self, request):
        serializer = GerarSenhaSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        senha = serializer.save()

        return Response(
            SenhaSerializer(senha).data,
            status=status.HTTP_201_CREATED
        )


    def destroy(self, request, *args, **kwargs):
        senha = self.get_object()
        senha.status = Senha.Status.CANCELADA
        senha.save(update_fields=['status', 'atualizada_em'])

        return Response(
            {'detail': 'Senha cancelada com sucesso.'},
            status=status.HTTP_200_OK
        )
    



