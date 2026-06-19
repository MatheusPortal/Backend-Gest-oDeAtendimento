from django.db import models
from django.contrib.auth.models import User


class PerfilAcesso(models.Model):
    class Perfis(models.TextChoices):
        SUPERVISOR = 'SUPERVISOR', 'Supervisor'
        COLABORADOR = 'COLABORADOR', 'Colaborador'

    nome = models.CharField(max_length=30, choices=Perfis.choices, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'perfis_acesso'
        ordering = ['nome']
        verbose_name = 'Perfil de acesso'
        verbose_name_plural = 'Perfis de acesso'

    def __str__(self):
        return self.get_nome_display()


class PermissaoSistema(models.Model):
    class Modulos(models.TextChoices):
        UNIDADE = 'UNIDADE', 'Unidade de atendimento'
        COLABORADOR = 'COLABORADOR', 'Colaboradores'
        CATEGORIA = 'CATEGORIA', 'Categorias de senha'
        SUBCATEGORIA = 'SUBCATEGORIA', 'Subcategorias de senha'
        PRIORIDADE = 'PRIORIDADE', 'Prioridades de senha'
        SENHA = 'SENHA', 'Senhas'
        FILA = 'FILA', 'Fila'
        ATENDIMENTO = 'ATENDIMENTO', 'Atendimento'
        RELATORIO = 'RELATORIO', 'Relatórios'
        PERMISSAO = 'PERMISSAO', 'Permissões'
        INTEGRACAO = 'INTEGRACAO', 'Integrações'
        CONFIGURACAO = 'CONFIGURACAO', 'Configurações'
        GUICHE = 'GUICHE', 'Guichês'

    codigo = models.CharField(max_length=100, unique=True)
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True, null=True)
    modulo = models.CharField(max_length=30, choices=Modulos.choices)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'permissoes_sistema'
        ordering = ['modulo', 'codigo']
        verbose_name = 'Permissão do sistema'
        verbose_name_plural = 'Permissões do sistema'

    def __str__(self):
        return f'{self.codigo} - {self.nome}'


class PerfilPermissao(models.Model):
    perfil = models.ForeignKey(
        PerfilAcesso,
        on_delete=models.CASCADE,
        related_name='permissoes_do_perfil'
    )
    permissao = models.ForeignKey(
        PermissaoSistema,
        on_delete=models.CASCADE,
        related_name='perfis_com_permissao'
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'perfil_permissoes'
        unique_together = ['perfil', 'permissao']
        verbose_name = 'Permissão do perfil'
        verbose_name_plural = 'Permissões dos perfis'

    def __str__(self):
        return f'{self.perfil} - {self.permissao.codigo}'


class Funcionario(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='funcionario'
    )
    perfil = models.ForeignKey(
        PerfilAcesso,
        on_delete=models.PROTECT,
        related_name='funcionarios'
    )
    unidade = models.ForeignKey(
        'unidades.UnidadeAtendimento',
        on_delete=models.SET_NULL,
        related_name='funcionarios',
        blank=True,
        null=True
    )
    nome = models.CharField(max_length=150)
    matricula = models.CharField(max_length=50, unique=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'funcionarios'
        ordering = ['nome']
        verbose_name = 'Funcionário'
        verbose_name_plural = 'Funcionários'

    def __str__(self):
        return f'{self.nome} - {self.matricula}'


class FuncionarioPermissao(models.Model):
    funcionario = models.ForeignKey(
        Funcionario,
        on_delete=models.CASCADE,
        related_name='permissoes_individuais'
    )
    permissao = models.ForeignKey(
        PermissaoSistema,
        on_delete=models.CASCADE,
        related_name='funcionarios_com_permissao'
    )
    permitido = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'funcionario_permissoes'
        unique_together = ['funcionario', 'permissao']
        verbose_name = 'Permissão individual'
        verbose_name_plural = 'Permissões individuais'

    def __str__(self):
        status = 'Permitido' if self.permitido else 'Bloqueado'
        return f'{self.funcionario.nome} - {self.permissao.codigo} - {status}'