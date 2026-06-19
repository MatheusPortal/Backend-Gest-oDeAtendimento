from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.senhas.models import Senha


STATUS_CANCELAVEIS = [
    Senha.Status.AGUARDANDO,
    Senha.Status.PULADA
]


@transaction.atomic
def excluir_todas_senhas_pendentes(unidade_id=None):
    queryset = Senha.objects.filter(
        status__in=STATUS_CANCELAVEIS
    )

    if unidade_id:
        queryset = queryset.filter(unidade_id=unidade_id)

    total = queryset.count()

    queryset.update(
        status=Senha.Status.CANCELADA,
        cancelada_em=timezone.now(),
        colaborador_atual=None
    )

    return total


@transaction.atomic
def excluir_senhas_por_categoria(categoria_id, unidade_id=None):
    if not categoria_id:
        raise ValidationError({
            'categoria': 'Informe a categoria.'
        })

    queryset = Senha.objects.filter(
        categoria_id=categoria_id,
        status__in=STATUS_CANCELAVEIS
    )

    if unidade_id:
        queryset = queryset.filter(unidade_id=unidade_id)

    total = queryset.count()

    queryset.update(
        status=Senha.Status.CANCELADA,
        cancelada_em=timezone.now(),
        colaborador_atual=None
    )

    return total

