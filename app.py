import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import pandas as pd
from datetime import datetime
import hashlib
import fitz  # PyMuPDF
from PIL import Image, ImageTk
import io
import shutil

# ================= CONFIGURAÇÃO INICIAL =================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Variáveis globais
ARQUIVO_CSV = "dados.csv"
PASTA_PDFS = "pdf_anexos"
USUARIO_CORRETO = "admin"
SENHA_CORRETA = "1234"

# ================= FUNÇÕES PRINCIPAIS =================
USUARIOS = {
    "admin": hashlib.sha256("1234".encode()).hexdigest()
}

def voltar_ao_inicio(janela_atual):
    janela_atual.destroy()
    app.deiconify()

def validar_login():
    usuario = campo_usuario.get()
    senha = hash_senha(campo_senha.get())
    
    if usuario in USUARIOS and USUARIOS[usuario] == senha:
        abrir_formulario()
    else:
        resultado_login.configure(text="Credenciais inválidas!", text_color="red")

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def visualizar_pdf_historico(caminho_arquivo, janela_pai):
    if not os.path.exists(caminho_arquivo):
        messagebox.showerror("Erro", "Arquivo PDF não encontrado!")
        return
    
    try:
        doc = fitz.open(caminho_arquivo)
        page = doc.load_page(0)
        pix = page.get_pixmap()
        img = Image.open(io.BytesIO(pix.tobytes()))
        img.thumbnail((500, 500))
        
        viewer = ctk.CTkToplevel(janela_pai)
        viewer.title("Visualizador de PDF")
        
        tkimg = ImageTk.PhotoImage(img)
        label = ctk.CTkLabel(viewer, image=tkimg, text="")
        label.image = tkimg
        label.pack()
        
        ctk.CTkButton(
            viewer, 
            text="Voltar", 
            command=lambda: [viewer.destroy(), janela_pai.lift()],
            fg_color="gray"
        ).pack(pady=10)
        
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível abrir o PDF: {e}")

def abrir_historico(janela_pai=None):
    historico = ctk.CTkToplevel(janela_pai)
    historico.title("Histórico de Envios")
    historico.geometry("800x600")
    
    try:
        if not os.path.exists(ARQUIVO_CSV):
            messagebox.showinfo("Informação", "Nenhum registro encontrado!")
            historico.destroy()
            return
        
        df = pd.read_csv(ARQUIVO_CSV)
        
        frame = ctk.CTkScrollableFrame(historico)
        frame.pack(fill="both", expand=True)
        
        if df.empty:
            ctk.CTkLabel(frame, text="Nenhum registro encontrado").pack(pady=20)
            return
        
        for index, row in df.iterrows():
            registro_frame = ctk.CTkFrame(frame)
            registro_frame.pack(fill="x", pady=5, padx=10)
            
            ctk.CTkLabel(registro_frame, text=f"Data: {row['Data']}").pack(anchor="w")
            ctk.CTkLabel(registro_frame, text=f"Email: {row['Email']}").pack(anchor="w")
            ctk.CTkLabel(registro_frame, text=f"Telefone: {row['Telefone']}").pack(anchor="w")
            
            if pd.notna(row['Arquivo']) and row['Arquivo'] != 'N/A':
                ctk.CTkButton(
                    registro_frame, 
                    text="Visualizar PDF",
                    command=lambda path=row['Arquivo']: visualizar_pdf_historico(path, historico)
                ).pack(pady=5)
            
            ctk.CTkLabel(registro_frame, text="-"*50).pack(fill="x", pady=5)
            
    except Exception as e:
        messagebox.showerror("Erro", f"Não foi possível carregar o histórico: {e}")
        historico.destroy()
    
    ctk.CTkButton(
        historico, 
        text="Voltar ao Início", 
        command=lambda: voltar_ao_inicio(historico),
        fg_color="gray"
    ).pack(pady=10)

