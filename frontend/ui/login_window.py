import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, api_client, on_success):
        super().__init__(parent)
        self.api = api_client
        self.on_success = on_success
        self.parent = parent

        self.title("Login - Gestão de Autoescola")
        self.geometry("600x350")
        self.iconbitmap("icone.ico")

        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Carregar a imagem do logo
        try:
            # Tenta carregar a imagem a partir de um caminho relativo
            image_path = os.path.join(os.path.dirname(__file__), '..', '..', 'utils', 'imagem.png')
            self.logo_image = ImageTk.PhotoImage(Image.open(image_path).resize((100, 100), Image.Resampling.LANCZOS))
        except FileNotFoundError:
            print(f"Aviso: Imagem de logo não encontrada em {image_path}")
            self.logo_image = None
        except Exception as e:
            print(f"Erro ao carregar a imagem: {e}")
            self.logo_image = None

        self.create_widgets()

    def create_widgets(self):
        # --- Painel Esquerdo (Azul) ---
        left_frame = tk.Frame(self, bg="#007BFF", width=250)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        if self.logo_image:
            label_logo = tk.Label(left_frame, image=self.logo_image, bg="#007BFF")
            label_logo.pack(pady=(50, 10))

        label_title = tk.Label(left_frame, text="Autoescola\nManager", font=("Segoe UI", 20, "bold"), fg="white", bg="#007BFF")
        label_title.pack(pady=10)

        # --- Painel Direito (Branco) ---
        right_frame = ttk.Frame(self, padding=(40, 30))
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        label_login = ttk.Label(right_frame, text="Acesso Restrito", font=("Segoe UI", 18, "bold"), foreground="#007BFF")
        label_login.pack(pady=(20, 30))

        # Container para os campos de entrada
        input_frame = ttk.Frame(right_frame)
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text="Email:").pack(anchor=tk.W)
        self.email_entry = ttk.Entry(input_frame, width=30, font=("Segoe UI", 10))
        self.email_entry.pack(fill=tk.X, pady=(5, 15))
        self.email_entry.focus() # Foco inicial no campo de email

        ttk.Label(input_frame, text="Senha:").pack(anchor=tk.W)
        self.senha_entry = ttk.Entry(input_frame, width=30, show="*", font=("Segoe UI", 10))
        self.senha_entry.pack(fill=tk.X, pady=(5, 20))
        self.senha_entry.bind("<Return>", self.do_login) # Permite fazer login com a tecla Enter

        btn_login = ttk.Button(right_frame, text="Entrar", command=self.do_login, style='TButton')
        btn_login.pack(fill=tk.X, ipady=5)

    def do_login(self, event=None): # Adicionado event=None para o bind da tecla Enter
        email = self.email_entry.get()
        senha = self.senha_entry.get()

        if not email or not senha:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha o email e a senha.")
            return

        resultado = self.api.login(email, senha)
        
        if resultado and 'token' in resultado:
            self.destroy()
            self.on_success()
        else:
            erro = resultado.get('erro', 'Erro desconhecido ao tentar fazer login.')
            messagebox.showerror("Erro de Login", erro)
            
    def on_closing(self):
        self.parent.destroy()