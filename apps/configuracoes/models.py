from django.db import models


class ConfiguracaoUnidade(models.Model):
    unidade = models.OneToOneField(
        'unidades.UnidadeAtendimento',
        on_delete=models.CASCADE,
        related_name='configuracao'
    )

    cor_primaria = models.CharField(max_length=20, default='#FFE3A3')
    cor_secundaria = models.CharField(max_length=20, default='#FFFFFF')
    cor_fundo = models.CharField(max_length=20, default='#F5F5F5')
    cor_texto = models.CharField(max_length=20, default='#000000')

    som_chamada_url = models.CharField(max_length=500, blank=True, null=True)
    som_chamada_ativo = models.BooleanField(default=True)

    quantidade_historico_painel = models.PositiveIntegerField(default=5)
    quantidade_proximas_painel = models.PositiveIntegerField(default=5)

    ativo = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configuracoes_unidade'
        verbose_name = 'Configuração da unidade'
        verbose_name_plural = 'Configurações das unidades'

    def __str__(self):
        return f'Configuração - {self.unidade.nome}'


class PreferenciaFuncionario(models.Model):
    funcionario = models.OneToOneField(
        'usuarios.Funcionario',
        on_delete=models.CASCADE,
        related_name='preferencias'
    )

    som_mudo = models.BooleanField(default=False)
    cor_pagina = models.CharField(max_length=20, blank=True, null=True)

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'preferencias_funcionario'
        verbose_name = 'Preferência do funcionário'
        verbose_name_plural = 'Preferências dos funcionários'

    def __str__(self):
        return f'Preferências - {self.funcionario.nome}'