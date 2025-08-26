import tkinter as tk
from tkinter import ttk, messagebox

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, api_client, on_success):
        super().__init__(parent)
        self.api = api_client
        self.on_success = on_success
        self.parent = parent

        self.title("Login - Gestão de Autoescola")
        self.geometry("350x200")
        self.iconbitmap("icone.ico")
        self.transient(parent)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill=tk.BOTH)

        ttk.Label(frame, text="Email:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.email_entry = ttk.Entry(frame, width=30)
        self.email_entry.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Senha:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.senha_entry = ttk.Entry(frame, width=30, show="*")
        self.senha_entry.grid(row=1, column=1, pady=5)

        btn_login = ttk.Button(frame, text="Entrar", command=self.do_login)
        btn_login.grid(row=2, column=0, columnspan=2, pady=20)

    def do_login(self):
        email = self.email_entry.get()
        senha = self.senha_entry.get()

        if not email or not senha:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha o email e a senha.")
            return

        resultado = self.api.login(email, senha)
        
        if resultado and 'token' in resultado:
            self.destroy() # Fecha a janela de login
            self.on_success() # Chama a função para abrir a janela principal
        else:
            erro = resultado.get('erro', 'Erro desconhecido ao tentar fazer login.')
            messagebox.showerror("Erro de Login", erro)
            
    def on_closing(self):
        # Garante que a aplicação feche se o usuário fechar a janela de login
        self.parent.destroy()