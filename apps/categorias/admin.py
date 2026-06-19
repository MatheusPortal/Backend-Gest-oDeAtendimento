from django.contrib import admin
from .models import CategoriaSenha, SubcategoriaSenha


class SubcategoriaSenhaInline(admin.TabularInline):
    model = SubcategoriaSenha
    extra = 1


@admin.register(CategoriaSenha)
class CategoriaSenhaAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'nome', 'ativa', 'criada_em']
    list_filter = ['ativa']
    search_fields = ['nome', 'codigo']
    ordering = ['nome']
    inlines = [SubcategoriaSenhaInline]


@admin.register(SubcategoriaSenha)
class SubcategoriaSenhaAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'nome', 'categoria', 'ativa', 'criada_em']
    list_filter = ['ativa', 'categoria']
    search_fields = ['nome', 'codigo', 'categoria__nome']
    ordering = ['categoria__nome', 'nome']