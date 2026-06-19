from rest_framework import serializers
from apps.unidades.models import UnidadeAtendimento


class UnidadeAtendimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnidadeAtendimento
        fields = [
            'id',
            'nome',
            'codigo',
            'endereco',
            'ativa',
            'criada_em',
            'atualizada_em'
        ]
        read_only_fields = [
            'id',
            'criada_em',
            'atualizada_em'
        ]