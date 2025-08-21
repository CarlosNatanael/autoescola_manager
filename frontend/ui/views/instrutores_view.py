import tkinter as tk
from tkinter import ttk, messagebox
from ..cadastro_usuario_window import CadastroUsuarioWindow

class InstrutoresView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent, padding="10")
        self.api = api_client
        
        self.style = ttk.Style(self)
        self.style.configure('View.TFrame', background='#FFFFFF')
        self.configure(style='View.TFrame')

        self.create_widgets()
        self.popular_tabela_instrutores()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='View.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        label_titulo = ttk.Label(main_frame, text="Gestão de Instrutores", style='Title.TLabel')
        label_titulo.pack(pady=10, anchor=tk.W)

        tree_container = ttk.Frame(main_frame, style='View.TFrame')
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

        botoes_frame = ttk.Frame(main_frame, style='View.TFrame')
        botoes_frame.pack(pady=15, fill='x')

        ttk.Button(botoes_frame, text="Cadastrar Novo", command=lambda: self.abrir_janela_cadastro(None)).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.popular_tabela_instrutores).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Editar Selecionado", command=self.editar_instrutor_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Excluir Selecionado", command=self.deletar_instrutor_selecionado, style='Delete.TButton').pack(side=tk.LEFT, padx=5)

    def _get_selected_item_id(self):
        selection = self.tree_instrutores.selection()
        if not selection:
            messagebox.showwarning("Nenhum Instrutor Selecionado", "Por favor, selecione um instrutor na lista primeiro.")
            return None
        item = self.tree_instrutores.item(selection[0])
        return item['values'][0]

    def abrir_janela_cadastro(self, instrutor=None):
        CadastroUsuarioWindow(self, self.api, self.popular_tabela_instrutores, role='instrutor', usuario_existente=instrutor)

    def popular_tabela_instrutores(self):
        for i in self.tree_instrutores.get_children(): self.tree_instrutores.delete(i)
        instrutores = self.api.listar_instrutores()
        if instrutores and 'erro' not in instrutores:
            for instrutor in instrutores:
                self.tree_instrutores.insert('', tk.END, values=(instrutor['id'], instrutor['nome'], instrutor['email'], instrutor['cpf'], instrutor['cnh']))
        elif instrutores and 'erro' in instrutores:
            messagebox.showerror("Erro de API", f"Não foi possível buscar os instrutores: {instrutores['erro']}")

    def editar_instrutor_selecionado(self):
        instrutor_id = self._get_selected_item_id()
        if not instrutor_id: return
        instrutores = self.api.listar_instrutores()
        if instrutores and 'erro' not in instrutores:
            instrutor_data = next((i for i in instrutores if i['id'] == instrutor_id), None)
            if instrutor_data:
                self.abrir_janela_cadastro(instrutor=instrutor_data)

    def deletar_instrutor_selecionado(self):
        instrutor_id = self._get_selected_item_id()
        if not instrutor_id: return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o instrutor selecionado?"):
            resultado = self.api.deletar_instrutor(instrutor_id)
            if 'erro' in resultado:
                messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Instrutor excluído com sucesso!")
                self.popular_tabela_instrutores()