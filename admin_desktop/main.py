import tkinter as tk
from tkinter import ttk, messagebox, font
from api_client import ApiCliente
from ui.cadastro_veiculo_window import CadastroVeiculoWindow
from ui.cadastro_usuario_window import CadastroUsuarioWindow 
from ui.agendamento_tab import AgendamentoTab

class App(tk.Tk):
    """Aplicação principal da interface de administração."""
    def __init__(self):
        super().__init__()
        self.title("Gestão de Autoescola")
        self.geometry("950x650")

        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure_styles()

        self.api = ApiCliente()
        self.create_widgets()

    def configure_styles(self):
        """Configura a paleta de cores e os estilos dos widgets."""
        COR_FUNDO = "#ECEFF1"
        COR_FUNDO_FRAME = "#FFFFFF"
        COR_PRIMARIA = "#007BFF"
        COR_DELETAR = "#DC3545"
        COR_LETRA_BOTAO = "#FFFFFF"

        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=10)
        
        self.configure(background=COR_FUNDO)
        self.style.configure('TFrame', background=COR_FUNDO_FRAME)
        self.style.configure('TNotebook', background=COR_FUNDO, borderwidth=0)
        self.style.configure('TNotebook.Tab', background="#D4D7D9", padding=[10, 5], font=("Segoe UI", 10))
        self.style.map('TNotebook.Tab', background=[('selected', COR_FUNDO_FRAME)])
        self.style.configure('Title.TLabel', background=COR_FUNDO_FRAME, foreground=COR_PRIMARIA, font=("Segoe UI", 16, "bold"))
        self.style.configure('TButton', background=COR_PRIMARIA, foreground=COR_LETRA_BOTAO, font=("Segoe UI", 10, "bold"), padding=5)
        self.style.map('TButton', background=[('active', '#0056b3')])
        self.style.configure('Delete.TButton', background=COR_DELETAR, foreground=COR_LETRA_BOTAO)
        self.style.map('Delete.TButton', background=[('active', '#c82333')])
        self.style.configure("Treeview", background=COR_FUNDO_FRAME, foreground="#263238", rowheight=25, fieldbackground=COR_FUNDO_FRAME)
        self.style.map("Treeview", background=[('selected', COR_PRIMARIA)])
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=5)

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # --- Aba de Veículos ---
        self.frame_veiculos = ttk.Frame(notebook, padding="10")
        notebook.add(self.frame_veiculos, text='Frota de Veículos')
        self.create_aba_veiculos()
        self.popular_tabela_veiculos()

        # --- Aba de Alunos ---
        self.frame_alunos = ttk.Frame(notebook, padding="10")
        notebook.add(self.frame_alunos, text='Alunos')
        self.create_aba_alunos()
        self.popular_tabela_alunos()

        # --- Aba de Instrutores ---
        self.frame_instrutores = ttk.Frame(notebook, padding="10")
        notebook.add(self.frame_instrutores, text='Instrutores')
        self.create_aba_instrutores()
        self.popular_tabela_instrutores()

        # --- Aba de Agendamentos ---
        self.frame_agendamentos = AgendamentoTab(notebook, self.api)
        self.frame_agendamentos.configure(style='TFrame')
        notebook.add(self.frame_agendamentos, text="Agendamento de Aulas")

    def _get_selected_item_id(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Nenhum Item Selecionado", "Por favor, selecione um item na lista primeiro.")
            return None
        item = tree.item(selection[0])
        return item['values'][0]

    # --- ABA DE VEÍCULOS ---
    def create_aba_veiculos(self):
        label_titulo = ttk.Label(self.frame_veiculos, text="Gestão da Frota", style='Title.TLabel')
        label_titulo.pack(pady=10, anchor=tk.W)
        tree_container = ttk.Frame(self.frame_veiculos, style='TFrame')
        tree_container.pack(expand=True, fill='both')
        colunas = ('id', 'placa', 'modelo', 'marca', 'ano', 'tipo')
        self.tree_veiculos = ttk.Treeview(tree_container, columns=colunas, show='headings')
        self.tree_veiculos.heading('id', text='ID'); self.tree_veiculos.column('id', width=40)
        self.tree_veiculos.heading('placa', text='Placa'); self.tree_veiculos.column('placa', width=100)
        self.tree_veiculos.heading('modelo', text='Modelo'); self.tree_veiculos.column('modelo', width=150)
        self.tree_veiculos.heading('marca', text='Marca'); self.tree_veiculos.column('marca', width=150)
        self.tree_veiculos.heading('ano', text='Ano'); self.tree_veiculos.column('ano', width=60)
        self.tree_veiculos.heading('tipo', text='Tipo'); self.tree_veiculos.column('tipo', width=80)
        self.tree_veiculos.pack(expand=True, fill='both', side=tk.LEFT)
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_veiculos.yview)
        self.tree_veiculos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        botoes_frame = ttk.Frame(self.frame_veiculos)
        botoes_frame.pack(pady=15, fill='x')
        ttk.Button(botoes_frame, text="Cadastrar Novo", command=self.abrir_janela_cadastro_veiculo).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.popular_tabela_veiculos).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Editar Selecionado", command=self.editar_veiculo_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Excluir Selecionado", command=self.deletar_veiculo_selecionado, style='Delete.TButton').pack(side=tk.LEFT, padx=5)

    def abrir_janela_cadastro_veiculo(self, veiculo=None):
        CadastroVeiculoWindow(self, self.api, self.popular_tabela_veiculos, veiculo_existente=veiculo)

    def popular_tabela_veiculos(self):
        for i in self.tree_veiculos.get_children(): self.tree_veiculos.delete(i)
        veiculos = self.api.listar_veiculos()
        if veiculos and 'erro' not in veiculos:
            for v in veiculos:
                self.tree_veiculos.insert('', tk.END, values=(v['id'], v['placa'], v['modelo'], v.get('marca', ''), v.get('ano', ''), v.get('tipo', '')))
        elif veiculos and 'erro' in veiculos:
            messagebox.showerror("Erro de API", f"Não foi possível buscar os veículos: {veiculos['erro']}")

    def editar_veiculo_selecionado(self):
        veiculo_id = self._get_selected_item_id(self.tree_veiculos)
        if not veiculo_id: return
        veiculos = self.api.listar_veiculos() 
        if veiculos and 'erro' not in veiculos:
            veiculo_data = next((v for v in veiculos if v['id'] == veiculo_id), None)
            if veiculo_data:
                self.abrir_janela_cadastro_veiculo(veiculo=veiculo_data)

    def deletar_veiculo_selecionado(self):
        veiculo_id = self._get_selected_item_id(self.tree_veiculos)
        if not veiculo_id: return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o veículo selecionado?"):
            resultado = self.api.deletar_veiculo(veiculo_id)
            if 'erro' in resultado: messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Veículo excluído com sucesso!")
                self.popular_tabela_veiculos()

    # --- NOVA: ABA DE ALUNOS ---
    def create_aba_alunos(self):
        label_titulo = ttk.Label(self.frame_alunos, text="Gestão de Alunos", style='Title.TLabel')
        label_titulo.pack(pady=10, anchor=tk.W)
        tree_container = ttk.Frame(self.frame_alunos, style='TFrame')
        tree_container.pack(expand=True, fill='both')
        colunas = ('id', 'nome', 'email', 'cpf', 'matricula')
        self.tree_alunos = ttk.Treeview(tree_container, columns=colunas, show='headings')
        self.tree_alunos.heading('id', text='ID'); self.tree_alunos.column('id', width=40)
        self.tree_alunos.heading('nome', text='Nome'); self.tree_alunos.column('nome', width=250)
        self.tree_alunos.heading('email', text='Email'); self.tree_alunos.column('email', width=250)
        self.tree_alunos.heading('cpf', text='CPF'); self.tree_alunos.column('cpf', width=120)
        self.tree_alunos.heading('matricula', text='Matrícula'); self.tree_alunos.column('matricula', width=100)
        self.tree_alunos.pack(expand=True, fill='both', side=tk.LEFT)
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_alunos.yview)
        self.tree_alunos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        botoes_frame = ttk.Frame(self.frame_alunos)
        botoes_frame.pack(pady=15, fill='x')
        ttk.Button(botoes_frame, text="Cadastrar Novo", command=lambda: self.abrir_janela_cadastro_usuario(role='aluno')).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.popular_tabela_alunos).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Editar Selecionado", command=self.editar_aluno_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Excluir Selecionado", command=self.deletar_aluno_selecionado, style='Delete.TButton').pack(side=tk.LEFT, padx=5)

    def popular_tabela_alunos(self):
        for i in self.tree_alunos.get_children(): self.tree_alunos.delete(i)
        alunos = self.api.listar_alunos()
        if alunos and 'erro' not in alunos:
            for aluno in alunos:
                self.tree_alunos.insert('', tk.END, values=(aluno['id'], aluno['nome'], aluno['email'], aluno['cpf'], aluno['matricula']))
        elif alunos and 'erro' in alunos:
            messagebox.showerror("Erro de API", f"Não foi possível buscar os alunos: {alunos['erro']}")
            
    def editar_aluno_selecionado(self):
        aluno_id = self._get_selected_item_id(self.tree_alunos)
        if not aluno_id: return
        alunos = self.api.listar_alunos()
        if alunos and 'erro' not in alunos:
            aluno_data = next((a for a in alunos if a['id'] == aluno_id), None)
            if aluno_data:
                self.abrir_janela_cadastro_usuario(role='aluno', usuario=aluno_data)

    def deletar_aluno_selecionado(self):
        aluno_id = self._get_selected_item_id(self.tree_alunos)
        if not aluno_id: return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o aluno selecionado?"):
            resultado = self.api.deletar_aluno(aluno_id)
            if 'erro' in resultado: messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!")
                self.popular_tabela_alunos()

    # --- NOVA: ABA DE INSTRUTORES ---
    def create_aba_instrutores(self):
        label_titulo = ttk.Label(self.frame_instrutores, text="Gestão de Instrutores", style='Title.TLabel')
        label_titulo.pack(pady=10, anchor=tk.W)
        tree_container = ttk.Frame(self.frame_instrutores, style='TFrame')
        tree_container.pack(expand=True, fill='both')
        colunas = ('id', 'nome', 'email', 'cpf', 'cnh')
        self.tree_instrutores = ttk.Treeview(tree_container, columns=colunas, show='headings')
        self.tree_instrutores.heading('id', text='ID'); self.tree_instrutores.column('id', width=40)
        self.tree_instrutores.heading('nome', text='Nome'); self.tree_instrutores.column('nome', width=250)
        self.tree_instrutores.heading('email', text='Email'); self.tree_instrutores.column('email', width=250)
        self.tree_instrutores.heading('cpf', text='CPF'); self.tree_instrutores.column('cpf', width=120)
        self.tree_instrutores.heading('cnh', text='CNH'); self.tree_instrutores.column('cnh', width=100)
        self.tree_instrutores.pack(expand=True, fill='both', side=tk.LEFT)
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_instrutores.yview)
        self.tree_instrutores.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        botoes_frame = ttk.Frame(self.frame_instrutores)
        botoes_frame.pack(pady=15, fill='x')
        ttk.Button(botoes_frame, text="Cadastrar Novo", command=lambda: self.abrir_janela_cadastro_usuario(role='instrutor')).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.popular_tabela_instrutores).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Editar Selecionado", command=self.editar_instrutor_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Excluir Selecionado", command=self.deletar_instrutor_selecionado, style='Delete.TButton').pack(side=tk.LEFT, padx=5)

    def popular_tabela_instrutores(self):
        for i in self.tree_instrutores.get_children(): self.tree_instrutores.delete(i)
        instrutores = self.api.listar_instrutores()
        if instrutores and 'erro' not in instrutores:
            for instrutor in instrutores:
                self.tree_instrutores.insert('', tk.END, values=(instrutor['id'], instrutor['nome'], instrutor['email'], instrutor['cpf'], instrutor['cnh']))
        elif instrutores and 'erro' in instrutores:
            messagebox.showerror("Erro de API", f"Não foi possível buscar os instrutores: {instrutores['erro']}")

    def editar_instrutor_selecionado(self):
        instrutor_id = self._get_selected_item_id(self.tree_instrutores)
        if not instrutor_id: return
        instrutores = self.api.listar_instrutores()
        if instrutores and 'erro' not in instrutores:
            instrutor_data = next((i for i in instrutores if i['id'] == instrutor_id), None)
            if instrutor_data:
                self.abrir_janela_cadastro_usuario(role='instrutor', usuario=instrutor_data)

    def deletar_instrutor_selecionado(self):
        instrutor_id = self._get_selected_item_id(self.tree_instrutores)
        if not instrutor_id: return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o instrutor selecionado?"):
            resultado = self.api.deletar_instrutor(instrutor_id)
            if 'erro' in resultado: messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Instrutor excluído com sucesso!")
                self.popular_tabela_instrutores()

    def abrir_janela_cadastro_usuario(self, role, usuario=None):
        on_success_callback = self.popular_tabela_alunos if role == 'aluno' else self.popular_tabela_instrutores
        CadastroUsuarioWindow(self, self.api, on_success_callback, role=role, usuario_existente=usuario)

if __name__ == "__main__":
    app = App()
    app.mainloop()