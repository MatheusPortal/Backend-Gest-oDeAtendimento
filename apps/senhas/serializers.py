from rest_framework import serializers

from apps.senhas.models import PrioridadeSenha, Senha
from apps.categorias.models import CategoriaSenha
from apps.unidades.models import UnidadeAtendimento
from apps.senhas.services.gerador_senha import gerar_senha


class PrioridadeSenhaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrioridadeSenha
        fields = [
            'id',
            'nome',
            'codigo',
            'peso',
            'cor',
            'descricao',
            'visivel_na_geracao',
            'ativo',
            'criado_em',
            'atualizado_em'
        ]
        read_only_fields = [
            'id',
            'criado_em',
            'atualizado_em'
        ]


class SenhaSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    categoria_codigo = serializers.CharField(source='categoria.codigo', read_only=True)

    prioridade_nome = serializers.CharField(source='prioridade.nome', read_only=True)
    prioridade_codigo = serializers.CharField(source='prioridade.codigo', read_only=True)
    prioridade_cor = serializers.CharField(source='prioridade.cor', read_only=True)

    unidade_nome = serializers.CharField(source='unidade.nome', read_only=True)
    unidade_codigo = serializers.CharField(source='unidade.codigo', read_only=True)

    status_nome = serializers.CharField(source='get_status_display', read_only=True)
    humor_nome = serializers.CharField(source='get_humor_display', read_only=True)

    ticket_impressao = serializers.SerializerMethodField()
    guiche_numero = serializers.CharField(source='guiche.numero', read_only=True)
    guiche_nome = serializers.CharField(source='guiche.nome', read_only=True)

    colaborador_redirecionou_nome = serializers.CharField(
        source='colaborador_redirecionou.nome',
        read_only=True
    )

    colaborador_destino_nome = serializers.CharField(
        source='colaborador_destino.nome',
        read_only=True
    )

    class Meta:
        model = Senha
        fields = [
            'id',
            'codigo',
            'cpf',

            'categoria',
            'categoria_nome',
            'categoria_codigo',

            'prioridade',
            'prioridade_nome',
            'prioridade_codigo',
            'prioridade_cor',

            'unidade',
            'unidade_nome',
            'unidade_codigo',

            'humor',
            'humor_nome',

            'status',
            'status_nome',

            'colaborador_atual',
            'colaborador_chamou',
            'colaborador_finalizou',

            'gerada_em',
            'chamada_em',
            'iniciada_em',
            'finalizada_em',
            'pulada_em',
            'cancelada_em',
            'redirecionada_em',
            'atualizada_em',

            'ticket_impressao',
            'colaborador_pulou',
            'colaborador_redirecionou',
            'colaborador_redirecionou_nome',
            'colaborador_destino',
            'colaborador_destino_nome',
            'motivo_redirecionamento',

            'guiche',
            'guiche_numero',
            'guiche_nome',
        ]
        read_only_fields = [
            'id',
            'codigo',
            'status',
            'colaborador_atual',
            'colaborador_chamou',
            'colaborador_finalizou',
            'gerada_em',
            'chamada_em',
            'iniciada_em',
            'finalizada_em',
            'pulada_em',
            'cancelada_em',
            'redirecionada_em',
            'atualizada_em',
            'ticket_impressao',
            'colaborador_pulou',
            'colaborador_redirecionou',
            'colaborador_redirecionou_nome',
            'colaborador_destino',
            'colaborador_destino_nome',
            'motivo_redirecionamento',
            'guiche',
            'guiche_numero',
            'guiche_nome',
        ]

    def get_ticket_impressao(self, obj):
        return {
            'codigo': obj.codigo,
            'categoria_prioridade': f'{obj.categoria.nome} - {obj.prioridade.nome}',
            'unidade': obj.unidade.nome,
            'data_geracao': obj.gerada_em.strftime('%d/%m/%Y %H:%M')
        }
    

class GerarSenhaSerializer(serializers.Serializer):
    cpf = serializers.CharField(max_length=14)

    categoria = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaSenha.objects.filter(ativa=True)
    )

    prioridade = serializers.PrimaryKeyRelatedField(
        queryset=PrioridadeSenha.objects.filter(
            ativo=True,
            visivel_na_geracao=True
        )
    )

    unidade = serializers.PrimaryKeyRelatedField(
        queryset=UnidadeAtendimento.objects.filter(ativa=True)
    )

    humor = serializers.ChoiceField(
        choices=Senha.Humor.choices,
        default=Senha.Humor.NEUTRO
    )

    def validate_cpf(self, value):
        cpf_limpo = ''.join(filter(str.isdigit, value))

        if len(cpf_limpo) != 11:
            raise serializers.ValidationError('CPF deve conter 11 números.')

        return value

    def create(self, validated_data):
        return gerar_senha(
            cpf=validated_data['cpf'],
            categoria=validated_data['categoria'],
            prioridade=validated_data['prioridade'],
            unidade=validated_data['unidade'],
            humor=validated_data.get('humor', Senha.Humor.NEUTRO)
        )
    

class PainelSenhaSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    categoria_codigo = serializers.CharField(source='categoria.codigo', read_only=True)

    prioridade_nome = serializers.CharField(source='prioridade.nome', read_only=True)
    prioridade_codigo = serializers.CharField(source='prioridade.codigo', read_only=True)
    prioridade_cor = serializers.CharField(source='prioridade.cor', read_only=True)

    unidade_nome = serializers.CharField(source='unidade.nome', read_only=True)
    status_nome = serializers.CharField(source='get_status_display', read_only=True)
    guiche_numero = serializers.CharField(source='guiche.numero', read_only=True)
    guiche_nome = serializers.CharField(source='guiche.nome', read_only=True)

    class Meta:
        model = Senha
        fields = [
            'id',
            'codigo',
            'categoria_nome',
            'categoria_codigo',
            'prioridade_nome',
            'prioridade_codigo',
            'prioridade_cor',
            'unidade_nome',
            'status',
            'status_nome',
            'gerada_em',
            'chamada_em'
            'guiche_numero',
            'guiche_nome',
        ]
    def get_guiche_numero(self, obj):
        if obj.guiche:
            return obj.guiche.numero

        return None

    def get_guiche_nome(self, obj):
        if obj.guiche:
            return obj.guiche.nome

        return None

class HistoricoSenhaSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    prioridade_nome = serializers.CharField(source='prioridade.nome', read_only=True)
    unidade_nome = serializers.CharField(source='unidade.nome', read_only=True)
    humor_nome = serializers.CharField(source='get_humor_display', read_only=True)
    status_nome = serializers.CharField(source='get_status_display', read_only=True)
    colaborador_chamou_nome = serializers.CharField(source='colaborador_chamou.nome', read_only=True)
    colaborador_finalizou_nome = serializers.CharField(source='colaborador_finalizou.nome', read_only=True)

    class Meta:
        model = Senha
        fields = [
            'id',
            'codigo',
            'cpf',
            'categoria_nome',
            'prioridade_nome',
            'unidade_nome',
            'humor',
            'humor_nome',
            'status',
            'status_nome',
            'colaborador_chamou_nome',
            'colaborador_finalizou_nome',
            'gerada_em',
            'chamada_em',
            'iniciada_em',
            'finalizada_em',
            'pulada_em',
            'cancelada_em',
            'redirecionada_em'
        ]




