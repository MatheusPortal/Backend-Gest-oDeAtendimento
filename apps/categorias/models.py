from django.db import models


class CategoriaSenha(models.Model):
    nome = models.CharField(max_length=150, unique=True)
    codigo = models.CharField(max_length=30, unique=True)
    descricao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'categorias_senha'
        ordering = ['nome']
        verbose_name = 'Categoria de senha'
        verbose_name_plural = 'Categorias de senha'

    def __str__(self):
        return f'{self.codigo} - {self.nome}'


class SubcategoriaSenha(models.Model):
    categoria = models.ForeignKey(
        CategoriaSenha,
        on_delete=models.PROTECT,
        related_name='subcategorias'
    )
    nome = models.CharField(max_length=150)
    codigo = models.CharField(max_length=30)
    descricao = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subcategorias_senha'
        ordering = ['categoria__nome', 'nome']
        unique_together = [
            ['categoria', 'nome'],
            ['categoria', 'codigo']
        ]
        verbose_name = 'Subcategoria de senha'
        verbose_name_plural = 'Subcategorias de senha'

    def __str__(self):
        return f'{self.categoria.nome} - {self.nome}'