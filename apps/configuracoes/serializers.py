from rest_framework import serializers

from apps.configuracoes.models import ConfiguracaoUnidade, PreferenciaFuncionario


class ConfiguracaoUnidadeSerializer(serializers.ModelSerializer):
    unidade_nome = serializers.CharField(source='unidade.nome', read_only=True)
    unidade_codigo = serializers.CharField(source='unidade.codigo', read_only=True)

    class Meta:
        model = ConfiguracaoUnidade
        fields = [
            'id',
            'unidade',
            'unidade_nome',
            'unidade_codigo',
            'cor_primaria',
            'cor_secundaria',
            'cor_fundo',
            'cor_texto',
            'som_chamada_url',
            'som_chamada_ativo',
            'quantidade_historico_painel',
            'quantidade_proximas_painel',
            'ativo',
            'criada_em',
            'atualizada_em'
        ]
        read_only_fields = [
            'id',
            'unidade_nome',
            'unidade_codigo',
            'criada_em',
            'atualizada_em'
        ]


class PreferenciaFuncionarioSerializer(serializers.ModelSerializer):
    funcionario_nome = serializers.CharField(source='funcionario.nome', read_only=True)
    funcionario_matricula = serializers.CharField(source='funcionario.matricula', read_only=True)

    class Meta:
        model = PreferenciaFuncionario
        fields = [
            'id',
            'funcionario',
            'funcionario_nome',
            'funcionario_matricula',
            'som_mudo',
            'cor_pagina',
            'criada_em',
            'atualizada_em'
        ]
        read_only_fields = [
            'id',
            'funcionario',
            'funcionario_nome',
            'funcionario_matricula',
            'criada_em',
            'atualizada_em'
        ]


