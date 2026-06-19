from rest_framework.routers import DefaultRouter
from apps.categorias.views import CategoriaSenhaViewSet, SubcategoriaSenhaViewSet


router = DefaultRouter()
router.register(r'categorias', CategoriaSenhaViewSet, basename='categorias')
router.register(r'subcategorias', SubcategoriaSenhaViewSet, basename='subcategorias')


urlpatterns = router.urls