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
    
    # 1. Pega nos dados de referência do PnFO
    pnfo_qs = PnfoGeral.objects.all().values()
    if not list(pnfo_qs):
        return HttpResponse("A base de dados de referência (PnFO) está vazia. Por favor, importe um ficheiro PnFO primeiro.")
    df_pnfo = pd.DataFrame(list(pnfo_qs))

    # 2. Pega nas atualizações das regionais
    projetos_qs = Projeto.objects.all().values()
    df_projetos = pd.DataFrame(list(projetos_qs))

    # 3. Combina os dois conjuntos de dados de forma inteligente
    if not df_projetos.empty:
        # Usa um 'merge' para juntar os dois dataframes, mantendo todos os projetos do PnFO
        # O 'left' merge garante que todos os projetos da base PnFO são mantidos.
        df_final = pd.merge(df_pnfo, df_projetos, on='Identificador', how='left', suffixes=('_pnfo', ''))
        
        # Para cada coluna que existe em ambos, damos prioridade à versão atualizada (sem sufixo)
        # e preenchemos os vazios com os dados do PnFO (_pnfo).
        for col in df_pnfo.columns:
            if col != 'Identificador' and f"{col}_pnfo" in df_final.columns:
                # combine_first preenche os valores nulos em uma série com valores de outra
                df_final[col] = df_final[col].combine_first(df_final[f"{col}_pnfo"])
                # Remove a coluna duplicada do PnFO
                df_final.drop(columns=[f"{col}_pnfo"], inplace=True)
    else:
        # Se não houver atualizações, a exportação é apenas a base do PnFO
        df_final = df_pnfo

    # 4. Garante que as colunas estão na ordem correta do ficheiro SIG FO_RB.xlsb
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
    
    # Adiciona colunas que possam faltar no DataFrame com valores vazios
    for col in colunas_finais:
        if col not in df_final.columns:
            df_final[col] = None
    
    # Reordena e seleciona apenas as colunas necessárias
    df_final = df_final[colunas_finais]

    # 5. Gera o ficheiro Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = 'attachment; filename="SIG_FO_Compilado.xlsx"'
    df_final.to_excel(response, index=False)
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
