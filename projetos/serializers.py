from rest_framework import serializers
from .models import Projeto, PnfoGeral

class ProjetoSerializer(serializers.ModelSerializer):
    # Campos que vêm da tabela PnfoGeral e que vamos adicionar à nossa resposta da API
    Ano_Implantacao_pnfo = serializers.SerializerMethodField()
    Estacao_BdRaf_pnfo = serializers.SerializerMethodField()
    COD_IBGE_pnfo = serializers.SerializerMethodField()
    Municipio_pnfo = serializers.SerializerMethodField()
    Projeto_CAPEX_pnfo = serializers.SerializerMethodField()
    Sub_Projeto_CAPEX_pnfo = serializers.SerializerMethodField()
    SI_CAPEX_pnfo = serializers.SerializerMethodField()

    class Meta:
        model = Projeto
        # CORREÇÃO: Listamos todos os campos explicitamente
        fields = [
            'Identificador', 'Ano_Implantacao', 'Regional', 'Estacao_BdRaf', 'COD_IBGE', 
            'Municipio', 'Projeto_CAPEX', 'Sub_Projeto_CAPEX', 'SI_CAPEX', 'CAPEX', 
            'OS_WF', 'QUALIDADE_PREENCHIMENTO', 'Req_Gen_Plan', 'Req_Gen_Real', 
            'Projeto_Executivo_Plan', 'Projeto_Executivo_Real', 'Licenciamento_Plan', 
            'Licenciamento_Real', 'MOS_Plan', 'MOS_Real', 'Swap_Plan', 'Swap_Real', 
            'Construcao_Total_Plan', 'Construcao_Total_Real', 'RFI_Plan', 'RFI_Real', 
            'Entroncado_Plan', 'Entroncado_Real', 'Documentacao_Plan', 'Documentacao_Real', 
            'GP_Plan', 'GP_Real', 'Data_Protocolo_Real', 'Construcao_Parcial_Real', 
            'Km_Projeto_Executado', 'Km_Construido', 'data_atualizacao', 
            'ultima_atualizacao_por', 'foi_notificado',
            # Adicionamos os campos extra da PnfoGeral
            'Ano_Implantacao_pnfo', 'Estacao_BdRaf_pnfo', 'COD_IBGE_pnfo', 'Municipio_pnfo', 
            'Projeto_CAPEX_pnfo', 'Sub_Projeto_CAPEX_pnfo', 'SI_CAPEX_pnfo'
        ]

    # Função para obter o dado de um campo específico da tabela PnfoGeral
    def get_pnfo_data(self, obj, field_name):
        try:
            pnfo_obj = PnfoGeral.objects.get(Identificador=obj.Identificador)
            return getattr(pnfo_obj, field_name, None)
        except PnfoGeral.DoesNotExist:
            return None

    # Para cada campo que criámos, dizemos ao Django como obter o seu valor
    def get_Ano_Implantacao_pnfo(self, obj):
        return self.get_pnfo_data(obj, 'Ano_Implantacao')

    def get_Estacao_BdRaf_pnfo(self, obj):
        return self.get_pnfo_data(obj, 'Estacao_BdRaf')

    def get_COD_IBGE_pnfo(self, obj):
        return self.get_pnfo_data(obj, 'COD_IBGE')

    def get_Municipio_pnfo(self, obj):
        return self.get_pnfo_data(obj, 'Municipio')

    def get_Projeto_CAPEX_pnfo(self, obj):
        return self.get_pnfo_data(obj, 'Projeto_CAPEX')

    def get_Sub_Projeto_CAPEX_pnfo(self, obj):
        return self.get_pnfo_data(obj, 'Sub_Projeto_CAPEX')

    def get_SI_CAPEX_pnfo(self, obj):
        return self.get_pnfo_data(obj, 'SI_CAPEX')
