import tkinter as tk
from tkinter import ttk, messagebox
from api_client import ApiCliente
from ui.cadastro_veiculo_window import CadastroVeiculoWindow
from ui.cadastro_usuario_window import CadastroUsuarioWindow
from ui.agendamento_tab import AgendamentoTab

class App(tk.Tk):
    """
    Aplicação principal da interface de administração.
    """
    def __init__(self):
        super().__init__()
        self.title("Gestão de Autoescola")
        self.geometry("900x600")
        self.api = ApiCliente()
        self.create_widgets()

    def create_widgets(self):
        # Cria o widget de abas (Notebook)
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # Cria o frame para cada aba
        self.frame_veiculos = ttk.Frame(notebook, padding="10")
        self.frame_usuarios = ttk.Frame(notebook, padding="10")
        self.frame_agendamentos = ttk.Frame(notebook, padding="10")

        notebook.add(self.frame_veiculos, text='Frota de Veículos')
        notebook.add(self.frame_usuarios, text='Utilizadores')
        notebook.add(self.frame_agendamentos, text="Agendamento de Aulas")

        # Popula cada aba com os seus widgets
        self.create_aba_veiculos()
        self.create_aba_usuarios()

        # Carrega os dados iniciais
        self.popular_tabela_veiculos()
        self.popular_tabela_usuarios()

    # --- ABA DE VEÍCULOS ---
    def create_aba_veiculos(self):
        label_titulo = ttk.Label(self.frame_veiculos, text="Gestão da Frota", font=("Helvetica", 16))
        label_titulo.pack(pady=10, anchor=tk.W)

        colunas = ('id', 'placa', 'modelo', 'marca', 'ano', 'tipo')
        self.tree_veiculos = ttk.Treeview(self.frame_veiculos, columns=colunas, show='headings')
        self.tree_veiculos.heading('id', text='ID'); self.tree_veiculos.column('id', width=40)
        self.tree_veiculos.heading('placa', text='Placa'); self.tree_veiculos.column('placa', width=100)
        self.tree_veiculos.heading('modelo', text='Modelo'); self.tree_veiculos.column('modelo', width=150)
        self.tree_veiculos.heading('marca', text='Marca'); self.tree_veiculos.column('marca', width=150)
        self.tree_veiculos.heading('ano', text='Ano'); self.tree_veiculos.column('ano', width=60)
        self.tree_veiculos.heading('tipo', text='Tipo'); self.tree_veiculos.column('tipo', width=80)
        self.tree_veiculos.pack(expand=True, fill='both')

        botoes_frame = ttk.Frame(self.frame_veiculos)
        botoes_frame.pack(pady=10, fill='x')
        ttk.Button(botoes_frame, text="Cadastrar Novo Veículo", command=self.abrir_janela_cadastro_veiculo).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.popular_tabela_veiculos).pack(side=tk.LEFT, padx=5)

    def abrir_janela_cadastro_veiculo(self):
        CadastroVeiculoWindow(self, self.api, self.popular_tabela_veiculos)

    def popular_tabela_veiculos(self):
        for i in self.tree_veiculos.get_children(): self.tree_veiculos.delete(i)
        veiculos = self.api.listar_veiculos()
        if veiculos:
            for v in veiculos:
                self.tree_veiculos.insert('', tk.END, values=(v['id'], v['placa'], v['modelo'], v.get('marca', ''), v.get('ano', ''), v.get('tipo', '')))
        elif veiculos is None:
            messagebox.showerror("Erro de Conexão", "Não foi possível buscar os dados de veículos.")

    # --- ABA DE UTILIZADORES ---
    def create_aba_usuarios(self):
        label_titulo = ttk.Label(self.frame_usuarios, text="Gestão de Utilizadores", font=("Helvetica", 16))
        label_titulo.pack(pady=10, anchor=tk.W)

        colunas = ('id', 'nome', 'email', 'cpf', 'funcao', 'detalhe')
        self.tree_usuarios = ttk.Treeview(self.frame_usuarios, columns=colunas, show='headings')
        self.tree_usuarios.heading('id', text='ID'); self.tree_usuarios.column('id', width=40)
        self.tree_usuarios.heading('nome', text='Nome'); self.tree_usuarios.column('nome', width=200)
        self.tree_usuarios.heading('email', text='Email'); self.tree_usuarios.column('email', width=200)
        self.tree_usuarios.heading('cpf', text='CPF'); self.tree_usuarios.column('cpf', width=120)
        self.tree_usuarios.heading('funcao', text='Função'); self.tree_usuarios.column('funcao', width=80)
        self.tree_usuarios.heading('detalhe', text='Matrícula/CNH'); self.tree_usuarios.column('detalhe', width=120)
        self.tree_usuarios.pack(expand=True, fill='both')

        botoes_frame = ttk.Frame(self.frame_usuarios)
        botoes_frame.pack(pady=10, fill='x')
        ttk.Button(botoes_frame, text="Cadastrar Novo Utilizador", command=self.abrir_janela_cadastro_usuario).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.popular_tabela_usuarios).pack(side=tk.LEFT, padx=5)

    def abrir_janela_cadastro_usuario(self):
        CadastroUsuarioWindow(self, self.api, self.popular_tabela_usuarios)

    def popular_tabela_usuarios(self):
        for i in self.tree_usuarios.get_children(): self.tree_usuarios.delete(i)
        usuarios = self.api.listar_usuarios()
        if usuarios:
            for u in usuarios:
                detalhe = u.get('matricula', '') if u['role'] == 'aluno' else u.get('cnh', '')
                self.tree_usuarios.insert('', tk.END, values=(u['id'], u['nome'], u['email'], u['cpf'], u['role'], detalhe))
        elif usuarios is None:
             messagebox.showerror("Erro de Conexão", "Não foi possível buscar os dados de utilizadores.")

if __name__ == "__main__":
    app = App()
    app.mainloop()