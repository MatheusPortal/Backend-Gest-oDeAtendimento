from django.db import models
from django.utils import timezone


class Atendimento(models.Model):
    class Status(models.TextChoices):
        FINALIZADO = 'FINALIZADO', 'Finalizado'
        CANCELADO = 'CANCELADO', 'Cancelado'

    senha = models.OneToOneField(
        'senhas.Senha',
        on_delete=models.PROTECT,
        related_name='atendimento'
    )

    atendente = models.ForeignKey(
        'usuarios.Funcionario',
        on_delete=models.SET_NULL,
        related_name='atendimentos',
        blank=True,
        null=True
    )

    unidade = models.ForeignKey(
        'unidades.UnidadeAtendimento',
        on_delete=models.PROTECT,
        related_name='atendimentos'
    )

    categoria = models.ForeignKey(
        'categorias.CategoriaSenha',
        on_delete=models.PROTECT,
        related_name='atendimentos'
    )

    subcategoria = models.ForeignKey(
        'categorias.SubcategoriaSenha',
        on_delete=models.PROTECT,
        related_name='atendimentos'
    )

    titulo = models.CharField(max_length=180)
    matricula = models.CharField(max_length=50)
    cpf = models.CharField(max_length=14)
    email = models.EmailField()
    descricao = models.TextField()

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.FINALIZADO
    )

    criado_em = models.DateTimeField(auto_now_add=True)
    finalizado_em = models.DateTimeField(default=timezone.now)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'atendimentos'
        ordering = ['-criado_em']
        verbose_name = 'Atendimento'
        verbose_name_plural = 'Atendimentos'

    def __str__(self):
        return f'{self.senha.codigo} - {self.titulo}'