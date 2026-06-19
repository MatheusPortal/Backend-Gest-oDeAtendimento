from rest_framework.routers import DefaultRouter
from apps.senhas.views import PrioridadeSenhaViewSet, SenhaViewSet


router = DefaultRouter()
router.register(r'prioridades', PrioridadeSenhaViewSet, basename='prioridades')
router.register(r'senhas', SenhaViewSet, basename='senhas')


urlpatterns = router.urls