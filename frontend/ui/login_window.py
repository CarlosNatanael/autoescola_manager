import tkinter as tk
from tkinter import ttk, messagebox
import os

class LoginWindow(tk.Toplevel):
    def __init__(self, master, api_client, on_login_success):
        super().__init__(master)
        self.master = master
        self.api = api_client
        self.on_login_success = on_login_success

        self.title("Login - Gestão de Autoescola")
        
        # --- Estilo e Geometria da Janela ---
        self.geometry("300x480")
        self.resizable(False, False)
        self.configure(background="#ECEFF1") # Fundo cinza claro

        # Centraliza a janela na tela
        self.center_window()

        # Define o ícone da janela
        try:
            script_dir = os.path.dirname(__file__)
            # O ícone está na pasta raiz do projeto, então voltamos dois níveis
            icon_path = os.path.join(script_dir, "..", "..", "icone.ico")
            self.iconbitmap(icon_path)
        except tk.TclError:
            print("Aviso: 'icone.ico' não encontrado para a janela de login.")

        # --- Estilos Personalizados para os Widgets ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        
        # Estilo para os labels (CPF, Senha)
        self.style.configure("Login.TLabel", background="#ECEFF1", foreground="#212529", font=("Segoe UI", 11))
        # Estilo para o título principal
        self.style.configure("Title.TLabel", background="#ECEFF1", foreground="#007BFF", font=("Segoe UI", 22, "bold"))
        # Estilo para os campos de entrada
        self.style.configure("TEntry", font=("Segoe UI", 12), padding=8, relief="flat")
        # Estilo para o botão de login
        self.style.configure("Login.TButton", font=("Segoe UI", 12, "bold"), padding=10, background="#007BFF", foreground="white", relief="flat", borderwidth=0)
        self.style.map("Login.TButton",
            background=[('active', '#0056b3')] # Cor quando o mouse está sobre o botão
        )
        # Estilo para o frame principal
        self.style.configure("Main.TFrame", background="#ECEFF1")

        self.create_widgets()
        
        # Configura a janela para ser modal (bloqueia interação com a janela principal)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.transient(master)
        self.grab_set()
        self.focus_force()

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        # Frame principal com preenchimento interno
        main_frame = ttk.Frame(self, style="Main.TFrame", padding=(40, 30))
        main_frame.pack(fill="both", expand=True)

        # --- Título ---
        title_label = ttk.Label(main_frame, text="Seja Bem-Vindo", style="Title.TLabel")
        title_label.pack(pady=(20, 40))

        # --- Campo de CPF ---
        cpf_label = ttk.Label(main_frame, text="CPF", style="Login.TLabel")
        cpf_label.pack(anchor="w", padx=5)
        self.entry_cpf = ttk.Entry(main_frame, style="TEntry", width=30)
        self.entry_cpf.pack(fill="x", pady=(5, 20), ipady=4)

        # --- Campo de Senha ---
        senha_label = ttk.Label(main_frame, text="Senha", style="Login.TLabel")
        senha_label.pack(anchor="w", padx=5)
        self.entry_senha = ttk.Entry(main_frame, show="*", style="TEntry", width=30)
        self.entry_senha.pack(fill="x", pady=(5, 40), ipady=4)
        self.add_placeholder(self.entry_senha, "Digite sua senha")
        
        # --- Botão de Login ---
        login_button = ttk.Button(main_frame, text="Entrar", command=self.login, style="Login.TButton", cursor="hand2")
        login_button.pack(fill="x", ipady=5)
        
        # Permite fazer login pressionando a tecla "Enter"
        self.bind("<Return>", lambda event: self.login())

    def add_placeholder(self, entry, placeholder_text):
        """Adiciona um texto temporário (placeholder) a um campo de entrada."""
        entry.insert(0, placeholder_text)
        entry.config(foreground="grey")

        def on_focus_in(event):
            if entry.get() == placeholder_text and entry.config('foreground')[4] == 'grey':
                entry.delete(0, "end")
                entry.config(foreground="black")

        def on_focus_out(event):
            if not entry.get():
                entry.insert(0, placeholder_text)
                entry.config(foreground="grey")

        entry.bind("<FocusIn>", on_focus_in, add="+")
        entry.bind("<FocusOut>", on_focus_out, add="+")

    def login(self):
        cpf = self.entry_cpf.get()
        # Verifica se o campo não está com o placeholder antes de enviar
        if cpf == "Digite apenas números" and self.entry_cpf.config('foreground')[4] == 'grey':
            cpf = ""
            
        senha = self.entry_senha.get()
        if senha == "Digite sua senha" and self.entry_senha.config('foreground')[4] == 'grey':
            senha = ""
            
        if not cpf or not senha:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha o CPF e a senha.", parent=self)
            return

        sucesso, mensagem = self.api.login(cpf, senha)
        if sucesso:
            self.destroy() # Fecha a janela de login
            self.on_login_success() # Chama a função para abrir a janela principal
        else:
            messagebox.showerror("Erro de Login", mensagem, parent=self)

    def _on_closing(self):
        """Fecha toda a aplicação se a janela de login for fechada."""
        self.master.destroy()