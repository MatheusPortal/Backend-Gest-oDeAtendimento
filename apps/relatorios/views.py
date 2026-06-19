from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from apps.senhas.models import Senha
from apps.usuarios.services.permissoes import usuario_tem_permissao
from django.db.models import Count, Avg, F, Q, ExpressionWrapper, DurationField
from apps.atendimentos.models import Atendimento
from apps.usuarios.models import Funcionario


def formatar_duracao(valor):
    if not valor:
        return None

    total_segundos = int(valor.total_seconds())

    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    segundos = total_segundos % 60

    return f'{horas:02d}:{minutos:02d}:{segundos:02d}'


class RelatorioGeralSenhasView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser and not usuario_tem_permissao(request.user, 'relatorio.visualizar'):
            raise PermissionDenied('Você não tem permissão para visualizar relatórios.')

        queryset = Senha.objects.select_related(
            'categoria',
            'prioridade',
            'unidade'
        ).all()

        unidade_id = request.query_params.get('unidade')
        categoria_id = request.query_params.get('categoria')
        prioridade_id = request.query_params.get('prioridade')
        status_senha = request.query_params.get('status')
        humor = request.query_params.get('humor')
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')

        if unidade_id:
            queryset = queryset.filter(unidade_id=unidade_id)

        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        if prioridade_id:
            queryset = queryset.filter(prioridade_id=prioridade_id)

        if status_senha:
            queryset = queryset.filter(status=status_senha)

        if humor:
            queryset = queryset.filter(humor=humor)

        if data_inicio:
            queryset = queryset.filter(gerada_em__date__gte=data_inicio)

        if data_fim:
            queryset = queryset.filter(gerada_em__date__lte=data_fim)

        total_geradas = queryset.count()

        resumo = {
            'total_geradas': total_geradas,
            'total_aguardando': queryset.filter(status=Senha.Status.AGUARDANDO).count(),
            'total_chamadas': queryset.filter(status=Senha.Status.CHAMADA).count(),
            'total_em_atendimento': queryset.filter(status=Senha.Status.EM_ATENDIMENTO).count(),
            'total_puladas': queryset.filter(status=Senha.Status.PULADA).count(),
            'total_finalizadas': queryset.filter(status=Senha.Status.FINALIZADA).count(),
            'total_canceladas': queryset.filter(status=Senha.Status.CANCELADA).count(),
            'total_redirecionadas': queryset.filter(status=Senha.Status.REDIRECIONADA).count(),
        }

        status_choices = dict(Senha.Status.choices)
        humor_choices = dict(Senha.Humor.choices)

        por_status = []
        for item in queryset.values('status').annotate(total=Count('id')).order_by('status'):
            por_status.append({
                'status': item['status'],
                'status_nome': status_choices.get(item['status'], item['status']),
                'total': item['total']
            })

        por_categoria = list(
            queryset.values(
                'categoria_id',
                'categoria__nome',
                'categoria__codigo'
            )
            .annotate(total=Count('id'))
            .order_by('-total', 'categoria__nome')
        )

        por_prioridade = list(
            queryset.values(
                'prioridade_id',
                'prioridade__nome',
                'prioridade__codigo',
                'prioridade__cor'
            )
            .annotate(total=Count('id'))
            .order_by('-total', 'prioridade__nome')
        )

        por_humor = []
        for item in queryset.values('humor').annotate(total=Count('id')).order_by('-total'):
            por_humor.append({
                'humor': item['humor'],
                'humor_nome': humor_choices.get(item['humor'], item['humor']),
                'total': item['total']
            })

        por_unidade = list(
            queryset.values(
                'unidade_id',
                'unidade__nome',
                'unidade__codigo'
            )
            .annotate(total=Count('id'))
            .order_by('-total', 'unidade__nome')
        )

        tempo_espera = queryset.filter(
            chamada_em__isnull=False
        ).annotate(
            tempo=ExpressionWrapper(
                F('chamada_em') - F('gerada_em'),
                output_field=DurationField()
            )
        ).aggregate(media=Avg('tempo'))['media']

        tempo_atendimento = queryset.filter(
            iniciada_em__isnull=False,
            finalizada_em__isnull=False
        ).annotate(
            tempo=ExpressionWrapper(
                F('finalizada_em') - F('iniciada_em'),
                output_field=DurationField()
            )
        ).aggregate(media=Avg('tempo'))['media']

        tempo_total = queryset.filter(
            finalizada_em__isnull=False
        ).annotate(
            tempo=ExpressionWrapper(
                F('finalizada_em') - F('gerada_em'),
                output_field=DurationField()
            )
        ).aggregate(media=Avg('tempo'))['media']

        tempos_medios = {
            'tempo_medio_espera': formatar_duracao(tempo_espera),
            'tempo_medio_atendimento': formatar_duracao(tempo_atendimento),
            'tempo_medio_total': formatar_duracao(tempo_total),
        }

        return Response({
            'filtros_aplicados': {
                'unidade': unidade_id,
                'categoria': categoria_id,
                'prioridade': prioridade_id,
                'status': status_senha,
                'humor': humor,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
            },
            'resumo': resumo,
            'tempos_medios': tempos_medios,
            'por_status': por_status,
            'por_categoria': por_categoria,
            'por_prioridade': por_prioridade,
            'por_humor': por_humor,
            'por_unidade': por_unidade,
        })
    

class RelatorioAtendimentosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser and not usuario_tem_permissao(request.user, 'relatorio.visualizar'):
            raise PermissionDenied('Você não tem permissão para visualizar relatórios.')

        queryset = Atendimento.objects.select_related(
            'senha',
            'atendente',
            'unidade',
            'categoria',
            'subcategoria'
        ).all()

        unidade_id = request.query_params.get('unidade')
        atendente_id = request.query_params.get('atendente')
        categoria_id = request.query_params.get('categoria')
        subcategoria_id = request.query_params.get('subcategoria')
        matricula = request.query_params.get('matricula')
        cpf = request.query_params.get('cpf')
        email = request.query_params.get('email')
        status_atendimento = request.query_params.get('status')
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        pesquisar = request.query_params.get('pesquisar')

        try:
            limite = int(request.query_params.get('limite', 100))
        except ValueError:
            limite = 100

        if limite > 500:
            limite = 500

        if unidade_id:
            queryset = queryset.filter(unidade_id=unidade_id)

        if atendente_id:
            queryset = queryset.filter(atendente_id=atendente_id)

        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        if subcategoria_id:
            queryset = queryset.filter(subcategoria_id=subcategoria_id)

        if matricula:
            queryset = queryset.filter(matricula__icontains=matricula)

        if cpf:
            queryset = queryset.filter(cpf__icontains=cpf)

        if email:
            queryset = queryset.filter(email__icontains=email)

        if status_atendimento:
            queryset = queryset.filter(status=status_atendimento)

        if data_inicio:
            queryset = queryset.filter(finalizado_em__date__gte=data_inicio)

        if data_fim:
            queryset = queryset.filter(finalizado_em__date__lte=data_fim)

        if pesquisar:
            queryset = queryset.filter(
                Q(senha__codigo__icontains=pesquisar) |
                Q(titulo__icontains=pesquisar) |
                Q(matricula__icontains=pesquisar) |
                Q(cpf__icontains=pesquisar) |
                Q(email__icontains=pesquisar) |
                Q(descricao__icontains=pesquisar) |
                Q(categoria__nome__icontains=pesquisar) |
                Q(subcategoria__nome__icontains=pesquisar) |
                Q(unidade__nome__icontains=pesquisar) |
                Q(atendente__nome__icontains=pesquisar)
            )

        total_atendimentos = queryset.count()

        status_choices = dict(Atendimento.Status.choices)

        por_status = []
        for item in queryset.values('status').annotate(total=Count('id')).order_by('status'):
            por_status.append({
                'status': item['status'],
                'status_nome': status_choices.get(item['status'], item['status']),
                'total': item['total']
            })

        por_categoria = list(
            queryset.values(
                'categoria_id',
                'categoria__nome',
                'categoria__codigo'
            )
            .annotate(total=Count('id'))
            .order_by('-total', 'categoria__nome')
        )

        por_subcategoria = list(
            queryset.values(
                'subcategoria_id',
                'subcategoria__nome',
                'categoria__nome'
            )
            .annotate(total=Count('id'))
            .order_by('-total', 'subcategoria__nome')
        )

        por_unidade = list(
            queryset.values(
                'unidade_id',
                'unidade__nome',
                'unidade__codigo'
            )
            .annotate(total=Count('id'))
            .order_by('-total', 'unidade__nome')
        )

        por_atendente = list(
            queryset.values(
                'atendente_id',
                'atendente__nome',
                'atendente__matricula'
            )
            .annotate(total=Count('id'))
            .order_by('-total', 'atendente__nome')
        )

        tempo_atendimento = queryset.filter(
            senha__iniciada_em__isnull=False,
            senha__finalizada_em__isnull=False
        ).annotate(
            tempo=ExpressionWrapper(
                F('senha__finalizada_em') - F('senha__iniciada_em'),
                output_field=DurationField()
            )
        ).aggregate(media=Avg('tempo'))['media']

        tempo_total = queryset.filter(
            senha__gerada_em__isnull=False,
            senha__finalizada_em__isnull=False
        ).annotate(
            tempo=ExpressionWrapper(
                F('senha__finalizada_em') - F('senha__gerada_em'),
                output_field=DurationField()
            )
        ).aggregate(media=Avg('tempo'))['media']

        atendimentos = []

        for atendimento in queryset.order_by('-finalizado_em')[:limite]:
            atendimentos.append({
                'id': atendimento.id,
                'senha': {
                    'id': atendimento.senha.id,
                    'codigo': atendimento.senha.codigo,
                    'status': atendimento.senha.status,
                    'status_nome': atendimento.senha.get_status_display()
                },
                'titulo': atendimento.titulo,
                'matricula': atendimento.matricula,
                'cpf': atendimento.cpf,
                'email': atendimento.email,
                'descricao': atendimento.descricao,
                'categoria': {
                    'id': atendimento.categoria.id,
                    'nome': atendimento.categoria.nome,
                    'codigo': atendimento.categoria.codigo
                },
                'subcategoria': {
                    'id': atendimento.subcategoria.id,
                    'nome': atendimento.subcategoria.nome,
                    'codigo': atendimento.subcategoria.codigo
                },
                'unidade': {
                    'id': atendimento.unidade.id,
                    'nome': atendimento.unidade.nome,
                    'codigo': atendimento.unidade.codigo
                },
                'atendente': {
                    'id': atendimento.atendente.id,
                    'nome': atendimento.atendente.nome,
                    'matricula': atendimento.atendente.matricula
                } if atendimento.atendente else None,
                'status': atendimento.status,
                'status_nome': atendimento.get_status_display(),
                'criado_em': atendimento.criado_em,
                'finalizado_em': atendimento.finalizado_em
            })

        return Response({
            'filtros_aplicados': {
                'unidade': unidade_id,
                'atendente': atendente_id,
                'categoria': categoria_id,
                'subcategoria': subcategoria_id,
                'matricula': matricula,
                'cpf': cpf,
                'email': email,
                'status': status_atendimento,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'pesquisar': pesquisar,
                'limite': limite
            },
            'resumo': {
                'total_atendimentos': total_atendimentos,
                'tempo_medio_atendimento': formatar_duracao(tempo_atendimento),
                'tempo_medio_total': formatar_duracao(tempo_total)
            },
            'por_status': por_status,
            'por_categoria': por_categoria,
            'por_subcategoria': por_subcategoria,
            'por_unidade': por_unidade,
            'por_atendente': por_atendente,
            'atendimentos': atendimentos
        })


class RelatorioColaboradoresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser and not usuario_tem_permissao(request.user, 'relatorio.visualizar'):
            raise PermissionDenied('Você não tem permissão para visualizar relatórios.')

        unidade_id = request.query_params.get('unidade')
        colaborador_id = request.query_params.get('colaborador')
        data_inicio = request.query_params.get('data_inicio')
        data_fim = request.query_params.get('data_fim')
        pesquisar = request.query_params.get('pesquisar')

        colaboradores = Funcionario.objects.select_related(
            'user',
            'perfil',
            'unidade'
        ).filter(
            ativo=True
        )

        if unidade_id:
            colaboradores = colaboradores.filter(unidade_id=unidade_id)

        if colaborador_id:
            colaboradores = colaboradores.filter(id=colaborador_id)

        if pesquisar:
            colaboradores = colaboradores.filter(
                Q(nome__icontains=pesquisar) |
                Q(matricula__icontains=pesquisar) |
                Q(user__username__icontains=pesquisar) |
                Q(user__email__icontains=pesquisar)
            )

        resultado = []

        for colaborador in colaboradores.order_by('nome'):
            senhas_chamadas = Senha.objects.filter(
                colaborador_chamou=colaborador
            )

            senhas_finalizadas = Senha.objects.filter(
                colaborador_finalizou=colaborador
            )

            senhas_puladas = Senha.objects.filter(
                colaborador_pulou=colaborador
            )

            if data_inicio:
                senhas_chamadas = senhas_chamadas.filter(chamada_em__date__gte=data_inicio)
                senhas_finalizadas = senhas_finalizadas.filter(finalizada_em__date__gte=data_inicio)
                senhas_puladas = senhas_puladas.filter(pulada_em__date__gte=data_inicio)

            if data_fim:
                senhas_chamadas = senhas_chamadas.filter(chamada_em__date__lte=data_fim)
                senhas_finalizadas = senhas_finalizadas.filter(finalizada_em__date__lte=data_fim)
                senhas_puladas = senhas_puladas.filter(pulada_em__date__lte=data_fim)

            tempo_espera = senhas_chamadas.filter(
                chamada_em__isnull=False
            ).annotate(
                tempo=ExpressionWrapper(
                    F('chamada_em') - F('gerada_em'),
                    output_field=DurationField()
                )
            ).aggregate(media=Avg('tempo'))['media']

            tempo_atendimento = senhas_finalizadas.filter(
                iniciada_em__isnull=False,
                finalizada_em__isnull=False
            ).annotate(
                tempo=ExpressionWrapper(
                    F('finalizada_em') - F('iniciada_em'),
                    output_field=DurationField()
                )
            ).aggregate(media=Avg('tempo'))['media']

            resultado.append({
                'colaborador': {
                    'id': colaborador.id,
                    'nome': colaborador.nome,
                    'matricula': colaborador.matricula,
                    'username': colaborador.user.username,
                    'email': colaborador.user.email,
                    'perfil': colaborador.perfil.nome,
                    'perfil_nome': colaborador.perfil.get_nome_display(),
                },
                'unidade': {
                    'id': colaborador.unidade.id,
                    'nome': colaborador.unidade.nome,
                    'codigo': colaborador.unidade.codigo
                } if colaborador.unidade else None,
                'produtividade': {
                    'senhas_chamadas': senhas_chamadas.count(),
                    'atendimentos_finalizados': senhas_finalizadas.count(),
                    'senhas_puladas': senhas_puladas.count(),
                    'tempo_medio_espera': formatar_duracao(tempo_espera),
                    'tempo_medio_atendimento': formatar_duracao(tempo_atendimento)
                }
            })

        total_chamadas = sum(item['produtividade']['senhas_chamadas'] for item in resultado)
        total_finalizadas = sum(item['produtividade']['atendimentos_finalizados'] for item in resultado)
        total_puladas = sum(item['produtividade']['senhas_puladas'] for item in resultado)

        return Response({
            'filtros_aplicados': {
                'unidade': unidade_id,
                'colaborador': colaborador_id,
                'data_inicio': data_inicio,
                'data_fim': data_fim,
                'pesquisar': pesquisar
            },
            'resumo': {
                'total_colaboradores': len(resultado),
                'total_senhas_chamadas': total_chamadas,
                'total_atendimentos_finalizados': total_finalizadas,
                'total_senhas_puladas': total_puladas
            },
            'colaboradores': resultado
        })


