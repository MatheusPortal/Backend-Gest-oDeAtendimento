from django.db import models


class GuicheAtendimento(models.Model):
    unidade = models.ForeignKey(
        'unidades.UnidadeAtendimento',
        on_delete=models.CASCADE,
        related_name='guiches'
    )

    numero = models.CharField(max_length=10)
    nome = models.CharField(max_length=100, blank=True, null=True)

    funcionario_atual = models.ForeignKey(
        'usuarios.Funcionario',
        on_delete=models.SET_NULL,
        related_name='guiches_vinculados',
        blank=True,
        null=True
    )

    ativo = models.BooleanField(default=True)
    disponivel = models.BooleanField(default=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'guiches_atendimento'
        ordering = ['unidade__nome', 'numero']
        unique_together = ['unidade', 'numero']
        verbose_name = 'Guichê de atendimento'
        verbose_name_plural = 'Guichês de atendimento'

    def __str__(self):
        return f'Guichê {self.numero} - {self.unidade.nome}'
    
    