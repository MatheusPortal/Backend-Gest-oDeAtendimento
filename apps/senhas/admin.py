from django.contrib import admin
from .models import PrioridadeSenha, Senha


@admin.register(PrioridadeSenha)
class PrioridadeSenhaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'codigo',
        'nome',
        'peso',
        'cor',
        'visivel_na_geracao',
        'ativo',
        'criado_em'
    ]
    list_filter = [
        'ativo',
        'codigo',
        'visivel_na_geracao'
    ]
    search_fields = [
        'nome',
        'codigo'
    ]
    ordering = [
        '-peso',
        'nome'
    ]


@admin.register(Senha)
class SenhaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'codigo',
        'cpf',
        'categoria',
        'prioridade',
        'humor',
        'unidade',
        'status',
        'colaborador_atual',
        'gerada_em',
        'colaborador_pulou',
        'colaborador_redirecionou',
        'colaborador_destino',
        'guiche',

    ]
    list_filter = [
        'status',
        'prioridade',
        'humor',
        'categoria',
        'unidade',
        'gerada_em',
        'colaborador_redirecionou',
        'colaborador_destino',
        'guiche',
    ]
    search_fields = [
        'codigo',
        'cpf',
        'categoria__nome',
        'unidade__nome'
    ]
    readonly_fields = [
        'gerada_em',
        'atualizada_em',
        'chamada_em',
        'iniciada_em',
        'finalizada_em',
        'pulada_em',
        'cancelada_em',
        'redirecionada_em'
    ]
    ordering = [
        '-gerada_em'
    ]