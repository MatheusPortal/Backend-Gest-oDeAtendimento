from django.contrib import admin

from apps.integracoes.models import (
    IntegracaoHubspot,
    HubspotTicketConfig,
    HubspotCampoMapeado,
    HubspotTicketLog
)


class HubspotCampoMapeadoInline(admin.TabularInline):
    model = HubspotCampoMapeado
    extra = 1


@admin.register(IntegracaoHubspot)
class IntegracaoHubspotAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nome',
        'identificador',
        'base_url',
        'token_cadastrado',
        'ativa',
        'criada_em'
    ]

    list_filter = [
        'ativa'
    ]

    search_fields = [
        'nome',
        'identificador'
    ]

    readonly_fields = [
        'criada_em',
        'atualizada_em'
    ]


@admin.register(HubspotTicketConfig)
class HubspotTicketConfigAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'nome',
        'tipo',
        'integracao',
        'pipeline_id',
        'stage_id',
        'criar_automaticamente',
        'permitir_manual',
        'ativo'
    ]

    list_filter = [
        'tipo',
        'ativo',
        'criar_automaticamente',
        'permitir_manual',
        'integracao'
    ]

    search_fields = [
        'nome',
        'pipeline_id',
        'pipeline_nome',
        'stage_id',
        'stage_nome'
    ]

    inlines = [
        HubspotCampoMapeadoInline
    ]


@admin.register(HubspotCampoMapeado)
class HubspotCampoMapeadoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'config_ticket',
        'propriedade_hubspot',
        'origem',
        'campo_sistema',
        'chave_front',
        'obrigatorio',
        'ativo',
        'ordem'
    ]

    list_filter = [
        'origem',
        'obrigatorio',
        'ativo',
        'config_ticket__tipo'
    ]

    search_fields = [
        'propriedade_hubspot',
        'nome_exibicao',
        'campo_sistema',
        'chave_front',
        'valor_fixo'
    ]


@admin.register(HubspotTicketLog)
class HubspotTicketLogAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'atendimento',
        'tipo',
        'integracao',
        'config_ticket',
        'hubspot_ticket_id',
        'status',
        'criado_em',
        'enviado_em'
    ]

    list_filter = [
        'tipo',
        'status',
        'integracao',
        'config_ticket',
        'criado_em'
    ]

    search_fields = [
        'hubspot_ticket_id',
        'erro',
        'atendimento__titulo',
        'atendimento__matricula',
        'atendimento__cpf'
    ]

    readonly_fields = [
        'criado_em',
        'enviado_em',
        'atualizado_em'
    ]


