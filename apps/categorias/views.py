from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.categorias.models import CategoriaSenha, SubcategoriaSenha
from apps.categorias.serializers import CategoriaSenhaSerializer, SubcategoriaSenhaSerializer
from apps.usuarios.permissions import PermissaoPorAcao


class CategoriaSenhaViewSet(viewsets.ModelViewSet):
    serializer_class = CategoriaSenhaSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'categoria.visualizar',
        'retrieve': 'categoria.visualizar',
        'create': 'categoria.criar',
        'update': 'categoria.editar',
        'partial_update': 'categoria.editar',
        'destroy': 'categoria.excluir',
    }

    def get_queryset(self):
        queryset = CategoriaSenha.objects.prefetch_related('subcategorias').all()

        ativa = self.request.query_params.get('ativa')
        pesquisar = self.request.query_params.get('pesquisar')

        if ativa == 'true':
            queryset = queryset.filter(ativa=True)

        if ativa == 'false':
            queryset = queryset.filter(ativa=False)

        if pesquisar:
            queryset = queryset.filter(
                Q(nome__icontains=pesquisar) |
                Q(codigo__icontains=pesquisar)
            )

        return queryset.order_by('nome')

    def destroy(self, request, *args, **kwargs):
        categoria = self.get_object()
        categoria.ativa = False
        categoria.save(update_fields=['ativa', 'atualizada_em'])

        return Response(
            {'detail': 'Categoria de senha desativada com sucesso.'},
            status=status.HTTP_200_OK
        )


class SubcategoriaSenhaViewSet(viewsets.ModelViewSet):
    serializer_class = SubcategoriaSenhaSerializer
    permission_classes = [IsAuthenticated, PermissaoPorAcao]

    permissoes_por_acao = {
        'list': 'subcategoria.visualizar',
        'retrieve': 'subcategoria.visualizar',
        'create': 'subcategoria.criar',
        'update': 'subcategoria.editar',
        'partial_update': 'subcategoria.editar',
        'destroy': 'subcategoria.excluir',
    }

    def get_queryset(self):
        queryset = SubcategoriaSenha.objects.select_related('categoria').all()

        ativa = self.request.query_params.get('ativa')
        categoria_id = self.request.query_params.get('categoria')
        pesquisar = self.request.query_params.get('pesquisar')

        if ativa == 'true':
            queryset = queryset.filter(ativa=True)

        if ativa == 'false':
            queryset = queryset.filter(ativa=False)

        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)

        if pesquisar:
            queryset = queryset.filter(
                Q(nome__icontains=pesquisar) |
                Q(codigo__icontains=pesquisar) |
                Q(categoria__nome__icontains=pesquisar)
            )

        return queryset.order_by('categoria__nome', 'nome')

    def destroy(self, request, *args, **kwargs):
        subcategoria = self.get_object()
        subcategoria.ativa = False
        subcategoria.save(update_fields=['ativa', 'atualizada_em'])

        return Response(
            {'detail': 'Subcategoria de senha desativada com sucesso.'},
            status=status.HTTP_200_OK
        )