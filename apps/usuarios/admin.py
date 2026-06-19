from django.contrib import admin
from .models import (
    PerfilAcesso,
    PermissaoSistema,
    PerfilPermissao,
    Funcionario,
    FuncionarioPermissao
)


@admin.register(PerfilAcesso)
class PerfilAcessoAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'ativo', 'criado_em']
    list_filter = ['ativo', 'nome']
    search_fields = ['nome']


@admin.register(PermissaoSistema)
class PermissaoSistemaAdmin(admin.ModelAdmin):
    list_display = ['id', 'codigo', 'nome', 'modulo', 'ativa']
    list_filter = ['modulo', 'ativa']
    search_fields = ['codigo', 'nome']


@admin.register(PerfilPermissao)
class PerfilPermissaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'perfil', 'permissao', 'criado_em']
    list_filter = ['perfil', 'permissao__modulo']
    search_fields = ['perfil__nome', 'permissao__codigo', 'permissao__nome']


@admin.register(Funcionario)
class FuncionarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nome', 'matricula', 'perfil', 'unidade', 'ativo']
    list_filter = ['perfil', 'unidade', 'ativo']
    search_fields = ['nome', 'matricula', 'user__username']


@admin.register(FuncionarioPermissao)
class FuncionarioPermissaoAdmin(admin.ModelAdmin):
    list_display = ['id', 'funcionario', 'permissao', 'permitido']
    list_filter = ['permitido', 'permissao__modulo']
    search_fields = ['funcionario__nome', 'funcionario__matricula', 'permissao__codigo']