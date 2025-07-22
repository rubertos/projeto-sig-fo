from django.contrib import admin
from django.urls import path, include
from projetos.views import index

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('projetos.urls')),
    path('', index, name='index'),
]