from django.contrib import admin
from .models import UnidadeAtendimento


@admin.register(UnidadeAtendimento)
class UnidadeAtendimentoAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'nome', 'ativa', 'criada_em']
    list_filter = ['ativa']
    search_fields = ['nome', 'codigo']
    ordering = ['nome']