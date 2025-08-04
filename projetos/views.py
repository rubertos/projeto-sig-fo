# projetos/views.py

# --- Imports existentes e novos ---
import json
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from .models import Projeto, PnfoGeral
from .serializers import ProjetoSerializer
from django.db import IntegrityError

# --- Views de login e páginas (MANTENHA) ---
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

# --- View para Importação do PnFO (CORRIGIDA E MAIS ROBUSTA) ---
@csrf_exempt
@login_required
def import_pnfo_view(request):
    if not request.user.is_staff:
        return JsonResponse({'message': 'Acesso negado.'}, status=403)
    
    if request.method == 'POST':
        file = request.FILES.get('pnfo_file')
        if not file:
            return JsonResponse({'message': 'Nenhum ficheiro enviado.'}, status=400)
        
        try:
            # Tenta ler o ficheiro, primeiro como CSV, depois como Excel
            try:
                df = pd.read_csv(file)
            except Exception:
                file.seek(0) # Volta ao início do ficheiro
                df = pd.read_excel(file)

            novos_projetos_count = 0
            atualizados_count = 0

            # Limpa os nomes das colunas
            df.columns = df.columns.str.strip()

            # Renomeia as colunas para corresponderem aos campos do modelo
            df.rename(columns={
                'Estação BdRaf': 'Estacao_BdRaf',
                'Projeto CAPEX': 'Projeto_CAPEX',
                'Sub-Projeto CAPEX': 'Sub_Projeto_CAPEX',
                'SI CAPEX': 'SI_CAPEX',
                'Ano Implantação': 'Ano_Implantacao'
            }, inplace=True)

            # Converte colunas numéricas, transformando erros em Nulo (NaN)
            numeric_cols = ['COD_IBGE', 'Ano_Implantacao']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Substitui os NaN do pandas por None, que o Django entende
            df = df.where(pd.notna(df), None)
            
            for _, row in df.iterrows():
                identificador = row.get('Identificador')
                if not identificador:
                    continue
                
                pnfo_data = {
                    'Regional': row.get('Regional'),
                    'Municipio': row.get('Municipio'),
                    'Estacao_BdRaf': row.get('Estacao_BdRaf'),
                    'COD_IBGE': row.get('COD_IBGE'),
                    'Projeto_CAPEX': row.get('Projeto_CAPEX'),
                    'Sub_Projeto_CAPEX': row.get('Sub_Projeto_CAPEX'),
                    'SI_CAPEX': row.get('SI_CAPEX'),
                    'Ano_Implantacao': row.get('Ano_Implantacao'),
                }
                
                # Filtra os valores nulos para não sobrescrever dados existentes com "nada"
                pnfo_data_cleaned = {k: v for k, v in pnfo_data.items() if v is not None}
                
                PnfoGeral.objects.update_or_create(
                    Identificador=identificador,
                    defaults=pnfo_data_cleaned
                )

                if not Projeto.objects.filter(Identificador=identificador).exists():
                    Projeto.objects.create(Identificador=identificador, Regional=row.get('Regional'))
                    novos_projetos_count += 1
                else:
                    atualizados_count += 1
                    
            return JsonResponse({'message': f'{novos_projetos_count} projetos novos criados e {atualizados_count} referências atualizadas.'})

        except Exception as e:
            return JsonResponse({'message': f'Erro ao processar o ficheiro: {e}'}, status=500)
    
    return JsonResponse({'message': 'Método não permitido.'}, status=405)

# --- View para Exportação Compilada (MANTENHA) ---
@login_required
def export_all_data_xls(request):
    if not request.user.is_staff:
        return HttpResponse("Acesso negado.", status=403)
    
    pnfo_qs = PnfoGeral.objects.all().values()
    if not list(pnfo_qs):
        return HttpResponse("A base de dados de referência (PnFO) está vazia.")
    df_pnfo = pd.DataFrame(list(pnfo_qs))

    projetos_qs = Projeto.objects.all().values()
    df_projetos = pd.DataFrame(list(projetos_qs))

    if not df_projetos.empty:
        df_pnfo = df_pnfo.set_index('Identificador')
        df_projetos = df_projetos.set_index('Identificador')
        df_pnfo.update(df_projetos)
        df_final = df_pnfo.reset_index()
    else:
        df_final = df_pnfo

    colunas_finais = [
        'Identificador', 'Ano_Implantacao', 'Regional', 'Estacao_BdRaf', 'COD_IBGE', 
        'Municipio', 'Projeto_CAPEX', 'Sub_Projeto_CAPEX', 'SI_CAPEX', 
        'QUALIDADE_PREENCHIMENTO', 'CAPEX', 'Req_Gen_Plan', 'Req_Gen_Real', 
        'OS_WF', 'Km_Projeto_Executado', 'Projeto_Executivo_Plan', 
        'Projeto_Executivo_Real', 'Data_Protocolo_Real', 'Licenciamento_Plan', 
        'Licenciamento_Real', 'MOS_Plan', 'MOS_Real', 'Swap_Plan', 'Swap_Real', 
        'Km_Construido', 'Construcao_Total_Plan', 'Construcao_Parcial_Real', 
        'Construcao_Total_Real', 'RFI_Plan', 'RFI_Real', 'Entroncado_Plan', 
        'Entroncado_Real', 'Documentacao_Plan', 'Documentacao_Real', 
        'GP_Plan', 'GP_Real'
    ]
    
    for col in colunas_finais:
        if col not in df_final.columns:
            df_final[col] = None
    
    df_final = df_final[colunas_finais]

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="SIG_FO_Compilado.xlsx"'
    df_final.to_excel(response, index=False)
    return response

# --- Views de Notificação (MANTENHA) ---
@login_required
def get_notifications_view(request):
    user = request.user
    if user.is_staff: return JsonResponse([], safe=False)
    regional_group = user.groups.first()
    if not regional_group: return JsonResponse([], safe=False)
    novos_projetos = Projeto.objects.filter(Regional=regional_group.name, foi_notificado=False).values('Identificador')
    return JsonResponse(list(novos_projetos), safe=False)

@csrf_exempt
@login_required
def dismiss_notification_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        project_ids = data.get('project_ids', [])
        Projeto.objects.filter(Identificador__in=project_ids).update(foi_notificado=True)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def lista_projetos_view(request):
    return render(request, 'lista_projetos.html')

# --- API de Projetos (MANTENHA) ---
class ProjetoViewSet(viewsets.ModelViewSet):
    queryset = Projeto.objects.all()
    serializer_class = ProjetoSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'Identificador'

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Projeto.objects.all()
        
        regional_group = user.groups.first()
        if regional_group:
            return Projeto.objects.filter(Regional=regional_group.name)
        return Projeto.objects.none()
