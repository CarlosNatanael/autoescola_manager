import tkinter as tk
from tkinter import ttk, messagebox
from ..cadastro_usuario_window import CadastroUsuarioWindow

class AlunosView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent, padding="10")
        self.api = api_client
        
        self.style = ttk.Style(self)
        self.style.configure('View.TFrame', background='#FFFFFF')
        self.configure(style='View.TFrame')

        self.create_widgets()
        self.popular_tabela_alunos()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='View.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        label_titulo = ttk.Label(main_frame, text="Gestão de Alunos", style='Title.TLabel')
        label_titulo.pack(pady=10, anchor=tk.W)

        tree_container = ttk.Frame(main_frame, style='View.TFrame')
        tree_container.pack(expand=True, fill='both')

        # --- CORREÇÃO AQUI: Adicionar 'email' e 'cpf' de volta às colunas ---
        colunas = ('id', 'nome', 'email', 'cpf', 'matricula', 'categoria', 'saldo_praticas', 'saldo_simulador')
        self.tree_alunos = ttk.Treeview(tree_container, columns=colunas, show='headings')
        
        # Configuração das colunas
        self.tree_alunos.heading('id', text='ID'); self.tree_alunos.column('id', width=40)
        self.tree_alunos.heading('nome', text='Nome'); self.tree_alunos.column('nome', width=200)
        self.tree_alunos.heading('email', text='Email'); self.tree_alunos.column('email', width=200)
        self.tree_alunos.heading('cpf', text='CPF'); self.tree_alunos.column('cpf', width=110)
        self.tree_alunos.heading('matricula', text='Matrícula'); self.tree_alunos.column('matricula', width=80)
        self.tree_alunos.heading('categoria', text='Categoria'); self.tree_alunos.column('categoria', width=80, anchor=tk.CENTER)
        self.tree_alunos.heading('saldo_praticas', text='Saldo Práticas'); self.tree_alunos.column('saldo_praticas', width=120, anchor=tk.CENTER)
        self.tree_alunos.heading('saldo_simulador', text='Saldo Simulador'); self.tree_alunos.column('saldo_simulador', width=120, anchor=tk.CENTER)
        
        self.tree_alunos.pack(expand=True, fill='both', side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(tree_container, orient="vertical", command=self.tree_alunos.yview)
        self.tree_alunos.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        botoes_frame = ttk.Frame(main_frame, style='View.TFrame')
        botoes_frame.pack(pady=15, fill='x')

        ttk.Button(botoes_frame, text="Cadastrar Novo", command=lambda: self.abrir_janela_cadastro(None)).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.popular_tabela_alunos).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Editar Selecionado", command=self.editar_aluno_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Excluir Selecionado", command=self.deletar_aluno_selecionado, style='Delete.TButton').pack(side=tk.LEFT, padx=5)

    def popular_tabela_alunos(self):
        for i in self.tree_alunos.get_children():
            self.tree_alunos.delete(i)
        
        alunos = self.api.listar_alunos()
        if alunos and 'erro' not in alunos:
            for aluno in alunos:
                saldo_praticas_str = f"{aluno.get('aulas_praticas_feitas', 0)} de {aluno.get('aulas_praticas_contratadas', 0)}"
                saldo_simulador_str = f"{aluno.get('aulas_simulador_feitas', 0)} de {aluno.get('aulas_simulador_contratadas', 0)}"
                
                # --- CORREÇÃO AQUI: Adicionar os valores de 'email' e 'cpf' ---
                self.tree_alunos.insert('', tk.END, values=(
                    aluno['id'], 
                    aluno['nome'], 
                    aluno['email'],
                    aluno['cpf'],
                    aluno['matricula'], 
                    aluno.get('categoria', 'N/D'),
                    saldo_praticas_str,
                    saldo_simulador_str
                ))
        elif alunos and 'erro' in alunos:
            messagebox.showerror("Erro de API", f"Não foi possível buscar os alunos: {alunos['erro']}")
            
    def _get_selected_item_id(self):
        selection = self.tree_alunos.selection()
        if not selection:
            messagebox.showwarning("Nenhum Aluno Selecionado", "Por favor, selecione um aluno na lista primeiro.")
            return None
        item = self.tree_alunos.item(selection[0])
        return item['values'][0]

    def abrir_janela_cadastro(self, aluno=None):
        CadastroUsuarioWindow(self, self.api, self.popular_tabela_alunos, role='aluno', usuario_existente=aluno)

    def editar_aluno_selecionado(self):
        aluno_id = self._get_selected_item_id()
        if not aluno_id: return
        # A API já retorna todos os dados, então podemos filtrar a lista local
        alunos = self.api.listar_alunos() 
        if alunos and 'erro' not in alunos:
            aluno_data = next((a for a in alunos if a['id'] == aluno_id), None)
            if aluno_data:
                self.abrir_janela_cadastro(aluno=aluno_data)

    def deletar_aluno_selecionado(self):
        aluno_id = self._get_selected_item_id()
        if not aluno_id: return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o aluno selecionado?"):
            resultado = self.api.deletar_aluno(aluno_id)
            if 'erro' in resultado:
                messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Aluno excluído com sucesso!")
                self.popular_tabela_alunos()