from django.contrib import admin
from .models import Atendimento


@admin.register(Atendimento)
class AtendimentoAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'senha',
        'titulo',
        'matricula',
        'cpf',
        'categoria',
        'subcategoria',
        'unidade',
        'atendente',
        'status',
        'criado_em'
    ]

    list_filter = [
        'status',
        'categoria',
        'subcategoria',
        'unidade',
        'atendente',
        'criado_em'
    ]

    search_fields = [
        'senha__codigo',
        'titulo',
        'matricula',
        'cpf',
        'email',
        'descricao',
        'categoria__nome',
        'subcategoria__nome',
        'unidade__nome'
    ]

    readonly_fields = [
        'criado_em',
        'finalizado_em',
        'atualizado_em'
    ]

    ordering = [
        '-criado_em'
    ]