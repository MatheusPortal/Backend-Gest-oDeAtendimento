from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.integracoes.models import (
    IntegracaoHubspot,
    HubspotTicketConfig,
    HubspotCampoMapeado,
    HubspotTicketLog
)
from apps.integracoes.serializers import (
    IntegracaoHubspotSerializer,
    HubspotTicketConfigSerializer,
    HubspotCampoMapeadoSerializer,
    HubspotTicketLogSerializer
)
from apps.usuarios.permissions import PermissaoPorAcao
from rest_framework.views import APIView


class IntegracaoHubspotViewSet(viewsets.ModelViewSet):
    serializer_class = IntegracaoHubspotSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'integracao.visualizar',
        'retrieve': 'integracao.visualizar',
        'create': 'integracao.criar',
        'update': 'integracao.editar',
        'partial_update': 'integracao.editar',
        'destroy': 'integracao.excluir',
    }

    def get_queryset(self):
        queryset = IntegracaoHubspot.objects.all()

        ativa = self.request.query_params.get('ativa')
        pesquisar = self.request.query_params.get('pesquisar')

        if ativa == 'true':
            queryset = queryset.filter(ativa=True)

        if ativa == 'false':
            queryset = queryset.filter(ativa=False)

        if pesquisar:
            queryset = queryset.filter(
                Q(nome__icontains=pesquisar) |
                Q(identificador__icontains=pesquisar)
            )

        return queryset.order_by('nome')

    def destroy(self, request, *args, **kwargs):
        integracao = self.get_object()
        integracao.ativa = False
        integracao.save(update_fields=['ativa', 'atualizada_em'])

        return Response(
            {'detail': 'Integração HubSpot desativada com sucesso.'},
            status=status.HTTP_200_OK
        )


class HubspotTicketConfigViewSet(viewsets.ModelViewSet):
    serializer_class = HubspotTicketConfigSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'integracao.visualizar',
        'retrieve': 'integracao.visualizar',
        'create': 'integracao.criar',
        'update': 'integracao.editar',
        'partial_update': 'integracao.editar',
        'destroy': 'integracao.excluir',
    }

    def get_queryset(self):
        queryset = HubspotTicketConfig.objects.select_related(
            'integracao'
        ).prefetch_related(
            'campos_mapeados'
        ).all()

        integracao_id = self.request.query_params.get('integracao')
        tipo = self.request.query_params.get('tipo')
        ativo = self.request.query_params.get('ativo')
        pesquisar = self.request.query_params.get('pesquisar')

        if integracao_id:
            queryset = queryset.filter(integracao_id=integracao_id)

        if tipo:
            queryset = queryset.filter(tipo=tipo)

        if ativo == 'true':
            queryset = queryset.filter(ativo=True)

        if ativo == 'false':
            queryset = queryset.filter(ativo=False)

        if pesquisar:
            queryset = queryset.filter(
                Q(nome__icontains=pesquisar) |
                Q(pipeline_id__icontains=pesquisar) |
                Q(pipeline_nome__icontains=pesquisar) |
                Q(stage_id__icontains=pesquisar) |
                Q(stage_nome__icontains=pesquisar)
            )

        return queryset.order_by('tipo', 'ordem', 'nome')

    def destroy(self, request, *args, **kwargs):
        config = self.get_object()
        config.ativo = False
        config.save(update_fields=['ativo', 'atualizada_em'])

        return Response(
            {'detail': 'Configuração de ticket desativada com sucesso.'},
            status=status.HTTP_200_OK
        )


class HubspotCampoMapeadoViewSet(viewsets.ModelViewSet):
    serializer_class = HubspotCampoMapeadoSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'integracao.visualizar',
        'retrieve': 'integracao.visualizar',
        'create': 'integracao.editar',
        'update': 'integracao.editar',
        'partial_update': 'integracao.editar',
        'destroy': 'integracao.editar',
    }

    def get_queryset(self):
        queryset = HubspotCampoMapeado.objects.select_related(
            'config_ticket',
            'config_ticket__integracao'
        ).all()

        config_ticket_id = self.request.query_params.get('config_ticket')
        ativo = self.request.query_params.get('ativo')
        origem = self.request.query_params.get('origem')
        pesquisar = self.request.query_params.get('pesquisar')

        if config_ticket_id:
            queryset = queryset.filter(config_ticket_id=config_ticket_id)

        if ativo == 'true':
            queryset = queryset.filter(ativo=True)

        if ativo == 'false':
            queryset = queryset.filter(ativo=False)

        if origem:
            queryset = queryset.filter(origem=origem)

        if pesquisar:
            queryset = queryset.filter(
                Q(propriedade_hubspot__icontains=pesquisar) |
                Q(nome_exibicao__icontains=pesquisar) |
                Q(campo_sistema__icontains=pesquisar) |
                Q(chave_front__icontains=pesquisar)
            )

        return queryset.order_by('config_ticket', 'ordem', 'propriedade_hubspot')

    def destroy(self, request, *args, **kwargs):
        campo = self.get_object()
        campo.ativo = False
        campo.save(update_fields=['ativo', 'atualizada_em'])

        return Response(
            {'detail': 'Campo mapeado desativado com sucesso.'},
            status=status.HTTP_200_OK
        )


class HubspotTicketLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = HubspotTicketLogSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'integracao.visualizar',
        'retrieve': 'integracao.visualizar',
    }

    def get_queryset(self):
        queryset = HubspotTicketLog.objects.select_related(
            'atendimento',
            'integracao',
            'config_ticket'
        ).all()

        atendimento_id = self.request.query_params.get('atendimento')
        integracao_id = self.request.query_params.get('integracao')
        config_ticket_id = self.request.query_params.get('config_ticket')
        tipo = self.request.query_params.get('tipo')
        status_envio = self.request.query_params.get('status')
        data_inicio = self.request.query_params.get('data_inicio')
        data_fim = self.request.query_params.get('data_fim')
        pesquisar = self.request.query_params.get('pesquisar')

        if atendimento_id:
            queryset = queryset.filter(atendimento_id=atendimento_id)

        if integracao_id:
            queryset = queryset.filter(integracao_id=integracao_id)

        if config_ticket_id:
            queryset = queryset.filter(config_ticket_id=config_ticket_id)

        if tipo:
            queryset = queryset.filter(tipo=tipo)

        if status_envio:
            queryset = queryset.filter(status=status_envio)

        if data_inicio:
            queryset = queryset.filter(criado_em__date__gte=data_inicio)

        if data_fim:
            queryset = queryset.filter(criado_em__date__lte=data_fim)

        if pesquisar:
            queryset = queryset.filter(
                Q(hubspot_ticket_id__icontains=pesquisar) |
                Q(erro__icontains=pesquisar) |
                Q(atendimento__titulo__icontains=pesquisar) |
                Q(atendimento__matricula__icontains=pesquisar) |
                Q(atendimento__cpf__icontains=pesquisar)
            )

        return queryset.order_by('-criado_em')
    

class HubspotOpcoesFinalizacaoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        configs_registro = HubspotTicketConfig.objects.select_related(
            'integracao'
        ).filter(
            integracao__ativa=True,
            ativo=True,
            tipo=HubspotTicketConfig.TipoTicket.REGISTRO_ATENDIMENTO,
            criar_automaticamente=True
        )

        configs_chamado = HubspotTicketConfig.objects.select_related(
            'integracao'
        ).prefetch_related(
            'campos_mapeados'
        ).filter(
            integracao__ativa=True,
            ativo=True,
            tipo=HubspotTicketConfig.TipoTicket.CHAMADO_INTERNO,
            permitir_manual=True
        ).order_by(
            'ordem',
            'nome'
        )

        chamados = []

        for config in configs_chamado:
            campos_front = []

            for campo in config.campos_mapeados.filter(
                ativo=True,
                origem=HubspotCampoMapeado.OrigemValor.CAMPO_FRONT
            ).order_by('ordem', 'nome_exibicao'):
                campos_front.append({
                    'id': campo.id,
                    'propriedade_hubspot': campo.propriedade_hubspot,
                    'nome_exibicao': campo.nome_exibicao or campo.propriedade_hubspot,
                    'chave_front': campo.chave_front,
                    'obrigatorio': campo.obrigatorio,
                    'ordem': campo.ordem
                })

            chamados.append({
                'id': config.id,
                'nome': config.nome,
                'tipo': config.tipo,
                'tipo_nome': config.get_tipo_display(),
                'pipeline_id': config.pipeline_id,
                'pipeline_nome': config.pipeline_nome,
                'stage_id': config.stage_id,
                'stage_nome': config.stage_nome,
                'campos_front': campos_front
            })

        return Response({
            'registro_automatico_ativo': configs_registro.exists(),
            'total_configs_registro_automatico': configs_registro.count(),
            'chamado_interno_disponivel': len(chamados) > 0,
            'configs_chamado_interno': chamados
        })
    
    