def abrir_formulario():
    app.withdraw()
    
    formulario = ctk.CTkToplevel()
    formulario.title("Formulário Completo")
    formulario.geometry("700x700")
    
    arquivo_selecionado = [None]
    btn_visualizar = None

    # Campos do formulário
    ctk.CTkLabel(formulario, text="Email*:").pack(pady=5)
    campo_email = ctk.CTkEntry(formulario, width=400)
    campo_email.pack(pady=5)
    
    ctk.CTkLabel(formulario, text="Telefone*:").pack(pady=5)
    campo_telefone = ctk.CTkEntry(formulario, width=400)
    campo_telefone.pack(pady=5)
    
    def visualizar_pdf():
        if arquivo_selecionado[0]:
            try:
                doc = fitz.open(arquivo_selecionado[0])
                page = doc.load_page(0)
                pix = page.get_pixmap()
                img = Image.open(io.BytesIO(pix.tobytes()))
                img.thumbnail((500, 500))
                
                viewer = ctk.CTkToplevel(formulario)
                viewer.title("Visualizador de PDF")
                
                tkimg = ImageTk.PhotoImage(img)
                label = ctk.CTkLabel(viewer, image=tkimg, text="")
                label.image = tkimg
                label.pack()
                
                ctk.CTkButton(
                    viewer, 
                    text="Voltar", 
                    command=viewer.destroy,
                    fg_color="gray"
                ).pack(pady=10)
                
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível abrir o PDF: {e}")
    
    def upload_pdf():
        nonlocal btn_visualizar
        arquivo = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if arquivo:
            if os.path.getsize(arquivo) > 5_000_000:
                messagebox.showerror("Erro", "Arquivo muito grande (máx. 5MB)")
            else:
                arquivo_selecionado[0] = arquivo
                label_arquivo.configure(text=f"PDF: {os.path.basename(arquivo)}")
                
                if btn_visualizar:
                    btn_visualizar.destroy()
                btn_visualizar = ctk.CTkButton(formulario, text="Visualizar PDF", command=visualizar_pdf)
                btn_visualizar.pack(pady=5)
    
    ctk.CTkButton(formulario, text="Selecionar PDF (máx. 5MB)", command=upload_pdf).pack(pady=10)
    label_arquivo = ctk.CTkLabel(formulario, text="Nenhum PDF selecionado")
    label_arquivo.pack()
    
    def enviar_formulario():
        email = campo_email.get()
        telefone = campo_telefone.get()
        
        if not email or not telefone:
            messagebox.showerror("Erro", "Preencha todos os campos obrigatórios!")
            return
        
        os.makedirs(PASTA_PDFS, exist_ok=True)
        
        nome_arquivo_pdf = "N/A"
        if arquivo_selecionado[0]:
            nome_arquivo = os.path.basename(arquivo_selecionado[0])
            destino = os.path.join(PASTA_PDFS, nome_arquivo)
            shutil.copy(arquivo_selecionado[0], destino)
            nome_arquivo_pdf = destino
        
        novos_dados = {
            "Data": [datetime.now().strftime("%d/%m/%Y %H:%M")],
            "Email": [email],
            "Telefone": [telefone],
            "Arquivo": [nome_arquivo_pdf]
        }
        
        df = pd.DataFrame(novos_dados)
        df.to_csv(ARQUIVO_CSV, mode='a', header=not os.path.exists(ARQUIVO_CSV), index=False)
        
        messagebox.showinfo("Sucesso", "Dados salvos com sucesso!")
        formulario.destroy()
        app.deiconify()
    
    ctk.CTkButton(formulario, text="ENVIAR", command=enviar_formulario, fg_color="green").pack(pady=20)
    
    ctk.CTkButton(
        formulario, 
        text="VER HISTÓRICO", 
        command=lambda: abrir_historico(formulario),
        fg_color="purple"
    ).pack(pady=5)
    
    ctk.CTkButton(
        formulario, 
        text="Voltar ao Início", 
        command=lambda: voltar_ao_inicio(formulario),
        fg_color="gray"
    ).pack(pady=10)

# ================= JANELA DE LOGIN =================
app = ctk.CTk()
app.geometry("500x400")
app.title("Sistema de Login")

ctk.CTkLabel(app, text="Usuário:").pack(pady=10)
campo_usuario = ctk.CTkEntry(app, placeholder_text="Digite 'admin'")
campo_usuario.pack(pady=10)

ctk.CTkLabel(app, text="Senha:").pack(pady=10)
campo_senha = ctk.CTkEntry(app, placeholder_text="Digite '1234'", show="*")
campo_senha.pack(pady=10)

ctk.CTkButton(app, text="ENTRAR", command=validar_login).pack(pady=20)

resultado_login = ctk.CTkLabel(app, text="")
resultado_login.pack(pady=10)

app.mainloop()