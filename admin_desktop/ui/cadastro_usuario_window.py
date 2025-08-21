import tkinter as tk
from tkinter import ttk, messagebox

class CadastroUsuarioWindow(tk.Toplevel):
    """Janela para cadastrar ou editar um Aluno ou Instrutor."""
    def __init__(self, parent, api_client, on_success, role, usuario_existente=None):
        super().__init__(parent)
        self.api = api_client
        self.on_success = on_success
        self.usuario_existente = usuario_existente
        self.role = role  # 'aluno' ou 'instrutor'

        titulo_acao = "Editar" if self.usuario_existente else "Cadastrar Novo"
        self.title(f"{titulo_acao} {self.role.capitalize()}")
            
        self.geometry("450x350")
        self.transient(parent)
        self.grab_set()

        self.entries = {}
        self.create_widgets()
        if self.usuario_existente:
            self.preencher_dados()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill=tk.BOTH)

        # Campos comuns
        campos = ['Nome', 'Email', 'CPF', 'Telefone']
        for i, campo in enumerate(campos):
            label = ttk.Label(frame, text=f"{campo}:")
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame, width=35)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
            self.entries[campo.lower()] = entry

        # Campo específico da função
        if self.role == 'instrutor':
            label_cnh = ttk.Label(frame, text="CNH:")
            label_cnh.grid(row=4, column=0, sticky=tk.W, pady=5)
            entry_cnh = ttk.Entry(frame, width=35)
            entry_cnh.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
            self.entries['cnh'] = entry_cnh
            
        # Botão de Salvar
        texto_botao = "Atualizar" if self.usuario_existente else "Salvar"
        btn_salvar = ttk.Button(frame, text=texto_botao, command=self.salvar_usuario)
        btn_salvar.grid(row=5, column=0, columnspan=2, pady=20)

    def preencher_dados(self):
        """Preenche o formulário com os dados do utilizador existente."""
        for campo_key, entry in self.entries.items():
            valor = self.usuario_existente.get(campo_key, "")
            entry.insert(0, valor if valor else "")

    def salvar_usuario(self):
        dados_usuario = {campo: entry.get() for campo, entry in self.entries.items()}

        # Validação de campos obrigatórios
        campos_obrigatorios = ['nome', 'email', 'cpf']
        if self.role == 'instrutor':
            campos_obrigatorios.append('cnh')

        if not all(dados_usuario.get(key) for key in campos_obrigatorios):
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha todos os campos obrigatórios.")
            return

        resultado = None
        mensagem_sucesso = ""

        if self.usuario_existente:
            if self.role == 'aluno':
                resultado = self.api.atualizar_aluno(self.usuario_existente['id'], dados_usuario)
            else:
                resultado = self.api.atualizar_instrutor(self.usuario_existente['id'], dados_usuario)
            mensagem_sucesso = f"{self.role.capitalize()} atualizado com sucesso!"
        else:
            if self.role == 'aluno':
                resultado = self.api.cadastrar_aluno(dados_usuario)
            else:
                resultado = self.api.cadastrar_instrutor(dados_usuario)
            mensagem_sucesso = f"{self.role.capitalize()} cadastrado com sucesso!"
        
        if resultado and 'erro' not in resultado:
            messagebox.showinfo("Sucesso", mensagem_sucesso)
            self.on_success()
            self.destroy()
        elif resultado:
            messagebox.showerror("Erro", resultado['erro'])