from django.contrib import admin
from .models import GuicheAtendimento


@admin.register(GuicheAtendimento)
class GuicheAtendimentoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'numero',
        'nome',
        'unidade',
        'funcionario_atual',
        'ativo',
        'disponivel',
        'criado_em'
    ]

    list_filter = [
        'ativo',
        'disponivel',
        'unidade'
    ]

    search_fields = [
        'numero',
        'nome',
        'unidade__nome',
        'funcionario_atual__nome',
        'funcionario_atual__matricula'
    ]

