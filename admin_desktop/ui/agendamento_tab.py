import tkinter as tk
from tkinter import ttk, messagebox
from .cadastro_aula_window import CadastroAulaWindow
from datetime import datetime

class AgendamentoTab(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        self.aulas_list = [] # Inicializa a lista de aulas
        
        self.create_widgets()
        self.atualizar_lista_aulas()

    def create_widgets(self):
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        # Reorganizei a ordem dos botões para ficar mais lógico
        ttk.Button(action_frame, text="Agendar Nova Aula", command=self.abrir_janela_agendamento).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Editar Aula", command=self.editar_aula_selecionada).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Excluir Aula", command=self.deletar_aula_selecionada, style='Delete.TButton').pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Atualizar Lista", command=self.atualizar_lista_aulas).pack(side=tk.RIGHT, padx=5)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # CORREÇÃO: Adicionamos a coluna 'id' mas vamos escondê-la
        self.tree = ttk.Treeview(tree_frame, columns=("id", "data_hora", "aluno", "instrutor", "veiculo", "status"), show="headings")
        self.tree['displaycolumns'] = ("data_hora", "aluno", "instrutor", "veiculo", "status")

        self.tree.heading("data_hora", text="Data e Hora")
        self.tree.heading("aluno", text="Aluno")
        self.tree.heading("instrutor", text="Instrutor")
        self.tree.heading("veiculo", text="Veículo")
        self.tree.heading("status", text="Status")

        self.tree.column("data_hora", width=150, anchor=tk.W)
        self.tree.column("status", width=80, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def _get_selected_aula_data(self):
        """Pega os dados da aula selecionada de forma mais segura."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Nenhuma Aula Selecionada", "Por favor, selecione uma aula na lista.")
            return None
        
        # CORREÇÃO: Pega o ID diretamente da linha da tabela
        selected_id = self.tree.item(selection[0])['values'][0]

        # Encontra a aula correspondente na nossa lista de dados
        for aula in self.aulas_list:
            if aula['id'] == selected_id:
                return aula
        return None

    def editar_aula_selecionada(self):
        aula_data = self._get_selected_aula_data()
        if aula_data:
            CadastroAulaWindow(self, self.api_client, self.atualizar_lista_aulas, aula_existente=aula_data)

    def deletar_aula_selecionada(self):
        aula_data = self._get_selected_aula_data()
        if not aula_data:
            return

        if messagebox.askyesno("Confirmar Exclusão", "Tem certeza que deseja excluir a aula selecionada?"):
            resultado = self.api_client.deletar_aula(aula_data['id'])
            if 'erro' in resultado:
                messagebox.showerror("Erro ao Excluir", resultado['erro'])
            else:
                messagebox.showinfo("Sucesso", "Aula excluída com sucesso!")
                self.atualizar_lista_aulas()

    def atualizar_lista_aulas(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        # CORREÇÃO: Armazena a lista completa de aulas
        self.aulas_list = self.api_client.listar_aulas()

        if self.aulas_list and 'erro' not in self.aulas_list:
            for aula in self.aulas_list:
                data_formatada = datetime.fromisoformat(aula['data_hora_inicio']).strftime('%d/%m/%Y %H:%M')
                
                # CORREÇÃO: Passa o ID da aula como primeiro valor
                self.tree.insert("", tk.END, values=(
                    aula['id'],
                    data_formatada,
                    aula['aluno']['nome'],
                    aula['instrutor']['nome'],
                    aula['veiculo']['placa'],
                    aula['status'].capitalize()
                ))

    def abrir_janela_agendamento(self):
        CadastroAulaWindow(self, self.api_client, self.atualizar_lista_aulas)