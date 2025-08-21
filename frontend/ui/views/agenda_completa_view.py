import tkinter as tk
from tkinter import ttk, messagebox
from ..cadastro_aula_window import CadastroAulaWindow
from datetime import datetime

class AgendaCompletaView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent, padding="10")
        self.api = api_client
        self.aulas_list = []

        # Estilos
        self.style = ttk.Style(self)
        self.style.configure('View.TFrame', background='#FFFFFF')
        self.configure(style='View.TFrame')
        
        self.create_widgets()
        self.atualizar_lista_aulas()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='View.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Frame para os botões de ação
        action_frame = ttk.Frame(main_frame, style='View.TFrame')
        action_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(action_frame, text="Agendar Nova Aula", command=self.abrir_janela_agendamento).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Editar Aula Selecionada", command=self.editar_aula_selecionada).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Excluir Aula Selecionada", command=self.deletar_aula_selecionada, style='Delete.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Atualizar Lista", command=self.atualizar_lista_aulas).pack(side=tk.RIGHT, padx=5)

        # Container da Tabela
        tree_frame = ttk.Frame(main_frame, style='View.TFrame')
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        colunas = ("id", "data_hora", "aluno", "instrutor", "veiculo", "status")
        self.tree = ttk.Treeview(tree_frame, columns=colunas, show="headings")
        self.tree['displaycolumns'] = ("data_hora", "aluno", "instrutor", "veiculo", "status")

        self.tree.heading("data_hora", text="Data e Hora")
        self.tree.heading("aluno", text="Aluno")
        self.tree.heading("instrutor", text="Instrutor")
        self.tree.heading("veiculo", text="Veículo")
        self.tree.heading("status", text="Status")

        self.tree.column("data_hora", width=150, anchor=tk.W)
        self.tree.column("status", width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _get_selected_aula_data(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Nenhuma Aula Selecionada", "Por favor, selecione uma aula na lista.")
            return None
        
        selected_id = self.tree.item(selection[0])['values'][0]
        for aula in self.aulas_list:
            if aula['id'] == selected_id:
                return aula
        return None

    def abrir_janela_agendamento(self, aula=None):
        CadastroAulaWindow(self, self.api, self.atualizar_lista_aulas, aula_existente=aula)

    def editar_aula_selecionada(self):
        aula_data = self._get_selected_aula_data()
        if aula_data:
            self.abrir_janela_agendamento(aula=aula_data)

    def deletar_aula_selecionada(self):
        aula_data = self._get_selected_aula_data()
        if not aula_data: return
        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir a aula selecionada?"):
            resultado = self.api.deletar_aula(aula_data['id'])
            if 'erro' in resultado:
                messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Aula excluída com sucesso!")
                self.atualizar_lista_aulas()

    def atualizar_lista_aulas(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        self.aulas_list = self.api.listar_aulas() # Usa o endpoint que lista TODAS as aulas

        if self.aulas_list and 'erro' not in self.aulas_list:
            for aula in self.aulas_list:
                data_formatada = datetime.fromisoformat(aula['data_hora_inicio']).strftime('%d/%m/%Y %H:%M')
                self.tree.insert("", tk.END, values=(
                    aula['id'], data_formatada, aula['aluno']['nome'],
                    aula['instrutor']['nome'], aula['veiculo']['placa'],
                    aula['status'].capitalize()
                ))