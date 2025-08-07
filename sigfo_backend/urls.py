from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from projetos.views import (
    login_view, index_view, admin_view, lista_projetos_view,
    handle_login, handle_logout, ProjetoViewSet,
    import_pnfo_view, import_regional_view,
    get_notifications_view, dismiss_notification_view,
    export_all_data_xls
)

router = DefaultRouter()
router.register(r'projetos', ProjetoViewSet, basename='projeto')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas de Páginas
    path('', login_view, name='login'),
    path('app/', index_view, name='app'),
    path('painel/', admin_view, name='painel'),
    path('lista/', lista_projetos_view, name='lista_projetos'),
    
    # Rotas de API
    path('api/login/', handle_login, name='api_login'),
    path('api/logout/', handle_logout, name='api_logout'),
    path('api/export_all/', export_all_data_xls, name='export_all'),
    path('api/import_pnfo/', import_pnfo_view, name='import_pnfo'),
    path('api/import_regional/', import_regional_view, name='import_regional'),
    path('api/notifications/', get_notifications_view, name='get_notifications'),
    path('api/notifications/dismiss/', dismiss_notification_view, name='dismiss_notification'),
    
    # Rota principal da API de dados
    path('api/', include(router.urls)),
]
