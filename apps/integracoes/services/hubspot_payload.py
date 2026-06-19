from rest_framework.exceptions import ValidationError

from apps.integracoes.models import (
    HubspotTicketConfig,
    HubspotCampoMapeado,
    HubspotTicketLog
)


def obter_valor_campo_sistema(atendimento, campo):
    senha = atendimento.senha
    atendente = atendimento.atendente

    mapa = {
        'titulo': atendimento.titulo,
        'descricao': atendimento.descricao,
        'matricula': atendimento.matricula,
        'cpf': atendimento.cpf,
        'email': atendimento.email,

        'senha.codigo': senha.codigo if senha else None,

        'unidade.nome': atendimento.unidade.nome if atendimento.unidade else None,
        'unidade.codigo': atendimento.unidade.codigo if atendimento.unidade else None,

        'colaborador.nome': atendente.nome if atendente else None,
        'colaborador.email': atendente.user.email if atendente and atendente.user else None,

        'categoria.nome': atendimento.categoria.nome if atendimento.categoria else None,
        'subcategoria.nome': atendimento.subcategoria.nome if atendimento.subcategoria else None,

        'prioridade.nome': senha.prioridade.nome if senha and senha.prioridade else None,

        'finalizado_em': atendimento.finalizado_em.isoformat() if atendimento.finalizado_em else None,
    }

    return mapa.get(campo)


def montar_payload_hubspot(config_ticket, atendimento, campos_front=None):
    campos_front = campos_front or {}

    propriedades = {
        'hs_pipeline': config_ticket.pipeline_id,
        'hs_pipeline_stage': config_ticket.stage_id
    }

    erros = []

    campos_mapeados = config_ticket.campos_mapeados.filter(
        ativo=True
    ).order_by(
        'ordem',
        'propriedade_hubspot'
    )

    for campo in campos_mapeados:
        valor = None

        if campo.origem == HubspotCampoMapeado.OrigemValor.CAMPO_SISTEMA:
            valor = obter_valor_campo_sistema(
                atendimento=atendimento,
                campo=campo.campo_sistema
            )

        elif campo.origem == HubspotCampoMapeado.OrigemValor.VALOR_FIXO:
            valor = campo.valor_fixo

        elif campo.origem == HubspotCampoMapeado.OrigemValor.CAMPO_FRONT:
            valor = campos_front.get(campo.chave_front)

        if campo.obrigatorio and (valor is None or valor == ''):
            erros.append(
                f'O campo obrigatório "{campo.propriedade_hubspot}" não recebeu valor.'
            )

        if valor is not None and valor != '':
            propriedades[campo.propriedade_hubspot] = valor

    payload = {
        'properties': propriedades
    }

    return payload, erros


def criar_log_hubspot(config_ticket, atendimento, campos_front=None):
    payload, erros = montar_payload_hubspot(
        config_ticket=config_ticket,
        atendimento=atendimento,
        campos_front=campos_front
    )

    status = HubspotTicketLog.StatusEnvio.PENDENTE
    erro = None

    if erros:
        status = HubspotTicketLog.StatusEnvio.ERRO
        erro = ' '.join(erros)

    log = HubspotTicketLog.objects.create(
        atendimento=atendimento,
        integracao=config_ticket.integracao,
        config_ticket=config_ticket,
        tipo=config_ticket.tipo,
        pipeline_id=config_ticket.pipeline_id,
        stage_id=config_ticket.stage_id,
        status=status,
        payload_enviado=payload,
        erro=erro
    )

    return log


def preparar_logs_hubspot_atendimento(atendimento, opcoes_hubspot=None):
    opcoes_hubspot = opcoes_hubspot or {}

    logs = []

    configs_registro = HubspotTicketConfig.objects.select_related(
        'integracao'
    ).prefetch_related(
        'campos_mapeados'
    ).filter(
        integracao__ativa=True,
        ativo=True,
        tipo=HubspotTicketConfig.TipoTicket.REGISTRO_ATENDIMENTO,
        criar_automaticamente=True
    )

    for config in configs_registro:
        log = criar_log_hubspot(
            config_ticket=config,
            atendimento=atendimento,
            campos_front={}
        )
        logs.append(log)

    abrir_chamado_interno = opcoes_hubspot.get('abrir_chamado_interno', False)

    if abrir_chamado_interno:
        config_chamado_id = opcoes_hubspot.get('config_chamado')
        campos_front = opcoes_hubspot.get('campos_front') or {}

        configs_chamado = HubspotTicketConfig.objects.select_related(
            'integracao'
        ).prefetch_related(
            'campos_mapeados'
        ).filter(
            integracao__ativa=True,
            ativo=True,
            tipo=HubspotTicketConfig.TipoTicket.CHAMADO_INTERNO,
            permitir_manual=True
        )

        if config_chamado_id:
            configs_chamado = configs_chamado.filter(id=config_chamado_id)

        configs_chamado = list(configs_chamado.order_by('ordem', 'nome'))

        if not configs_chamado:
            raise ValidationError({
                'hubspot': 'Nenhuma configuração ativa de chamado interno HubSpot foi encontrada.'
            })

        for config in configs_chamado:
            log = criar_log_hubspot(
                config_ticket=config,
                atendimento=atendimento,
                campos_front=campos_front
            )
            logs.append(log)

    return logs


