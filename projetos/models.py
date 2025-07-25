from django.db import models
from django.contrib.auth.models import User

class Projeto(models.Model):
    Identificador = models.CharField(max_length=100, primary_key=True, unique=True)
    Ano_Implantacao = models.IntegerField(null=True, blank=True)
    Regional = models.CharField(max_length=100, null=True, blank=True)
    Estacao_BdRaf = models.CharField(max_length=100, null=True, blank=True)
    COD_IBGE = models.IntegerField(null=True, blank=True)
    Municipio = models.CharField(max_length=100, null=True, blank=True)
    Projeto_CAPEX = models.CharField(max_length=100, null=True, blank=True)
    Sub_Projeto_CAPEX = models.CharField(max_length=100, null=True, blank=True)
    SI_CAPEX = models.CharField(max_length=100, null=True, blank=True)
    CAPEX = models.FloatField(null=True, blank=True)
    OS_WF = models.CharField(max_length=100, null=True, blank=True)
    QUALIDADE_PREENCHIMENTO = models.CharField(max_length=50, null=True, blank=True)

    Req_Gen_Plan = models.DateField(null=True, blank=True)
    Req_Gen_Real = models.DateField(null=True, blank=True)
    Projeto_Executivo_Plan = models.DateField(null=True, blank=True)
    Projeto_Executivo_Real = models.DateField(null=True, blank=True)
    Licenciamento_Plan = models.DateField(null=True, blank=True)
    Licenciamento_Real = models.DateField(null=True, blank=True)
    MOS_Plan = models.DateField(null=True, blank=True)
    MOS_Real = models.DateField(null=True, blank=True)
    Swap_Plan = models.DateField(null=True, blank=True)
    Swap_Real = models.DateField(null=True, blank=True)
    Construcao_Total_Plan = models.DateField(null=True, blank=True)
    Construcao_Total_Real = models.DateField(null=True, blank=True)
    RFI_Plan = models.DateField(null=True, blank=True)
    RFI_Real = models.DateField(null=True, blank=True)
    Entroncado_Plan = models.DateField(null=True, blank=True)
    Entroncado_Real = models.DateField(null=True, blank=True)
    Documentacao_Plan = models.DateField(null=True, blank=True)
    Documentacao_Real = models.DateField(null=True, blank=True)
    GP_Plan = models.DateField(null=True, blank=True)
    GP_Real = models.DateField(null=True, blank=True)
    Data_Protocolo_Real = models.DateField(null=True, blank=True)
    Construcao_Parcial_Real = models.DateField(null=True, blank=True)

    Km_Projeto_Executado = models.FloatField(null=True, blank=True)
    Km_Construido = models.FloatField(null=True, blank=True)

    data_atualizacao = models.DateField(auto_now=True)
    ultima_atualizacao_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.Identificador