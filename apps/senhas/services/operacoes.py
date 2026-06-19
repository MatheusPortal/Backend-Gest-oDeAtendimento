from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from apps.senhas.models import Senha, PrioridadeSenha
from apps.usuarios.services.permissoes import obter_funcionario_usuario


def obter_senha_por_id(senha_id):
    try:
        return Senha.objects.select_related(
            'categoria',
            'prioridade',
            'unidade',
            'colaborador_atual',
            'colaborador_chamou',
            'colaborador_finalizou'
        ).get(id=senha_id)
    except Senha.DoesNotExist:
        raise NotFound('Senha não encontrada.')


def validar_funcionario_operacao(user):
    if user.is_superuser:
        return None

    funcionario = obter_funcionario_usuario(user)

    if not funcionario:
        raise PermissionDenied('Usuário não possui funcionário vinculado.')

    if not funcionario.ativo:
        raise PermissionDenied('Funcionário inativo.')

    return funcionario


@transaction.atomic
def iniciar_atendimento_senha(user, senha_id):
    funcionario = validar_funcionario_operacao(user)
    senha = obter_senha_por_id(senha_id)

    if senha.status != Senha.Status.CHAMADA:
        raise ValidationError({
            'status': 'A senha precisa estar chamada para iniciar o atendimento.'
        })

    if funcionario and senha.colaborador_atual and senha.colaborador_atual != funcionario:
        raise PermissionDenied('Esta senha está vinculada a outro colaborador.')

    senha.status = Senha.Status.EM_ATENDIMENTO
    senha.iniciada_em = timezone.now()

    if funcionario:
        senha.colaborador_atual = funcionario

    senha.save(update_fields=[
        'status',
        'iniciada_em',
        'colaborador_atual',
        'atualizada_em'
    ])

    return senha


@transaction.atomic
def pular_senha(user, senha_id):
    funcionario = validar_funcionario_operacao(user)
    senha = obter_senha_por_id(senha_id)

    if senha.status not in [
        Senha.Status.CHAMADA,
        Senha.Status.EM_ATENDIMENTO
    ]:
        raise ValidationError({
            'status': 'Somente senhas chamadas ou em atendimento podem ser puladas.'
        })

    if funcionario and senha.colaborador_atual and senha.colaborador_atual != funcionario:
        raise PermissionDenied('Esta senha está vinculada a outro colaborador.')

    senha.status = Senha.Status.PULADA
    senha.pulada_em = timezone.now()
    senha.colaborador_pulou = funcionario
    senha.colaborador_atual = None

    senha.save(update_fields=[
        'status',
        'pulada_em',
        'colaborador_atual',
        'atualizada_em',
        'colaborador_pulou',
    ])

    return senha


@transaction.atomic
def retornar_senha_pulada(user, senha_id):
    validar_funcionario_operacao(user)
    senha = obter_senha_por_id(senha_id)

    if senha.status != Senha.Status.PULADA:
        raise ValidationError({
            'status': 'Somente senhas puladas podem retornar para a fila.'
        })

    if not senha.pulada_em:
        raise ValidationError({
            'pulada_em': 'A senha não possui horário de pulo registrado.'
        })

    limite = senha.pulada_em + timedelta(minutes=15)

    if timezone.now() > limite:
        raise ValidationError({
            'tempo': 'Essa senha foi pulada há mais de 15 minutos e não pode retornar para a fila.'
        })

    try:
        prioridade_medio = PrioridadeSenha.objects.get(
            codigo=PrioridadeSenha.Codigos.MEDIO,
            ativo=True
        )
    except PrioridadeSenha.DoesNotExist:
        raise ValidationError({
            'prioridade': 'Prioridade Médio não encontrada ou inativa.'
        })

    senha.status = Senha.Status.AGUARDANDO
    senha.prioridade = prioridade_medio
    senha.colaborador_atual = None

    senha.save(update_fields=[
        'status',
        'prioridade',
        'colaborador_atual',
        'atualizada_em'
    ])

    return senha


@transaction.atomic
def cancelar_senha(user, senha_id):
    funcionario = validar_funcionario_operacao(user)
    senha = obter_senha_por_id(senha_id)

    if senha.status in [
        Senha.Status.FINALIZADA,
        Senha.Status.CANCELADA
    ]:
        raise ValidationError({
            'status': 'Senha finalizada ou cancelada não pode ser cancelada novamente.'
        })

    if funcionario and senha.colaborador_atual and senha.colaborador_atual != funcionario:
        raise PermissionDenied('Esta senha está vinculada a outro colaborador.')

    senha.status = Senha.Status.CANCELADA
    senha.cancelada_em = timezone.now()
    senha.colaborador_atual = None

    senha.save(update_fields=[
        'status',
        'cancelada_em',
        'colaborador_atual',
        'atualizada_em'
    ])

    return senha


@transaction.atomic
def finalizar_senha_simples(user, senha_id):
    funcionario = validar_funcionario_operacao(user)
    senha = obter_senha_por_id(senha_id)

    if senha.status != Senha.Status.EM_ATENDIMENTO:
        raise ValidationError({
            'status': 'A senha precisa estar em atendimento para ser finalizada.'
        })

    if funcionario and senha.colaborador_atual and senha.colaborador_atual != funcionario:
        raise PermissionDenied('Esta senha está vinculada a outro colaborador.')

    senha.status = Senha.Status.FINALIZADA
    senha.finalizada_em = timezone.now()
    senha.colaborador_finalizou = funcionario
    senha.colaborador_atual = None

    senha.save(update_fields=[
        'status',
        'finalizada_em',
        'colaborador_finalizou',
        'colaborador_atual',
        'atualizada_em'
    ])

    return senha