from django.contrib import admin
from .models import ConfiguracaoUnidade, PreferenciaFuncionario


@admin.register(ConfiguracaoUnidade)
class ConfiguracaoUnidadeAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'unidade',
        'cor_primaria',
        'som_chamada_ativo',
        'quantidade_historico_painel',
        'quantidade_proximas_painel',
        'ativo'
    ]

    list_filter = [
        'ativo',
        'som_chamada_ativo'
    ]

    search_fields = [
        'unidade__nome',
        'unidade__codigo'
    ]


@admin.register(PreferenciaFuncionario)
class PreferenciaFuncionarioAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'funcionario',
        'som_mudo',
        'cor_pagina',
        'atualizada_em'
    ]

    list_filter = [
        'som_mudo'
    ]

    search_fields = [
        'funcionario__nome',
        'funcionario__matricula',
        'funcionario__user__username'
    ]

