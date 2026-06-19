from rest_framework.routers import DefaultRouter
from apps.unidades.views import UnidadeAtendimentoViewSet


router = DefaultRouter()
router.register(r'unidades', UnidadeAtendimentoViewSet, basename='unidades')


urlpatterns = router.urls