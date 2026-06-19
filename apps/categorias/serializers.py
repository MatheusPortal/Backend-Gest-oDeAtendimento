from rest_framework import serializers
from apps.categorias.models import CategoriaSenha, SubcategoriaSenha


class SubcategoriaSenhaSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)

    class Meta:
        model = SubcategoriaSenha
        fields = [
            'id',
            'categoria',
            'categoria_nome',
            'nome',
            'codigo',
            'descricao',
            'ativa',
            'criada_em',
            'atualizada_em'
        ]
        read_only_fields = [
            'id',
            'categoria_nome',
            'criada_em',
            'atualizada_em'
        ]


class CategoriaSenhaSerializer(serializers.ModelSerializer):
    subcategorias = SubcategoriaSenhaSerializer(many=True, read_only=True)

    class Meta:
        model = CategoriaSenha
        fields = [
            'id',
            'nome',
            'codigo',
            'descricao',
            'ativa',
            'subcategorias',
            'criada_em',
            'atualizada_em'
        ]
        read_only_fields = [
            'id',
            'subcategorias',
            'criada_em',
            'atualizada_em'
        ]