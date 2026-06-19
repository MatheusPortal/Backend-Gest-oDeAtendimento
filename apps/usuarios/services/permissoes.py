from apps.usuarios.models import (
    Funcionario,
    PermissaoSistema,
    PerfilPermissao,
    FuncionarioPermissao
)


def obter_permissoes_usuario(user):
    if not user or not user.is_authenticated:
        return []

    if user.is_superuser:
        return list(
            PermissaoSistema.objects.filter(ativa=True)
            .values_list('codigo', flat=True)
        )

    try:
        funcionario = user.funcionario
    except Funcionario.DoesNotExist:
        return []

    if not funcionario.ativo:
        return []

    permissoes_perfil = set(
        PerfilPermissao.objects.filter(
            perfil=funcionario.perfil,
            permissao__ativa=True
        ).values_list('permissao__codigo', flat=True)
    )

    permissoes_individuais = FuncionarioPermissao.objects.filter(
        funcionario=funcionario,
        permissao__ativa=True
    ).select_related('permissao')

    for permissao_individual in permissoes_individuais:
        codigo = permissao_individual.permissao.codigo

        if permissao_individual.permitido:
            permissoes_perfil.add(codigo)
        else:
            permissoes_perfil.discard(codigo)

    return sorted(list(permissoes_perfil))


def usuario_tem_permissao(user, codigo_permissao):
    if not user or not user.is_authenticated:
        return False

    if user.is_superuser:
        return True

    permissoes = obter_permissoes_usuario(user)

    return codigo_permissao in permissoes


def obter_funcionario_usuario(user):
    if not user or not user.is_authenticated:
        return None

    try:
        return user.funcionario
    except Funcionario.DoesNotExist:
        return None