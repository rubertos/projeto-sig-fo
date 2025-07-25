# projetos/views.py

# --- Imports existentes e novos ---
import json
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from .models import Projeto
from .serializers import ProjetoSerializer

# --- Suas views existentes (MANTENHA TODAS) ---
def login_view(request):
    return render(request, 'login.html')

@login_required
def index_view(request):
    return render(request, 'index.html')

@login_required
def admin_view(request):
    return render(request, 'admin.html')

@csrf_exempt
def handle_login(request):
    # ... (seu código de login aqui, está perfeito)
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            user_data = {'username': user.username, 'is_staff': user.is_staff}
            regional_group = user.groups.first()
            user_data['regional'] = regional_group.name if regional_group else 'Admin'
            return JsonResponse({'status': 'success', 'user': user_data})
        else:
            return JsonResponse({'status': 'error', 'message': 'Utilizador ou senha inválidos.'}, status=401)
    return JsonResponse({'status': 'error', 'message': 'Método não permitido.'}, status=405)

def handle_logout(request):
    logout(request)
    return JsonResponse({'status': 'success'})

# --- API de Projetos (ADICIONE ESTA PARTE) ---
class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer
    permission_classes = [permissions.IsAuthenticated] # Protege a API
    lookup_field = 'Identificador'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff: # Admin vê tudo
            return Projeto.objects.all()
        
        # Utilizador regional vê apenas os projetos do seu grupo
        regional_group = user.groups.first()
        if regional_group:
            return Projeto.objects.filter(Regional=regional_group.name)
        return Projeto.objects.none() # Se não estiver em nenhum grupo, não vê nada