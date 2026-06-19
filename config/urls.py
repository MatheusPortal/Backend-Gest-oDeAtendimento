from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/usuarios/', include('apps.usuarios.urls')),
    path('api/', include('apps.unidades.urls')),
    path('api/', include('apps.categorias.urls')),
    path('api/', include('apps.senhas.urls')),
    path('api/', include('apps.guiches.urls')),
    path('api/integracoes/', include('apps.integracoes.urls')),
    path('api/relatorios/', include('apps.relatorios.urls')),
    path('api/configuracoes/', include('apps.configuracoes.urls')),
]