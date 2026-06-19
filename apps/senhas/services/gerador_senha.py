from django.db import transaction, IntegrityError

from apps.senhas.models import Senha


def gerar_codigo_senha(categoria):
    prefixo = categoria.codigo.upper()

    total_categoria = Senha.objects.filter(
        categoria=categoria
    ).count()

    numero = total_categoria + 1

    return f'{prefixo}{numero:03d}'


@transaction.atomic
def gerar_senha(cpf, categoria, prioridade, unidade, humor):
    tentativas = 0

    while tentativas < 10:
        codigo = gerar_codigo_senha(categoria)

        try:
            senha = Senha.objects.create(
                codigo=codigo,
                cpf=cpf,
                categoria=categoria,
                prioridade=prioridade,
                unidade=unidade,
                humor=humor,
                status=Senha.Status.AGUARDANDO
            )

            return senha

        except IntegrityError:
            tentativas += 1

    raise IntegrityError('Não foi possível gerar um código único para a senha.')