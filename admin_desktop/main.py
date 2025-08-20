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

        # --- CONFIGURAÇÃO DE ESTILO ---
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure_styles()

        self.api = ApiCliente()
        self.create_widgets()

    def configure_styles(self):
        """Configura a paleta de cores e os estilos dos widgets."""
        # Paleta de Cores
        COR_FUNDO = "#ECEFF1"
        COR_FUNDO_FRAME = "#FFFFFF"
        COR_LETRA = "#263238"
        COR_PRIMARIA = "#007BFF"
        COR_LETRA_BOTAO = "#FFFFFF"
        COR_DELETAR = "#DC3545"

        # Fontes
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(family="Segoe UI", size=10)
        
        # Estilo geral da janela
        self.configure(background=COR_FUNDO)

        # Estilo para os Frames das Abas
        self.style.configure('TFrame', background=COR_FUNDO_FRAME)
        
        # Estilo para o Notebook (Abas)
        self.style.configure('TNotebook', background=COR_FUNDO, borderwidth=0)
        self.style.configure('TNotebook.Tab', background="#D4D7D9", padding=[10, 5], font=("Segoe UI", 10))
        self.style.map('TNotebook.Tab', background=[('selected', COR_FUNDO_FRAME)])

        # Estilo para os Títulos
        self.style.configure('Title.TLabel', background=COR_FUNDO_FRAME, foreground=COR_PRIMARIA, font=("Segoe UI", 16, "bold"))
        
        # Estilo para os Botões
        self.style.configure('TButton', background=COR_PRIMARIA, foreground=COR_LETRA_BOTAO, font=("Segoe UI", 10, "bold"), padding=5)
        self.style.map('TButton', background=[('active', '#0056b3')])

        # Estilo para o botão Deletar
        self.style.configure('Delete.TButton', background=COR_DELETAR, foreground=COR_LETRA_BOTAO)
        self.style.map('Delete.TButton', background=[('active', '#c82333')])

        self.style.configure("Treeview", background=COR_FUNDO_FRAME, foreground="#263238", rowheight=25, fieldbackground=COR_FUNDO_FRAME)
        self.style.map("Treeview", background=[('selected', COR_PRIMARIA)])
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=5)

        # Estilo para a Tabela (Treeview)
        self.style.configure("Treeview", 
                             background=COR_FUNDO_FRAME, 
                             foreground=COR_LETRA,
                             rowheight=25, 
                             fieldbackground=COR_FUNDO_FRAME)
        self.style.map("Treeview", background=[('selected', COR_PRIMARIA)])
        
        # Estilo para o Cabeçalho da Tabela
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=5)

    def create_widgets(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Abas
        self.frame_veiculos = ttk.Frame(notebook, padding="10")
        notebook.add(self.frame_veiculos, text='Frota de Veículos')
        self.create_aba_veiculos()
        self.popular_tabela_veiculos()

        self.frame_usuarios = ttk.Frame(notebook, padding="10")
        notebook.add(self.frame_usuarios, text='Utilizadores')
        self.create_aba_usuarios()
        self.popular_tabela_usuarios()

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
        elif veiculos is None:
            messagebox.showerror("Erro de Conexão", "Não foi possível conectar à API para buscar veículos.")

    def editar_veiculo_selecionado(self):
        veiculo_id = self._get_selected_item_id(self.tree_veiculos)
        if not veiculo_id: return
        veiculos = self.api.listar_veiculos()
        if veiculos and 'erro' not in veiculos:
            veiculo_data = next((v for v in veiculos if v['id'] == veiculo_id), None)
            if veiculo_data:
                self.abrir_janela_cadastro_veiculo(veiculo=veiculo_data)
            else:
                messagebox.showerror("Erro", "Não foi possível encontrar os dados do veículo.")

    def deletar_veiculo_selecionado(self):
        veiculo_id = self._get_selected_item_id(self.tree_veiculos)
        if not veiculo_id:
            return
        
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o veículo selecionado?"):
            resultado = self.api.deletar_veiculo(veiculo_id)
            if 'erro' in resultado:
                messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Veículo excluído com sucesso!")
                self.popular_tabela_veiculos()

    # --- ABA DE UTILIZADORES ---
    def create_aba_usuarios(self):
        label_titulo = ttk.Label(self.frame_usuarios, text="Gestão de Utilizadores", style='Title.TLabel')
        label_titulo.pack(pady=10, anchor=tk.W)

        tree_container = ttk.Frame(self.frame_usuarios, style='TFrame')
        tree_container.pack(expand=True, fill='both')

        colunas = ('id', 'nome', 'email', 'cpf', 'funcao', 'detalhe')
        self.tree_usuarios = ttk.Treeview(tree_container, columns=colunas, show='headings')
        self.tree_usuarios.heading('id', text='ID'); self.tree_usuarios.column('id', width=40)
        self.tree_usuarios.heading('nome', text='Nome'); self.tree_usuarios.column('nome', width=200)
        self.tree_usuarios.heading('email', text='Email'); self.tree_usuarios.column('email', width=200)
        self.tree_usuarios.heading('cpf', text='CPF'); self.tree_usuarios.column('cpf', width=120)
        self.tree_usuarios.heading('funcao', text='Função'); self.tree_usuarios.column('funcao', width=80)
        self.tree_usuarios.heading('detalhe', text='Matrícula/CNH'); self.tree_usuarios.column('detalhe', width=120)
        self.tree_usuarios.pack(expand=True, fill='both', side=tk.LEFT)

        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_usuarios.yview)
        self.tree_usuarios.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        botoes_frame = ttk.Frame(self.frame_usuarios)
        botoes_frame.pack(pady=15, fill='x')
        ttk.Button(botoes_frame, text="Cadastrar Novo", command=self.abrir_janela_cadastro_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.popular_tabela_usuarios).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Editar Selecionado", command=self.editar_usuario_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Excluir Selecionado", command=self.deletar_usuario_selecionado, style='Delete.TButton').pack(side=tk.LEFT, padx=5)

    def abrir_janela_cadastro_usuario(self, usuario=None):
        CadastroUsuarioWindow(self, self.api, self.popular_tabela_usuarios, usuario_existente=usuario)

    def popular_tabela_usuarios(self):
        for i in self.tree_usuarios.get_children(): self.tree_usuarios.delete(i)
        usuarios = self.api.listar_usuarios()
        if usuarios and 'erro' not in usuarios:
            for u in usuarios:
                detalhe = u.get('matricula', '') if u['role'] == 'aluno' else u.get('cnh', '')
                self.tree_usuarios.insert('', tk.END, values=(u['id'], u['nome'], u['email'], u['cpf'], u['role'], detalhe))
        elif usuarios and 'erro' in usuarios:
            messagebox.showerror("Erro de API", f"Não foi possível buscar os usuários: {usuarios['erro']}")
        elif usuarios is None:
             messagebox.showerror("Erro de Conexão", "Não foi possível conectar à API para buscar usuários.")

    def editar_usuario_selecionado(self):
        usuario_id = self._get_selected_item_id(self.tree_usuarios)
        if not usuario_id: return
        usuarios = self.api.listar_usuarios()
        if usuarios and 'erro' not in usuarios:
            usuario_data = next((u for u in usuarios if u['id'] == usuario_id), None)
            if usuario_data:
                self.abrir_janela_cadastro_usuario(usuario=usuario_data)
            else:
                messagebox.showerror("Erro", "Não foi possível encontrar os dados do usuário.")

    def deletar_usuario_selecionado(self):
        usuario_id = self._get_selected_item_id(self.tree_usuarios)
        if not usuario_id:
            return

        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o usuário selecionado?"):
            resultado = self.api.deletar_usuario(usuario_id)
            if 'erro' in resultado:
                messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")
                self.popular_tabela_usuarios()

if __name__ == "__main__":
    app = App()
    app.mainloop()