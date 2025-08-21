import tkinter as tk
from tkinter import ttk, messagebox
from ..cadastro_veiculo_window import CadastroVeiculoWindow

class VeiculosView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent, padding="10")
        self.api = api_client
        
        # Estilo para o frame interno para corresponder ao fundo branco
        self.style = ttk.Style(self)
        self.style.configure('View.TFrame', background='#FFFFFF')
        self.configure(style='View.TFrame')

        self.create_widgets()
        self.popular_tabela_veiculos()

    def create_widgets(self):
        # Frame principal que ocupará todo o espaço da view
        main_frame = ttk.Frame(self, style='View.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        label_titulo = ttk.Label(main_frame, text="Gestão da Frota de Veículos", style='Title.TLabel')
        label_titulo.pack(pady=10, anchor=tk.W)

        tree_container = ttk.Frame(main_frame, style='View.TFrame')
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

        botoes_frame = ttk.Frame(main_frame, style='View.TFrame')
        botoes_frame.pack(pady=15, fill='x')

        ttk.Button(botoes_frame, text="Cadastrar Novo", command=self.abrir_janela_cadastro_veiculo).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.popular_tabela_veiculos).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Editar Selecionado", command=self.editar_veiculo_selecionado).pack(side=tk.LEFT, padx=5)
        ttk.Button(botoes_frame, text="Excluir Selecionado", command=self.deletar_veiculo_selecionado, style='Delete.TButton').pack(side=tk.LEFT, padx=5)

    def _get_selected_item_id(self, tree):
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("Nenhum Item Selecionado", "Por favor, selecione um item na lista primeiro.")
            return None
        item = tree.item(selection[0])
        return item['values'][0]

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
            else:
                messagebox.showerror("Erro", "Não foi possível encontrar os dados do veículo.")

    def deletar_veiculo_selecionado(self):
        veiculo_id = self._get_selected_item_id(self.tree_veiculos)
        if not veiculo_id: return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir o veículo selecionado?"):
            resultado = self.api.deletar_veiculo(veiculo_id)
            if 'erro' in resultado:
                messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Veículo excluído com sucesso!")
                self.popular_tabela_veiculos()