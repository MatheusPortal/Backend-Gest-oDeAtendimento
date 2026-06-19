from rest_framework import serializers

from apps.guiches.models import GuicheAtendimento


class GuicheAtendimentoSerializer(serializers.ModelSerializer):
    unidade_nome = serializers.CharField(source='unidade.nome', read_only=True)
    unidade_codigo = serializers.CharField(source='unidade.codigo', read_only=True)

    funcionario_nome = serializers.CharField(source='funcionario_atual.nome', read_only=True)
    funcionario_matricula = serializers.CharField(source='funcionario_atual.matricula', read_only=True)

    class Meta:
        model = GuicheAtendimento
        fields = [
            'id',
            'unidade',
            'unidade_nome',
            'unidade_codigo',
            'numero',
            'nome',
            'funcionario_atual',
            'funcionario_nome',
            'funcionario_matricula',
            'ativo',
            'disponivel',
            'criado_em',
            'atualizado_em'
        ]
        read_only_fields = [
            'id',
            'unidade_nome',
            'unidade_codigo',
            'funcionario_nome',
            'funcionario_matricula',
            'criado_em',
            'atualizado_em'
        ]

