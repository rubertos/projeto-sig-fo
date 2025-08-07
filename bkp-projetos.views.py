import json
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets, permissions
from .models import Projeto
from .serializers import ProjetoSerializer

# --- Views de Páginas ---
def login_view(request):
    return render(request, 'login.html')

@login_required
def index_view(request):
    return render(request, 'index.html')

@login_required
def admin_view(request):
    return render(request, 'admin.html')

@login_required
def lista_projetos_view(request):
    return render(request, 'lista_projetos.html')

# --- Views de API ---
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

# --- View de Importação do Admin (PnFO_geral) ---
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
            df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
            novos_projetos_count = 0
            
            for _, row in df.iterrows():
                identificador = row.get('Identificador')
                if not identificador or pd.isna(identificador): continue
                
                # Se o projeto não existe, cria a "casca" com os dados de identificação
                if not Projeto.objects.filter(Identificador=identificador).exists():
                    Projeto.objects.create(
                        Identificador=identificador,
                        Ano_Implantacao=pd.to_numeric(row.get('Ano Implantação'), errors='coerce'),
                        Regional=row.get('Regional'),
                        Estacao_BdRaf=row.get('Estação BdRaf'),
                        COD_IBGE=pd.to_numeric(row.get('COD_IBGE'), errors='coerce'),
                        Municipio=row.get('Municipio'),
                        Projeto_CAPEX=row.get('Projeto CAPEX'),
                        Sub_Projeto_CAPEX=row.get('Sub-Projeto CAPEX'),
                        SI_CAPEX=row.get('SI CAPEX'),
                        foi_notificado=False
                    )
                    novos_projetos_count += 1
                    
            return JsonResponse({'message': f'{novos_projetos_count} novos projetos foram criados.'})
        except Exception as e:
            return JsonResponse({'message': f'Erro ao processar o ficheiro: {e}'}, status=500)
    return JsonResponse({'message': 'Método não permitido.'}, status=405)

# --- View de Importação Regional ---
@csrf_exempt
@login_required
def import_regional_view(request):
    if request.method == 'POST':
        file = request.FILES.get('regional_update_file')
        user = request.user
        if not file:
            return JsonResponse({'message': 'Nenhum ficheiro enviado.'}, status=400)
        try:
            df = pd.read_excel(file)
            updated_count = 0
            
            mapeamento_colunas = {
                'Req Gen Plan': 'Req_Gen_Plan', 'Req Gen Real': 'Req_Gen_Real', 'OS WF': 'OS_WF',
                'Km projeto executado': 'Km_Projeto_Executado', 'Projeto Executivo Plan': 'Projeto_Executivo_Plan',
                'Projeto Executivo Real': 'Projeto_Executivo_Real', 'Data protocolo real': 'Data_Protocolo_Real',
                'Licenciamento Plan': 'Licenciamento_Plan', 'Licenciamento Real': 'Licenciamento_Real',
                'MOS Plan': 'MOS_Plan', 'MOS Real': 'MOS_Real', 'Swap Plan': 'Swap_Plan', 'Swap Real': 'Swap_Real',
                'Km construído': 'Km_Construido', 'Construção Plan': 'Construcao_Total_Plan',
                'Construção Parcial': 'Construcao_Parcial_Real', 'Construção Real': 'Construcao_Total_Real',
                'RFI Plan': 'RFI_Plan', 'RFI Real': 'RFI_Real', 'Entroncado Plan': 'Entroncado_Plan',
                'Entroncado Real': 'Entroncado_Real', 'Documentação Plan': 'Documentacao_Plan',
                'Documentação Real': 'Documentacao_Real', 'GP Plan': 'GP_Plan', 'GP Real': 'GP_Real'
            }

            for _, row in df.iterrows():
                identificador = row.get('Identificador')
                if not identificador: continue
                try:
                    projeto = Projeto.objects.get(Identificador=identificador)
                    
                    for nome_coluna, campo_modelo in mapeamento_colunas.items():
                        if nome_coluna in row and pd.notna(row[nome_coluna]):
                            valor = row[nome_coluna]
                            if 'Plan' in campo_modelo or 'Real' in campo_modelo:
                                valor_convertido = pd.to_datetime(valor, errors='coerce')
                            else:
                                valor_convertido = pd.to_numeric(valor, errors='coerce')
                            
                            if pd.notna(valor_convertido):
                                setattr(projeto, campo_modelo, valor_convertido)
                    
                    projeto.ultima_atualizacao_por = user
                    projeto.save()
                    updated_count += 1
                except Projeto.DoesNotExist:
                    continue
                    
            return JsonResponse({'message': f'{updated_count} projetos foram atualizados com sucesso!'})
        except Exception as e:
            return JsonResponse({'message': f'Erro ao processar o ficheiro: {e}'}, status=500)
    return JsonResponse({'message': 'Método não permitido.'}, status=405)

# --- Views de Notificação e Exportação ---
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
def export_all_data_xls(request):
    if not request.user.is_staff:
        return HttpResponse("Acesso negado.", status=403)
    
    queryset = Projeto.objects.all().values()
    if not list(queryset):
        return HttpResponse("Não há dados para exportar.")
    
    df = pd.DataFrame(list(queryset))
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="SIG_FO_Compilado.xlsx"'
    df.to_excel(response, index=False)
    return response

# --- API de Projetos ---
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
