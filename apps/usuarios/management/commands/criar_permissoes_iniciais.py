from django.core.management.base import BaseCommand
from apps.usuarios.models import (
    PerfilAcesso,
    PermissaoSistema,
    PerfilPermissao
)


class Command(BaseCommand):
    help = 'Cria os perfis e permissões iniciais do sistema.'

    def handle(self, *args, **options):
        perfis = [
            {
                'nome': PerfilAcesso.Perfis.SUPERVISOR,
                'descricao': 'Perfil responsável por acompanhar e gerenciar a operação da unidade.'
            },
            {
                'nome': PerfilAcesso.Perfis.COLABORADOR,
                'descricao': 'Perfil responsável pelo atendimento e operação da fila.'
            }
        ]

        for perfil in perfis:
            PerfilAcesso.objects.update_or_create(
                nome=perfil['nome'],
                defaults={
                    'descricao': perfil['descricao'],
                    'ativo': True
                }
            )

        permissoes = [
            {
                'codigo': 'integracao.visualizar',
                'nome': 'Visualizar integrações',
                'descricao': 'Permite visualizar integrações configuradas.',
                'modulo': PermissaoSistema.Modulos.INTEGRACAO
            },
            {
                'codigo': 'integracao.criar',
                'nome': 'Criar integrações',
                'descricao': 'Permite criar integrações externas.',
                'modulo': PermissaoSistema.Modulos.INTEGRACAO
            },
            {
                'codigo': 'integracao.editar',
                'nome': 'Editar integrações',
                'descricao': 'Permite editar integrações externas.',
                'modulo': PermissaoSistema.Modulos.INTEGRACAO
            },
            {
                'codigo': 'integracao.excluir',
                'nome': 'Excluir integrações',
                'descricao': 'Permite desativar integrações externas.',
                'modulo': PermissaoSistema.Modulos.INTEGRACAO
            },
            {
                'codigo': 'integracao.testar',
                'nome': 'Testar integrações',
                'descricao': 'Permite testar conexão com APIs externas.',
                'modulo': PermissaoSistema.Modulos.INTEGRACAO
            },
            {
                'codigo': 'integracao.enviar_ticket',
                'nome': 'Enviar ticket via integração',
                'descricao': 'Permite enviar tickets para APIs externas.',
                'modulo': PermissaoSistema.Modulos.INTEGRACAO
            },
            {
                'codigo': 'guiche.visualizar',
                'nome': 'Visualizar guichês',
                'descricao': 'Permite visualizar guichês de atendimento.',
                'modulo': PermissaoSistema.Modulos.GUICHE
            },
            {
                'codigo': 'guiche.criar',
                'nome': 'Criar guichês',
                'descricao': 'Permite criar guichês de atendimento.',
                'modulo': PermissaoSistema.Modulos.GUICHE
            },
            {
                'codigo': 'guiche.editar',
                'nome': 'Editar guichês',
                'descricao': 'Permite editar guichês de atendimento.',
                'modulo': PermissaoSistema.Modulos.GUICHE
            },
            {
                'codigo': 'guiche.excluir',
                'nome': 'Excluir guichês',
                'descricao': 'Permite desativar guichês de atendimento.',
                'modulo': PermissaoSistema.Modulos.GUICHE
            },
            {
                'codigo': 'guiche.vincular',
                'nome': 'Vincular guichê',
                'descricao': 'Permite vincular o colaborador a um guichê.',
                'modulo': PermissaoSistema.Modulos.GUICHE
            },
            {
                'codigo': 'configuracao.visualizar',
                'nome': 'Visualizar configurações',
                'descricao': 'Permite visualizar configurações do sistema e das unidades.',
                'modulo': PermissaoSistema.Modulos.CONFIGURACAO
            },
            {
                'codigo': 'configuracao.editar',
                'nome': 'Editar configurações',
                'descricao': 'Permite editar configurações do sistema e das unidades.',
                'modulo': PermissaoSistema.Modulos.CONFIGURACAO
            },
            {
                'codigo': 'unidade.visualizar',
                'nome': 'Visualizar unidades de atendimento',
                'descricao': 'Permite visualizar unidades de atendimento.',
                'modulo': PermissaoSistema.Modulos.UNIDADE
            },
            {
                'codigo': 'unidade.criar',
                'nome': 'Criar unidade de atendimento',
                'descricao': 'Permite criar unidades de atendimento.',
                'modulo': PermissaoSistema.Modulos.UNIDADE
            },
            {
                'codigo': 'unidade.editar',
                'nome': 'Editar unidade de atendimento',
                'descricao': 'Permite editar unidades de atendimento.',
                'modulo': PermissaoSistema.Modulos.UNIDADE
            },
            {
                'codigo': 'unidade.excluir',
                'nome': 'Excluir unidade de atendimento',
                'descricao': 'Permite excluir ou desativar unidades de atendimento.',
                'modulo': PermissaoSistema.Modulos.UNIDADE
            },

            {
                'codigo': 'colaborador.visualizar',
                'nome': 'Visualizar colaboradores',
                'descricao': 'Permite visualizar colaboradores.',
                'modulo': PermissaoSistema.Modulos.COLABORADOR
            },
            {
                'codigo': 'colaborador.criar',
                'nome': 'Criar colaborador',
                'descricao': 'Permite criar colaboradores.',
                'modulo': PermissaoSistema.Modulos.COLABORADOR
            },
            {
                'codigo': 'colaborador.editar',
                'nome': 'Editar colaborador',
                'descricao': 'Permite editar colaboradores.',
                'modulo': PermissaoSistema.Modulos.COLABORADOR
            },
            {
                'codigo': 'colaborador.excluir',
                'nome': 'Excluir colaborador',
                'descricao': 'Permite excluir ou desativar colaboradores.',
                'modulo': PermissaoSistema.Modulos.COLABORADOR
            },

            {
                'codigo': 'categoria.visualizar',
                'nome': 'Visualizar categorias de senha',
                'descricao': 'Permite visualizar categorias de senha.',
                'modulo': PermissaoSistema.Modulos.CATEGORIA
            },
            {
                'codigo': 'categoria.criar',
                'nome': 'Criar categoria de senha',
                'descricao': 'Permite criar categorias de senha.',
                'modulo': PermissaoSistema.Modulos.CATEGORIA
            },
            {
                'codigo': 'categoria.editar',
                'nome': 'Editar categoria de senha',
                'descricao': 'Permite editar categorias de senha.',
                'modulo': PermissaoSistema.Modulos.CATEGORIA
            },
            {
                'codigo': 'categoria.excluir',
                'nome': 'Excluir categoria de senha',
                'descricao': 'Permite excluir ou desativar categorias de senha.',
                'modulo': PermissaoSistema.Modulos.CATEGORIA
            },

            {
                'codigo': 'subcategoria.visualizar',
                'nome': 'Visualizar subcategorias de senha',
                'descricao': 'Permite visualizar subcategorias de senha.',
                'modulo': PermissaoSistema.Modulos.SUBCATEGORIA
            },
            {
                'codigo': 'subcategoria.criar',
                'nome': 'Criar subcategoria de senha',
                'descricao': 'Permite criar subcategorias de senha.',
                'modulo': PermissaoSistema.Modulos.SUBCATEGORIA
            },
            {
                'codigo': 'subcategoria.editar',
                'nome': 'Editar subcategoria de senha',
                'descricao': 'Permite editar subcategorias de senha.',
                'modulo': PermissaoSistema.Modulos.SUBCATEGORIA
            },
            {
                'codigo': 'subcategoria.excluir',
                'nome': 'Excluir subcategoria de senha',
                'descricao': 'Permite excluir ou desativar subcategorias de senha.',
                'modulo': PermissaoSistema.Modulos.SUBCATEGORIA
            },

            {
                'codigo': 'senha.visualizar_fila',
                'nome': 'Visualizar fila de senhas',
                'descricao': 'Permite visualizar a fila de senhas.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },
            {
                'codigo': 'senha.chamar',
                'nome': 'Chamar senha',
                'descricao': 'Permite chamar a próxima senha da fila.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },
            {
                'codigo': 'senha.pular',
                'nome': 'Pular senha',
                'descricao': 'Permite pular uma senha chamada.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },
            {
                'codigo': 'senha.cancelar',
                'nome': 'Cancelar senha',
                'descricao': 'Permite cancelar uma senha.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },
            {
                'codigo': 'senha.excluir_individual',
                'nome': 'Excluir senha individual',
                'descricao': 'Permite excluir uma senha específica da fila.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },
            {
                'codigo': 'senha.excluir_todas',
                'nome': 'Excluir todas as senhas',
                'descricao': 'Permite excluir todas as senhas pendentes.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },
            {
                'codigo': 'senha.excluir_por_categoria',
                'nome': 'Excluir senhas por categoria',
                'descricao': 'Permite excluir senhas pendentes filtrando por categoria.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },
            {
                'codigo': 'senha.retornar_pulada',
                'nome': 'Retornar senha pulada',
                'descricao': 'Permite retornar uma senha pulada para a fila, respeitando o limite de 15 minutos.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },
            {
                'codigo': 'senha.redirecionar_colaborador',
                'nome': 'Redirecionar senha para colaborador',
                'descricao': 'Permite redirecionar uma senha para outro colaborador disponível.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },
            {
                'codigo': 'senha.redirecionar_fila',
                'nome': 'Redirecionar senha para fila',
                'descricao': 'Permite devolver uma senha para a fila novamente.',
                'modulo': PermissaoSistema.Modulos.SENHA
            },

            {
                'codigo': 'atendimento.iniciar',
                'nome': 'Iniciar atendimento',
                'descricao': 'Permite iniciar o atendimento de uma senha.',
                'modulo': PermissaoSistema.Modulos.ATENDIMENTO
            },
            {
                'codigo': 'atendimento.finalizar',
                'nome': 'Finalizar atendimento',
                'descricao': 'Permite finalizar o atendimento de uma senha.',
                'modulo': PermissaoSistema.Modulos.ATENDIMENTO
            },
            {
                'codigo': 'atendimento.redirecionar',
                'nome': 'Redirecionar atendimento',
                'descricao': 'Permite redirecionar um atendimento para outro setor ou colaborador.',
                'modulo': PermissaoSistema.Modulos.ATENDIMENTO
            },

            {
                'codigo': 'relatorio.visualizar',
                'nome': 'Visualizar relatórios',
                'descricao': 'Permite visualizar relatórios de atendimento.',
                'modulo': PermissaoSistema.Modulos.RELATORIO
            },
            {
                'codigo': 'permissao.visualizar',
                'nome': 'Visualizar permissões',
                'descricao': 'Permite visualizar permissões do sistema.',
                'modulo': PermissaoSistema.Modulos.PERMISSAO
            },
            {
                'codigo': 'permissao.atribuir_supervisor',
                'nome': 'Atribuir permissões a supervisores',
                'descricao': 'Permite atribuir permissões a supervisores.',
                'modulo': PermissaoSistema.Modulos.PERMISSAO
            },
            {
                'codigo': 'permissao.atribuir_colaborador',
                'nome': 'Atribuir permissões a colaboradores',
                'descricao': 'Permite atribuir permissões a colaboradores.',
                'modulo': PermissaoSistema.Modulos.PERMISSAO
            }
        ]

        permissoes_criadas = {}

        for permissao in permissoes:
            obj, created = PermissaoSistema.objects.update_or_create(
                codigo=permissao['codigo'],
                defaults={
                    'nome': permissao['nome'],
                    'descricao': permissao['descricao'],
                    'modulo': permissao['modulo'],
                    'ativa': True
                }
            )

            permissoes_criadas[permissao['codigo']] = obj

            if created:
                self.stdout.write(self.style.SUCCESS(f'Permissão criada: {obj.codigo}'))
            else:
                self.stdout.write(self.style.WARNING(f'Permissão atualizada: {obj.codigo}'))

        supervisor = PerfilAcesso.objects.get(nome=PerfilAcesso.Perfis.SUPERVISOR)
        colaborador = PerfilAcesso.objects.get(nome=PerfilAcesso.Perfis.COLABORADOR)

        permissoes_supervisor = [
            'unidade.visualizar',
            'unidade.criar',
            'unidade.editar',
            'unidade.excluir',

            'colaborador.visualizar',
            'colaborador.criar',
            'colaborador.editar',
            'colaborador.excluir',

            'categoria.visualizar',
            'categoria.criar',
            'categoria.editar',
            'categoria.excluir',

            'subcategoria.visualizar',
            'subcategoria.criar',
            'subcategoria.editar',
            'subcategoria.excluir',

            'senha.visualizar_fila',
            'senha.chamar',
            'senha.pular',
            'senha.cancelar',
            'senha.excluir_individual',
            'senha.excluir_todas',
            'senha.excluir_por_categoria',
            'senha.retornar_pulada',
            'senha.redirecionar_colaborador',
            'senha.redirecionar_fila',

            'atendimento.iniciar',
            'atendimento.finalizar',
            'atendimento.redirecionar',

            'relatorio.visualizar',
            'permissao.visualizar',
            'permissao.atribuir_colaborador',

            'configuracao.visualizar',
            'configuracao.editar',

            'guiche.visualizar',
            'guiche.criar',
            'guiche.editar',
            'guiche.excluir',
            'guiche.vincular',
            'integracao.visualizar',
        ]

        permissoes_colaborador = [
            'senha.visualizar_fila',
            'senha.chamar',
            'senha.pular',

            'atendimento.iniciar',
            'atendimento.finalizar',
            'configuracao.visualizar',
            'guiche.visualizar',
            'guiche.vincular',
        ]

        self.criar_vinculos(supervisor, permissoes_supervisor, permissoes_criadas)
        self.criar_vinculos(colaborador, permissoes_colaborador, permissoes_criadas)

        self.stdout.write(self.style.SUCCESS('Perfis e permissões iniciais criados com sucesso.'))

    def criar_vinculos(self, perfil, codigos_permissoes, permissoes_criadas):
        for codigo in codigos_permissoes:
            permissao = permissoes_criadas.get(codigo)

            if permissao:
                PerfilPermissao.objects.get_or_create(
                    perfil=perfil,
                    permissao=permissao
                )