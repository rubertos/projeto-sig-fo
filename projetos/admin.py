from django.contrib import admin
from .models import Projeto, PnfoGeral

admin.site.register(Projeto)
admin.site.register(PnfoGeral) #linha adicionada para consulta do PNFO
