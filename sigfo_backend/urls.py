from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from projetos.views import login_view, index_view, admin_view, handle_login, handle_logout, ProjetoViewSet

router = DefaultRouter()
router.register(r'projetos', ProjetoViewSet, basename='projeto')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', login_view, name='login'),
    path('app/', index_view, name='app'),
    path('painel/', admin_view, name='painel'),
    path('api/login/', handle_login, name='api_login'),
    path('api/logout/', handle_logout, name='api_logout'),

    # Adicione esta linha para as rotas da API de dados
    path('api/', include(router.urls)),
]