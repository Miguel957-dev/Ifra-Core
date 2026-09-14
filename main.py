from extrair_dados import extrair_geo
import ifcopenshell

modelo = ifcopenshell.open('C:/Users/Miguel Lucas/Downloads/InfraCore/Projeto_casa_Infracore.ifc')

medidas_vigas, posiçao_viga, vigas_aera_horizontal, vigas_aereas_vertical, viga_baldr_horizontal, viga_baldr_vertical, pi_reais = extrair_geo(modelo)
