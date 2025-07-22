from rest_framework import viewsets
from .models import Projeto
from .serializers import ProjetoSerializer

class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer
    lookup_field = 'Identificador'
    
from django.shortcuts import render

def index(request):
    return render(request, 'sigfo_form_projetos.html')        