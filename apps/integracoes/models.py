from django.db import models


class IntegracaoHubspot(models.Model):
    nome = models.CharField(max_length=120)
    identificador = models.SlugField(max_length=80, unique=True)
    base_url = models.URLField(default='https://api.hubapi.com')
    token_acesso = models.TextField(blank=True, null=True)
    ativa = models.BooleanField(default=True)

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'integracoes_hubspot'
        ordering = ['nome']
        verbose_name = 'Integração HubSpot'
        verbose_name_plural = 'Integrações HubSpot'

    def __str__(self):
        return self.nome

    @property
    def token_cadastrado(self):
        return bool(self.token_acesso)


class HubspotTicketConfig(models.Model):
    class TipoTicket(models.TextChoices):
        REGISTRO_ATENDIMENTO = 'REGISTRO_ATENDIMENTO', 'Registro de atendimento'
        CHAMADO_INTERNO = 'CHAMADO_INTERNO', 'Chamado interno'

    integracao = models.ForeignKey(
        IntegracaoHubspot,
        on_delete=models.CASCADE,
        related_name='configs_ticket'
    )

    nome = models.CharField(max_length=120)

    tipo = models.CharField(
        max_length=30,
        choices=TipoTicket.choices
    )

    pipeline_id = models.CharField(max_length=120)
    pipeline_nome = models.CharField(max_length=180, blank=True, null=True)

    stage_id = models.CharField(max_length=120)
    stage_nome = models.CharField(max_length=180, blank=True, null=True)

    criar_automaticamente = models.BooleanField(default=False)
    permitir_manual = models.BooleanField(default=True)

    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=1)

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hubspot_ticket_configs'
        ordering = ['tipo', 'ordem', 'nome']
        verbose_name = 'Configuração de ticket HubSpot'
        verbose_name_plural = 'Configurações de tickets HubSpot'

    def __str__(self):
        return f'{self.nome} - {self.get_tipo_display()}'


class HubspotCampoMapeado(models.Model):
    class OrigemValor(models.TextChoices):
        CAMPO_SISTEMA = 'CAMPO_SISTEMA', 'Campo do sistema'
        VALOR_FIXO = 'VALOR_FIXO', 'Valor fixo'
        CAMPO_FRONT = 'CAMPO_FRONT', 'Campo informado no front'

    class CampoSistema(models.TextChoices):
        TITULO = 'titulo', 'Título'
        DESCRICAO = 'descricao', 'Descrição'
        MATRICULA = 'matricula', 'Matrícula'
        CPF = 'cpf', 'CPF'
        EMAIL_ALUNO = 'email', 'E-mail do aluno'
        SENHA_CODIGO = 'senha.codigo', 'Código da senha'
        UNIDADE_NOME = 'unidade.nome', 'Nome da unidade'
        UNIDADE_CODIGO = 'unidade.codigo', 'Código da unidade'
        COLABORADOR_NOME = 'colaborador.nome', 'Nome do colaborador'
        COLABORADOR_EMAIL = 'colaborador.email', 'E-mail do colaborador'
        CATEGORIA_NOME = 'categoria.nome', 'Categoria'
        SUBCATEGORIA_NOME = 'subcategoria.nome', 'Subcategoria'
        PRIORIDADE_NOME = 'prioridade.nome', 'Prioridade'
        DATA_FINALIZACAO = 'finalizado_em', 'Data de finalização'

    config_ticket = models.ForeignKey(
        HubspotTicketConfig,
        on_delete=models.CASCADE,
        related_name='campos_mapeados'
    )

    propriedade_hubspot = models.CharField(max_length=120)
    nome_exibicao = models.CharField(max_length=180, blank=True, null=True)

    origem = models.CharField(
        max_length=30,
        choices=OrigemValor.choices,
        default=OrigemValor.CAMPO_SISTEMA
    )

    campo_sistema = models.CharField(
        max_length=80,
        choices=CampoSistema.choices,
        blank=True,
        null=True
    )

    chave_front = models.CharField(max_length=120, blank=True, null=True)
    valor_fixo = models.TextField(blank=True, null=True)

    obrigatorio = models.BooleanField(default=False)
    ativo = models.BooleanField(default=True)
    ordem = models.PositiveIntegerField(default=1)

    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hubspot_campos_mapeados'
        ordering = ['config_ticket', 'ordem', 'propriedade_hubspot']
        verbose_name = 'Campo mapeado HubSpot'
        verbose_name_plural = 'Campos mapeados HubSpot'

    def __str__(self):
        return f'{self.propriedade_hubspot} - {self.config_ticket.nome}'


class HubspotTicketLog(models.Model):
    class StatusEnvio(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        ENVIADO = 'ENVIADO', 'Enviado'
        ERRO = 'ERRO', 'Erro'

    atendimento = models.ForeignKey(
        'atendimentos.Atendimento',
        on_delete=models.SET_NULL,
        related_name='hubspot_logs',
        blank=True,
        null=True
    )

    integracao = models.ForeignKey(
        IntegracaoHubspot,
        on_delete=models.SET_NULL,
        related_name='logs_ticket',
        blank=True,
        null=True
    )

    config_ticket = models.ForeignKey(
        HubspotTicketConfig,
        on_delete=models.SET_NULL,
        related_name='logs_ticket',
        blank=True,
        null=True
    )

    tipo = models.CharField(
        max_length=30,
        choices=HubspotTicketConfig.TipoTicket.choices
    )

    pipeline_id = models.CharField(max_length=120, blank=True, null=True)
    stage_id = models.CharField(max_length=120, blank=True, null=True)

    hubspot_ticket_id = models.CharField(max_length=120, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=StatusEnvio.choices,
        default=StatusEnvio.PENDENTE
    )

    payload_enviado = models.JSONField(default=dict, blank=True)
    resposta_api = models.JSONField(default=dict, blank=True)

    erro = models.TextField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    enviado_em = models.DateTimeField(blank=True, null=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hubspot_ticket_logs'
        ordering = ['-criado_em']
        verbose_name = 'Log de ticket HubSpot'
        verbose_name_plural = 'Logs de tickets HubSpot'

    def __str__(self):
        return f'{self.get_tipo_display()} - {self.status}'
    
    