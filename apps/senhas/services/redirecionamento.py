from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from apps.senhas.models import Senha
from apps.usuarios.models import Funcionario
from apps.usuarios.services.permissoes import obter_funcionario_usuario


def obter_funcionario_operador(user):
    if user.is_superuser:
        return None

    funcionario = obter_funcionario_usuario(user)

    if not funcionario:
        raise PermissionDenied('Usuário não possui funcionário vinculado.')

    if not funcionario.ativo:
        raise PermissionDenied('Funcionário inativo.')

    return funcionario


def colaborador_esta_disponivel(funcionario):
    existe_senha_em_atendimento = Senha.objects.filter(
        colaborador_atual=funcionario,
        status__in=[
            Senha.Status.CHAMADA,
            Senha.Status.EM_ATENDIMENTO
        ]
    ).exists()

    return not existe_senha_em_atendimento


def listar_colaboradores_disponiveis(unidade):
    colaboradores = Funcionario.objects.select_related(
        'user',
        'perfil',
        'unidade'
    ).filter(
        ativo=True,
        unidade=unidade
    ).order_by('nome')

    disponiveis = []

    for colaborador in colaboradores:
        if colaborador_esta_disponivel(colaborador):
            disponiveis.append(colaborador)

    return disponiveis


@transaction.atomic
def redirecionar_senha_para_colaborador(user, senha, colaborador_destino_id, motivo=None):
    operador = obter_funcionario_operador(user)

    if senha.status not in [
        Senha.Status.CHAMADA,
        Senha.Status.EM_ATENDIMENTO
    ]:
        raise ValidationError({
            'status': 'Somente senhas chamadas ou em atendimento podem ser redirecionadas para outro colaborador.'
        })

    if operador and senha.colaborador_atual and senha.colaborador_atual != operador:
        raise PermissionDenied('Esta senha está vinculada a outro colaborador.')

    try:
        colaborador_destino = Funcionario.objects.select_related('unidade').get(
            id=colaborador_destino_id,
            ativo=True
        )
    except Funcionario.DoesNotExist:
        raise NotFound('Colaborador de destino não encontrado ou inativo.')

    if colaborador_destino.unidade_id != senha.unidade_id:
        raise ValidationError({
            'colaborador_destino': 'O colaborador de destino precisa pertencer à mesma unidade da senha.'
        })

    if not colaborador_esta_disponivel(colaborador_destino):
        raise ValidationError({
            'colaborador_destino': 'O colaborador selecionado não está disponível.'
        })

    senha.status = Senha.Status.CHAMADA
    senha.colaborador_atual = colaborador_destino
    senha.colaborador_redirecionou = operador
    senha.colaborador_destino = colaborador_destino
    senha.redirecionada_em = timezone.now()
    senha.motivo_redirecionamento = motivo

    senha.save(update_fields=[
        'status',
        'colaborador_atual',
        'colaborador_redirecionou',
        'colaborador_destino',
        'redirecionada_em',
        'motivo_redirecionamento',
        'atualizada_em'
    ])

    return senha


@transaction.atomic
def redirecionar_senha_para_fila(user, senha, motivo=None):
    operador = obter_funcionario_operador(user)

    if senha.status not in [
        Senha.Status.CHAMADA,
        Senha.Status.EM_ATENDIMENTO
    ]:
        raise ValidationError({
            'status': 'Somente senhas chamadas ou em atendimento podem voltar para a fila.'
        })

    if operador and senha.colaborador_atual and senha.colaborador_atual != operador:
        raise PermissionDenied('Esta senha está vinculada a outro colaborador.')

    senha.status = Senha.Status.AGUARDANDO
    senha.colaborador_atual = None
    senha.colaborador_redirecionou = operador
    senha.colaborador_destino = None
    senha.redirecionada_em = timezone.now()
    senha.motivo_redirecionamento = motivo

    senha.save(update_fields=[
        'status',
        'colaborador_atual',
        'colaborador_redirecionou',
        'colaborador_destino',
        'redirecionada_em',
        'motivo_redirecionamento',
        'atualizada_em'
    ])

    return senha


