from rest_framework import serializers

from apps.integracoes.models import (
    IntegracaoHubspot,
    HubspotTicketConfig,
    HubspotCampoMapeado,
    HubspotTicketLog
)


class IntegracaoHubspotSerializer(serializers.ModelSerializer):
    token_acesso = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        allow_null=True
    )
    token_cadastrado = serializers.BooleanField(read_only=True)

    class Meta:
        model = IntegracaoHubspot
        fields = [
            'id',
            'nome',
            'identificador',
            'base_url',
            'token_acesso',
            'token_cadastrado',
            'ativa',
            'criada_em',
            'atualizada_em'
        ]
        read_only_fields = [
            'id',
            'token_cadastrado',
            'criada_em',
            'atualizada_em'
        ]

    def update(self, instance, validated_data):
        if 'token_acesso' in validated_data and not validated_data.get('token_acesso'):
            validated_data.pop('token_acesso')

        return super().update(instance, validated_data)


class HubspotCampoMapeadoSerializer(serializers.ModelSerializer):
    origem_nome = serializers.CharField(source='get_origem_display', read_only=True)
    campo_sistema_nome = serializers.CharField(source='get_campo_sistema_display', read_only=True)

    class Meta:
        model = HubspotCampoMapeado
        fields = [
            'id',
            'config_ticket',
            'propriedade_hubspot',
            'nome_exibicao',
            'origem',
            'origem_nome',
            'campo_sistema',
            'campo_sistema_nome',
            'chave_front',
            'valor_fixo',
            'obrigatorio',
            'ativo',
            'ordem',
            'criada_em',
            'atualizada_em'
        ]
        read_only_fields = [
            'id',
            'origem_nome',
            'campo_sistema_nome',
            'criada_em',
            'atualizada_em'
        ]


class HubspotTicketConfigSerializer(serializers.ModelSerializer):
    integracao_nome = serializers.CharField(source='integracao.nome', read_only=True)
    tipo_nome = serializers.CharField(source='get_tipo_display', read_only=True)
    campos_mapeados = HubspotCampoMapeadoSerializer(many=True, read_only=True)

    class Meta:
        model = HubspotTicketConfig
        fields = [
            'id',
            'integracao',
            'integracao_nome',
            'nome',
            'tipo',
            'tipo_nome',
            'pipeline_id',
            'pipeline_nome',
            'stage_id',
            'stage_nome',
            'criar_automaticamente',
            'permitir_manual',
            'ativo',
            'ordem',
            'campos_mapeados',
            'criada_em',
            'atualizada_em'
        ]
        read_only_fields = [
            'id',
            'integracao_nome',
            'tipo_nome',
            'campos_mapeados',
            'criada_em',
            'atualizada_em'
        ]


class HubspotTicketLogSerializer(serializers.ModelSerializer):
    atendimento_titulo = serializers.CharField(source='atendimento.titulo', read_only=True)
    atendimento_matricula = serializers.CharField(source='atendimento.matricula', read_only=True)
    integracao_nome = serializers.CharField(source='integracao.nome', read_only=True)
    config_ticket_nome = serializers.CharField(source='config_ticket.nome', read_only=True)
    tipo_nome = serializers.CharField(source='get_tipo_display', read_only=True)
    status_nome = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = HubspotTicketLog
        fields = [
            'id',
            'atendimento',
            'atendimento_titulo',
            'atendimento_matricula',
            'integracao',
            'integracao_nome',
            'config_ticket',
            'config_ticket_nome',
            'tipo',
            'tipo_nome',
            'pipeline_id',
            'stage_id',
            'hubspot_ticket_id',
            'status',
            'status_nome',
            'payload_enviado',
            'resposta_api',
            'erro',
            'criado_em',
            'enviado_em',
            'atualizado_em'
        ]
        read_only_fields = fields


