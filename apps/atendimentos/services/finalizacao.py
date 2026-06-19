from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied

from apps.atendimentos.models import Atendimento
from apps.senhas.models import Senha
from apps.usuarios.services.permissoes import obter_funcionario_usuario
from apps.integracoes.services.hubspot_payload import preparar_logs_hubspot_atendimento


def obter_funcionario_para_finalizacao(user):
    if user.is_superuser:
        return None

    funcionario = obter_funcionario_usuario(user)

    if not funcionario:
        raise PermissionDenied('Usuário não possui funcionário vinculado.')

    if not funcionario.ativo:
        raise PermissionDenied('Funcionário inativo.')

    return funcionario


@transaction.atomic
def finalizar_atendimento_completo(user, senha, dados):
    funcionario = obter_funcionario_para_finalizacao(user)

    if senha.status != Senha.Status.EM_ATENDIMENTO:
        raise ValidationError({
            'status': 'A senha precisa estar em atendimento para ser finalizada.'
        })

    if funcionario and senha.colaborador_atual and senha.colaborador_atual != funcionario:
        raise PermissionDenied('Esta senha está vinculada a outro colaborador.')

    if hasattr(senha, 'atendimento'):
        raise ValidationError({
            'atendimento': 'Esta senha já possui atendimento registrado.'
        })
    
    dados_hubspot = dados.get('hubspot') or {}
    
    atendimento = Atendimento.objects.create(
        senha=senha,
        atendente=funcionario,
        unidade=senha.unidade,
        categoria=dados['categoria'],
        subcategoria=dados['subcategoria'],
        titulo=dados['titulo'],
        matricula=dados['matricula'],
        cpf=dados['cpf'],
        email=dados['email'],
        descricao=dados['descricao'],
        status=Atendimento.Status.FINALIZADO,
        finalizado_em=timezone.now()
    )

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

    preparar_logs_hubspot_atendimento(
        atendimento=atendimento,
        opcoes_hubspot=dados_hubspot
    )
    
    return atendimento