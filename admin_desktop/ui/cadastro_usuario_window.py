import tkinter as tk
from tkinter import ttk, messagebox

class CadastroUsuarioWindow(tk.Toplevel):
    """Janela para cadastrar um novo utilizador (Aluno ou Instrutor)."""
    def __init__(self, parent, api_client, on_success, usuario_existente=None):
        super().__init__(parent)
        self.api = api_client
        self.on_success = on_success
        self.usuario_existente = usuario_existente

        if self.usuario_existente:
            self.title("Editar Utilizador")
        else:
            self.title("Cadastrar Novo Utilizador")
            
        self.geometry("450x400")
        self.transient(parent)
        self.grab_set()

        self.entries = {}
        self.role_var = tk.StringVar()

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

        # Seletor de Função (Role)
        label_role = ttk.Label(frame, text="Função:")
        label_role.grid(row=4, column=0, sticky=tk.W, pady=5)
        self.role_combobox = ttk.Combobox(frame, textvariable=self.role_var, values=['aluno', 'instrutor'], state='readonly')
        self.role_combobox.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.role_combobox.bind("<<ComboboxSelected>>", self.toggle_campos_especificos)
        self.role_combobox.set('aluno') # Valor padrão

        # Campos específicos (iniciam ocultos)
        self.label_matricula = ttk.Label(frame, text="Matrícula:")
        self.entry_matricula = ttk.Entry(frame, width=35)
        self.entries['matricula'] = self.entry_matricula

        self.label_cnh = ttk.Label(frame, text="CNH:")
        self.entry_cnh = ttk.Entry(frame, width=35)
        self.entries['cnh'] = self.entry_cnh

        # Botão de Salvar
        texto_botao = "Atualizar" if self.usuario_existente else "Salvar"
        btn_salvar = ttk.Button(frame, text=texto_botao, command=self.salvar_usuario)
        btn_salvar.grid(row=7, column=0, columnspan=2, pady=20)

        # Se for edição, desabilita a troca de função (role)
        if self.usuario_existente:
            self.role_combobox.configure(state='disabled')

        self.toggle_campos_especificos()

    def toggle_campos_especificos(self, event=None):
        """Mostra/oculta os campos de matrícula ou CNH com base na função selecionada."""
        role = self.role_var.get()
        self.label_matricula.grid_forget()
        self.entry_matricula.grid_forget()
        self.label_cnh.grid_forget()
        self.entry_cnh.grid_forget()

        if role == 'aluno':
            self.label_matricula.grid(row=5, column=0, sticky=tk.W, pady=5)
            self.entry_matricula.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)
        elif role == 'instrutor':
            self.label_cnh.grid(row=5, column=0, sticky=tk.W, pady=5)
            self.entry_cnh.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=5)

    def preencher_dados(self):
        for campo_key in ['nome', 'email', 'cpf', 'telefone']:
            self.entries[campo_key].insert(0, self.usuario_existente.get(campo_key, ''))
        
        role = self.usuario_existente.get('role', 'aluno')
        self.role_var.set(role)
        
        if role == 'aluno':
            self.entries['matricula'].insert(0, self.usuario_existente.get('matricula', ''))
        elif role == 'instrutor':
            self.entries['cnh'].insert(0, self.usuario_existente.get('cnh', ''))
            
        self.toggle_campos_especificos()

    def salvar_usuario(self):
        dados_usuario = {campo: entry.get() for campo, entry in self.entries.items()}
        dados_usuario['role'] = self.role_var.get()

        if not all(dados_usuario.get(key) for key in ['nome', 'email', 'cpf', 'role']):
            messagebox.showwarning("Campos Obrigatórios", "Nome, Email, CPF e Função são obrigatórios.")
            return

        if self.usuario_existente:
            resultado = self.api.atualizar_usuario(self.usuario_existente['id'], dados_usuario)
            mensagem_sucesso = "Utilizador atualizado com sucesso!"
        else:
            resultado = self.api.cadastrar_usuario(dados_usuario)
            mensagem_sucesso = "Utilizador cadastrado com sucesso!"

        if 'erro' not in resultado:
            messagebox.showinfo("Sucesso", mensagem_sucesso)
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Erro", resultado['erro'])
