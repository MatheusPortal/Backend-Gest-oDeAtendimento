from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound

from apps.senhas.models import Senha
from apps.unidades.models import UnidadeAtendimento
from apps.usuarios.services.permissoes import obter_funcionario_usuario
from rest_framework.exceptions import ValidationError
from apps.guiches.models import GuicheAtendimento


def obter_contexto_operacao(user, unidade_id=None):
    funcionario = obter_funcionario_usuario(user)

    if user.is_superuser:
        if not unidade_id:
            raise ValidationError({
                'unidade': 'Informe a unidade para operação como superusuário.'
            })

        try:
            unidade = UnidadeAtendimento.objects.get(id=unidade_id, ativa=True)
        except UnidadeAtendimento.DoesNotExist:
            raise NotFound('Unidade de atendimento não encontrada ou inativa.')

        return unidade, funcionario

    if not funcionario:
        raise PermissionDenied('Usuário não possui funcionário vinculado.')

    if not funcionario.ativo:
        raise PermissionDenied('Funcionário inativo.')

    if not funcionario.unidade:
        raise PermissionDenied('Funcionário não possui unidade vinculada.')

    return funcionario.unidade, funcionario


def listar_fila(unidade):
    return Senha.objects.select_related(
        'categoria',
        'prioridade',
        'unidade',
        'colaborador_atual',
        'colaborador_chamou',
        'colaborador_finalizou'
    ).filter(
        unidade=unidade,
        status=Senha.Status.AGUARDANDO
    ).order_by(
        '-prioridade__peso',
        'gerada_em'
    )


@transaction.atomic
def chamar_proxima_senha(user, unidade_id=None, guiche_id=None):
    funcionario, unidade = obter_contexto_operacao(user, unidade_id)

    guiche = None

    if guiche_id:
        try:
            guiche = GuicheAtendimento.objects.get(
                id=guiche_id,
                unidade=unidade,
                ativo=True
            )
        except GuicheAtendimento.DoesNotExist:
            raise ValidationError({
                'guiche': 'Guichê não encontrado, inativo ou pertence a outra unidade.'
            })

        if not guiche.disponivel:
            raise ValidationError({
                'guiche': 'Este guichê está indisponível.'
            })

        if funcionario and guiche.funcionario_atual and guiche.funcionario_atual != funcionario:
            raise ValidationError({
                'guiche': 'Este guichê está vinculado a outro funcionário.'
            })

    elif funcionario:
        guiche = GuicheAtendimento.objects.filter(
            funcionario_atual=funcionario,
            unidade=unidade,
            ativo=True,
            disponivel=True
        ).first()

    with transaction.atomic():
        senha = Senha.objects.select_for_update().filter(
            unidade=unidade,
            status=Senha.Status.AGUARDANDO
        ).order_by(
            '-prioridade__peso',
            'gerada_em'
        ).first()

        if not senha:
            raise ValidationError({
                'senha': 'Não há senhas aguardando nesta unidade.'
            })

        senha.status = Senha.Status.CHAMADA
        senha.chamada_em = timezone.now()
        senha.colaborador_atual = funcionario
        senha.colaborador_chamou = funcionario
        senha.guiche = guiche

        senha.save(update_fields=[
            'status',
            'chamada_em',
            'colaborador_atual',
            'colaborador_chamou',
            'guiche',
            'atualizada_em'
        ])

        return senha
    


def obter_senha_atual(user, unidade_id=None):
    unidade, funcionario = obter_contexto_operacao(user, unidade_id)

    queryset = Senha.objects.select_related(
        'categoria',
        'prioridade',
        'unidade',
        'colaborador_atual',
        'colaborador_chamou',
        'colaborador_finalizou'
    ).filter(
        unidade=unidade,
        status__in=[
            Senha.Status.CHAMADA,
            Senha.Status.EM_ATENDIMENTO
        ]
    )

    if funcionario:
        queryset = queryset.filter(colaborador_atual=funcionario)

    return queryset.order_by('-chamada_em').first()