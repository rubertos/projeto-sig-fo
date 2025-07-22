from django.db import models

class Projeto(models.Model):
    # Seção 1: Identificação
    Identificador = models.CharField(max_length=100, unique=True, primary_key=True)
    Ano_Implantacao = models.IntegerField(null=True, blank=True)
    Regional = models.CharField(max_length=100, null=True, blank=True)
    Estacao_BdRaf = models.CharField(max_length=100, null=True, blank=True)
    COD_IBGE = models.IntegerField(null=True, blank=True)
    Municipio = models.CharField(max_length=200, null=True, blank=True)

    # Seção 2: CAPEX e Qualidade
    Projeto_CAPEX = models.CharField(max_length=200, null=True, blank=True)
    Sub_Projeto_CAPEX = models.CharField(max_length=200, null=True, blank=True)
    SI_CAPEX = models.CharField(max_length=100, null=True, blank=True)
    Reserva_1 = models.CharField(max_length=200, null=True, blank=True)
    Reserva_2 = models.CharField(max_length=200, null=True, blank=True)
    Reserva_3 = models.CharField(max_length=200, null=True, blank=True)
    Reserva_4 = models.CharField(max_length=200, null=True, blank=True)
    Reserva_5 = models.CharField(max_length=200, null=True, blank=True)
    QUALIDADE_PREENCHIMENTO = models.CharField(max_length=50, null=True, blank=True)
    CAPEX = models.FloatField(null=True, blank=True)
    OS_WF = models.CharField(max_length=100, null=True, blank=True)

    # Seção 3: Cronograma e Métricas
    Km_Projeto_Executado = models.FloatField(null=True, blank=True)
    Km_Construido = models.FloatField(null=True, blank=True)
    Data_Protocolo_Real = models.CharField(max_length=50, default='Não realizado')
    Construcao_Parcial_Real = models.CharField(max_length=50, default='Não realizado')

    # Marcos Planejados vs. Reais
    Req_Gen_Plan = models.DateField(null=True, blank=True)
    Req_Gen_Real = models.CharField(max_length=50, default='Não realizado')
    Projeto_Executivo_Plan = models.DateField(null=True, blank=True)
    Projeto_Executivo_Real = models.CharField(max_length=50, default='Não realizado')
    Licenciamento_Plan = models.DateField(null=True, blank=True)
    Licenciamento_Real = models.CharField(max_length=50, default='Não realizado')
    MOS_Plan = models.DateField(null=True, blank=True)
    MOS_Real = models.CharField(max_length=50, default='Não realizado')
    Swap_Plan = models.DateField(null=True, blank=True)
    Swap_Real = models.CharField(max_length=50, default='Não realizado')
    Construcao_Total_Plan = models.DateField(null=True, blank=True)
    Construcao_Total_Real = models.CharField(max_length=50, default='Não realizado')
    RFI_Plan = models.DateField(null=True, blank=True)
    RFI_Real = models.CharField(max_length=50, default='Não realizado')
    Entroncado_Plan = models.DateField(null=True, blank=True)
    Entroncado_Real = models.CharField(max_length=50, default='Não realizado')
    Documentacao_Plan = models.DateField(null=True, blank=True)
    Documentacao_Real = models.CharField(max_length=50, default='Não realizado')
    GP_Plan = models.DateField(null=True, blank=True)
    GP_Real = models.CharField(max_length=50, default='Não realizado')

    dataAtualizacao = models.DateField(auto_now=True)

    def __str__(self):
        return self.Identificador