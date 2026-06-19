from django.db import models


class UnidadeAtendimento(models.Model):
    nome = models.CharField(max_length=150)
    codigo = models.CharField(max_length=30, unique=True)
    endereco = models.CharField(max_length=255, blank=True, null=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'unidades_atendimento'
        ordering = ['nome']
        verbose_name = 'Unidade de atendimento'
        verbose_name_plural = 'Unidades de atendimento'

    def __str__(self):
        return f'{self.codigo} - {self.nome}'