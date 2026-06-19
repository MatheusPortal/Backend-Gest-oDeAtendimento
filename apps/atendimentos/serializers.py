from rest_framework import serializers

from apps.atendimentos.models import Atendimento
from apps.categorias.models import CategoriaSenha, SubcategoriaSenha


class AtendimentoSerializer(serializers.ModelSerializer):
    senha_codigo = serializers.CharField(source='senha.codigo', read_only=True)
    atendente_nome = serializers.CharField(source='atendente.nome', read_only=True)
    unidade_nome = serializers.CharField(source='unidade.nome', read_only=True)
    categoria_nome = serializers.CharField(source='categoria.nome', read_only=True)
    subcategoria_nome = serializers.CharField(source='subcategoria.nome', read_only=True)
    status_nome = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Atendimento
        fields = [
            'id',
            'senha',
            'senha_codigo',

            'atendente',
            'atendente_nome',

            'unidade',
            'unidade_nome',

            'categoria',
            'categoria_nome',

            'subcategoria',
            'subcategoria_nome',

            'titulo',
            'matricula',
            'cpf',
            'email',
            'descricao',

            'status',
            'status_nome',

            'criado_em',
            'finalizado_em',
            'atualizado_em'
        ]


class HubspotFinalizacaoSerializer(serializers.Serializer):
    abrir_chamado_interno = serializers.BooleanField(required=False, default=False)
    config_chamado = serializers.IntegerField(required=False, allow_null=True)
    campos_front = serializers.JSONField(required=False)


class FinalizarAtendimentoSerializer(serializers.Serializer):
    titulo = serializers.CharField(max_length=180)
    matricula = serializers.CharField(max_length=50)
    cpf = serializers.CharField(max_length=14)
    email = serializers.EmailField()
    descricao = serializers.CharField()
    hubspot = HubspotFinalizacaoSerializer(required=False)

    categoria = serializers.PrimaryKeyRelatedField(
        queryset=CategoriaSenha.objects.filter(ativa=True)
    )

    subcategoria = serializers.PrimaryKeyRelatedField(
        queryset=SubcategoriaSenha.objects.filter(ativa=True)
    )

    def validate_cpf(self, value):
        cpf_limpo = ''.join(filter(str.isdigit, value))

        if len(cpf_limpo) != 11:
            raise serializers.ValidationError('CPF deve conter 11 números.')

        return value

    def validate(self, attrs):
        categoria = attrs.get('categoria')
        subcategoria = attrs.get('subcategoria')

        if subcategoria.categoria_id != categoria.id:
            raise serializers.ValidationError({
                'subcategoria': 'A subcategoria selecionada não pertence à categoria informada.'
            })

        return attrs