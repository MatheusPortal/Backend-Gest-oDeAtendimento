from rest_framework import serializers
from apps.usuarios.services.permissoes import obter_permissoes_usuario, obter_funcionario_usuario

from django.contrib.auth.models import User

from apps.usuarios.models import Funcionario, PerfilAcesso
from apps.unidades.models import UnidadeAtendimento

from apps.usuarios.models import (
    Funcionario,
    PerfilAcesso,
    PermissaoSistema,
    PerfilPermissao,
    FuncionarioPermissao
    
)


class UsuarioLogadoSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField(allow_blank=True)
    is_superuser = serializers.BooleanField()
    acesso_total = serializers.SerializerMethodField()
    funcionario = serializers.SerializerMethodField()
    permissoes = serializers.SerializerMethodField()

    def get_acesso_total(self, user):
        return user.is_superuser

    def get_funcionario(self, user):
        funcionario = obter_funcionario_usuario(user)

        if not funcionario:
            return None

        return {
            'id': funcionario.id,
            'nome': funcionario.nome,
            'matricula': funcionario.matricula,
            'perfil': funcionario.perfil.nome if funcionario.perfil else None,
            'perfil_nome': funcionario.perfil.get_nome_display() if funcionario.perfil else None,
            'unidade': {
                'id': funcionario.unidade.id,
                'nome': funcionario.unidade.nome,
                'codigo': funcionario.unidade.codigo
            } if funcionario.unidade else None,
            'ativo': funcionario.ativo
        }

    def get_permissoes(self, user):
        return obter_permissoes_usuario(user)




class FuncionarioSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True, allow_blank=True)

    perfil_nome = serializers.CharField(source='perfil.get_nome_display', read_only=True)

    unidade_nome = serializers.CharField(source='unidade.nome', read_only=True)
    unidade_codigo = serializers.CharField(source='unidade.codigo', read_only=True)

    class Meta:
        model = Funcionario
        fields = [
            'id',
            'user_id',
            'username',
            'email',
            'nome',
            'matricula',
            'perfil',
            'perfil_nome',
            'unidade',
            'unidade_nome',
            'unidade_codigo',
            'ativo',
            'criado_em',
            'atualizado_em'
        ]


class FuncionarioInputSerializer(serializers.Serializer):
    nome = serializers.CharField(max_length=150, required=False)
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(required=False, allow_blank=True, allow_null=True)
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)
    matricula = serializers.CharField(max_length=50, required=False)

    perfil = serializers.PrimaryKeyRelatedField(
        queryset=PerfilAcesso.objects.filter(ativo=True),
        required=False
    )

    unidade = serializers.PrimaryKeyRelatedField(
        queryset=UnidadeAtendimento.objects.filter(ativa=True),
        required=False,
        allow_null=True
    )

    ativo = serializers.BooleanField(required=False)

    def validate(self, attrs):
        criando = self.instance is None

        campos_obrigatorios = [
            'nome',
            'username',
            'password',
            'matricula',
            'perfil'
        ]

        if criando:
            for campo in campos_obrigatorios:
                if not attrs.get(campo):
                    raise serializers.ValidationError({
                        campo: 'Este campo é obrigatório.'
                    })

        username = attrs.get('username')
        matricula = attrs.get('matricula')

        if username:
            user_queryset = User.objects.filter(username=username)

            if not criando:
                user_queryset = user_queryset.exclude(id=self.instance.user.id)

            if user_queryset.exists():
                raise serializers.ValidationError({
                    'username': 'Já existe um usuário com este nome de usuário.'
                })

        if matricula:
            funcionario_queryset = Funcionario.objects.filter(matricula=matricula)

            if not criando:
                funcionario_queryset = funcionario_queryset.exclude(id=self.instance.id)

            if funcionario_queryset.exists():
                raise serializers.ValidationError({
                    'matricula': 'Já existe um funcionário com esta matrícula.'
                })

        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email') or '',
            password=validated_data['password']
        )

        funcionario = Funcionario.objects.create(
            user=user,
            nome=validated_data['nome'],
            matricula=validated_data['matricula'],
            perfil=validated_data['perfil'],
            unidade=validated_data.get('unidade'),
            ativo=validated_data.get('ativo', True)
        )

        return funcionario

    def update(self, instance, validated_data):
        user = instance.user

        if 'username' in validated_data:
            user.username = validated_data['username']

        if 'email' in validated_data:
            user.email = validated_data.get('email') or ''

        if validated_data.get('password'):
            user.set_password(validated_data['password'])

        if 'ativo' in validated_data:
            user.is_active = validated_data['ativo']
            instance.ativo = validated_data['ativo']

        user.save()

        if 'nome' in validated_data:
            instance.nome = validated_data['nome']

        if 'matricula' in validated_data:
            instance.matricula = validated_data['matricula']

        if 'perfil' in validated_data:
            instance.perfil = validated_data['perfil']

        if 'unidade' in validated_data:
            instance.unidade = validated_data['unidade']

        instance.save()

        return instance
    

class PerfilAcessoSerializer(serializers.ModelSerializer):
    nome_display = serializers.CharField(source='get_nome_display', read_only=True)

    class Meta:
        model = PerfilAcesso
        fields = [
            'id',
            'nome',
            'nome_display',
            'descricao',
            'ativo',
            'criado_em',
            'atualizado_em'
        ]


class PermissaoSistemaSerializer(serializers.ModelSerializer):
    modulo_nome = serializers.CharField(source='get_modulo_display', read_only=True)

    class Meta:
        model = PermissaoSistema
        fields = [
            'id',
            'codigo',
            'nome',
            'descricao',
            'modulo',
            'modulo_nome',
            'ativa',
            'criado_em',
            'atualizado_em'
        ]


class AtualizarPermissaoItemSerializer(serializers.Serializer):
    permissao = serializers.PrimaryKeyRelatedField(
        queryset=PermissaoSistema.objects.filter(ativa=True)
    )
    permitido = serializers.BooleanField()


class AtualizarPermissoesFuncionarioSerializer(serializers.Serializer):
    permissoes = AtualizarPermissaoItemSerializer(many=True)



