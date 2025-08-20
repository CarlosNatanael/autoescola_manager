import tkinter as tk
from tkinter import ttk, messagebox
from .cadastro_aula_window import CadastroAulaWindow
from datetime import datetime

class AgendamentoTab(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api_client = api_client
        
        self.create_widgets()
        self.atualizar_lista_aulas()

    def create_widgets(self):
        # Frame de Ações
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, padx=10, pady=5)

        agendar_btn = ttk.Button(action_frame, text="Agendar Nova Aula", command=self.abrir_janela_agendamento)
        agendar_btn.pack(side=tk.LEFT)
        
        atualizar_btn = ttk.Button(action_frame, text="Atualizar Lista", command=self.atualizar_lista_aulas)
        atualizar_btn.pack(side=tk.RIGHT)

        editar_btn = ttk.Button(action_frame, text="Editar Aula", command=self.editar_aula_selecionada)
        editar_btn.pack(side=tk.LEFT, padx=5)
        
        excluir_btn = ttk.Button(action_frame, text="Excluir Aula", command=self.deletar_aula_selecionada, style='Delete.TButton')
        excluir_btn.pack(side=tk.LEFT, padx=5)

        # Tabela (Treeview) para exibir as aulas
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(tree_frame, columns=("data_hora", "aluno", "instrutor", "veiculo", "status"), show="headings")
        self.tree.heading("data_hora", text="Data e Hora")
        self.tree.heading("aluno", text="Aluno")
        self.tree.heading("instrutor", text="Instrutor")
        self.tree.heading("veiculo", text="Veículo")
        self.tree.heading("status", text="Status")

        # Ajuste das colunas
        self.tree.column("data_hora", width=150, anchor=tk.W)
        self.tree.column("status", width=80, anchor=tk.CENTER)

        self.tree.pack(fill=tk.BOTH, expand=True)

    def _get_selected_aula_data(self):
        """Pega os dados completos da aula selecionada na Treeview."""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Nenhuma Aula Selecionada", "Por favor, selecione uma aula na lista.")
            return None
        
        # Para pegar o ID, precisamos buscar os dados completos da API
        # Assumindo que a lista 'self.aulas_list' é preenchida em 'atualizar_lista_aulas'
        selected_item = self.tree.item(selection[0])
        data_hora_selecionada = selected_item['values'][0]

        if hasattr(self, 'aulas_list'):
            for aula in self.aulas_list:
                data_formatada = datetime.fromisoformat(aula['data_hora_inicio']).strftime('%d/%m/%Y %H:%M')
                if data_formatada == data_hora_selecionada:
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
        # Limpa a tabela antes de preencher
        for i in self.tree.get_children():
            self.tree.delete(i)
            
        aulas = self.api_client.listar_aulas()
        if aulas:
            for aula in aulas:
                # Formata a data para exibição
                data_formatada = datetime.fromisoformat(aula['data_hora_inicio']).strftime('%d/%m/%Y %H:%M')
                
                self.tree.insert("", tk.END, values=(
                    data_formatada,
                    aula['aluno']['nome'],
                    aula['instrutor']['nome'],
                    aula['veiculo']['placa'],
                    aula['status'].capitalize()
                ))

    def abrir_janela_agendamento(self):
        # O callback passado para a janela de agendamento é a própria função de atualizar a lista
        CadastroAulaWindow(self, self.api_client, self.atualizar_lista_aulas)