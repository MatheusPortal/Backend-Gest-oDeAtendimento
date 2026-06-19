from django.db import models


class PrioridadeSenha(models.Model):
    class Codigos(models.TextChoices):
        NORMAL = 'NORMAL', 'Normal'
        MEDIO = 'MEDIO', 'Médio'
        PREFERENCIAL = 'PREFERENCIAL', 'Preferencial'

    nome = models.CharField(max_length=100, unique=True)
    codigo = models.CharField(max_length=30, choices=Codigos.choices, unique=True)
    peso = models.PositiveIntegerField(default=1)
    cor = models.CharField(max_length=20, blank=True, null=True)
    descricao = models.TextField(blank=True, null=True)
    visivel_na_geracao = models.BooleanField(default=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'prioridades_senha'
        ordering = ['-peso', 'nome']
        verbose_name = 'Prioridade de senha'
        verbose_name_plural = 'Prioridades de senha'

    def __str__(self):
        return f'{self.nome} - peso {self.peso}'


class Senha(models.Model):
    class Status(models.TextChoices):
        AGUARDANDO = 'AGUARDANDO', 'Aguardando'
        CHAMADA = 'CHAMADA', 'Chamada'
        EM_ATENDIMENTO = 'EM_ATENDIMENTO', 'Em atendimento'
        PULADA = 'PULADA', 'Pulada'
        FINALIZADA = 'FINALIZADA', 'Finalizada'
        CANCELADA = 'CANCELADA', 'Cancelada'
        REDIRECIONADA = 'REDIRECIONADA', 'Redirecionada'

    class Humor(models.TextChoices):
        FELIZ = 'FELIZ', 'Feliz'
        NEUTRO = 'NEUTRO', 'Neutro'
        TRISTE = 'TRISTE', 'Triste'

    codigo = models.CharField(max_length=30, unique=True)
    cpf = models.CharField(max_length=14)


    categoria = models.ForeignKey(
        'categorias.CategoriaSenha',
        on_delete=models.PROTECT,
        related_name='senhas'
    )

    prioridade = models.ForeignKey(
        PrioridadeSenha,
        on_delete=models.PROTECT,
        related_name='senhas'
    )

    unidade = models.ForeignKey(
        'unidades.UnidadeAtendimento',
        on_delete=models.PROTECT,
        related_name='senhas'
    )
    
    guiche = models.ForeignKey(
        'guiches.GuicheAtendimento',
        on_delete=models.SET_NULL,
        related_name='senhas_chamadas',
        blank=True,
        null=True
    )

    colaborador_atual = models.ForeignKey(
        'usuarios.Funcionario',
        on_delete=models.SET_NULL,
        related_name='senhas_atuais',
        blank=True,
        null=True
    )

    colaborador_chamou = models.ForeignKey(
        'usuarios.Funcionario',
        on_delete=models.SET_NULL,
        related_name='senhas_chamadas',
        blank=True,
        null=True
    )

    colaborador_finalizou = models.ForeignKey(
        'usuarios.Funcionario',
        on_delete=models.SET_NULL,
        related_name='senhas_finalizadas',
        blank=True,
        null=True
    )
    
    colaborador_pulou = models.ForeignKey(
        'usuarios.Funcionario',
        on_delete=models.SET_NULL,
        related_name='senhas_puladas',
        blank=True,
        null=True
    )
    
    colaborador_redirecionou = models.ForeignKey(
        'usuarios.Funcionario',
        on_delete=models.SET_NULL,
        related_name='senhas_redirecionadas',
        blank=True,
        null=True
    )

    colaborador_destino = models.ForeignKey(
        'usuarios.Funcionario',
        on_delete=models.SET_NULL,
        related_name='senhas_recebidas_redirecionamento',
        blank=True,
        null=True
    )

    motivo_redirecionamento = models.TextField(blank=True, null=True)

    humor = models.CharField(
        max_length=20,
        choices=Humor.choices,
        default=Humor.NEUTRO
    )

    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.AGUARDANDO
    )

    gerada_em = models.DateTimeField(auto_now_add=True)
    chamada_em = models.DateTimeField(blank=True, null=True)
    iniciada_em = models.DateTimeField(blank=True, null=True)
    finalizada_em = models.DateTimeField(blank=True, null=True)
    pulada_em = models.DateTimeField(blank=True, null=True)
    cancelada_em = models.DateTimeField(blank=True, null=True)
    redirecionada_em = models.DateTimeField(blank=True, null=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'senhas'
        ordering = ['-prioridade__peso', 'gerada_em']
        verbose_name = 'Senha'
        verbose_name_plural = 'Senhas'

    def __str__(self):
        return f'{self.codigo} - {self.categoria.nome} - {self.status}'