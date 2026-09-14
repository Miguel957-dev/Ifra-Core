import tkinter as tk 
from tkinter import filedialog
import ifcopenshell
import customtkinter as ctk
from extrair_dados import extrair_dados

    # Abrir uma janela 
def iniciar_interface():
    '''Todo essa função (iniciar_interface) é para importar todos esses comando para o cerebro que é main que vai orquestrar tudo isso deixando os codigos mais limpos, faceis de entender e de desbugar. Essa função é para que toda a janela seja aberta e recebar o arquivo IFC em uma variavel.
    MIGUEL LUCAS.'''
    janela = ctk.CTk()
    janela.config(bg='black')
    janela.title('InfraCore')
    janela.geometry('800x700')

    # Receber o arquivo IFC


    def selecionar_IFC():
        '''''É O QUE VAI FAZER A SELEÇÃO DO ARQUIVO IFC PARA FINS DE CALCULOS ESTRUTURAIS.'''
        caminho_IFC = filedialog.askopenfilename(
            title="Selecionar arquivo IFC",
            filetypes=[("Arquivos IFC", "*.ifc")]
        )

        if caminho_IFC:
            txt_arquivo.configure(text=caminho_IFC)

            try:
                modelo = ifcopenshell.open(caminho_IFC)
                print("IFC carregado com sucesso")
            except Exception as e:
                print("Erro:", e)

        modelo = ifcopenshell.open(caminho_IFC)
        extrair_dados(modelo)

    txt_arquivo = ctk.CTkLabel(janela, text="Nenhum arquivo selecionado")


    txt_arquivo = ctk.CTkLabel(janela, text="Selecioner o arquivo IFC")
    txt_arquivo.pack(side='top', padx=10, pady=10)

    botao = ctk.CTkButton(janela, text="Selecionar", 
                        command= selecionar_IFC,
                        fg_color="#2ecc71",
                        hover_color="#1c8046")
    botao.pack(side='top', padx= 10, pady=10)

    # Enviar para a estração de informação 
    janela.mainloop()
