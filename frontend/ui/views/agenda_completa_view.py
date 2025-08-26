import tkinter as tk
from tkinter import ttk, messagebox
from ..cadastro_aula_window import CadastroAulaWindow
from datetime import datetime
from tkcalendar import Calendar

class AgendaCompletaView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent, padding="10")
        self.api = api_client
        self.todas_as_aulas = []

        # Estilos
        self.style = ttk.Style(self)
        self.style.configure('View.TFrame', background='#FFFFFF')
        self.configure(style='View.TFrame')
        
        self.create_widgets()
        self.atualizar_lista_aulas()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='View.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        left_panel = ttk.Frame(main_frame, style='View.TFrame')
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.cal = Calendar(left_panel, selectmode='day', locale='pt_BR')
        self.cal.pack(pady=10, padx=10)
        self.cal.bind("<<CalendarSelected>>", self.filtrar_aulas_por_data)

        ttk.Button(left_panel, text="Mostrar Todas as Aulas", command=self.mostrar_todas_as_aulas).pack(pady=10)

        right_panel = ttk.Frame(main_frame, style='View.TFrame')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        action_frame = ttk.Frame(right_panel, style='View.TFrame')
        action_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Button(action_frame, text="Agendar Nova Aula", command=self.abrir_janela_agendamento).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(action_frame, text="Editar Aula", command=self.editar_aula_selecionada).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Excluir Aula", command=self.deletar_aula_selecionada, style='Delete.TButton').pack(side=tk.LEFT, padx=5)

        tree_frame = ttk.Frame(right_panel, style='View.TFrame')
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

    def filtrar_aulas_por_data(self, event=None):
        data_selecionada = self.cal.get_date() 

        for i in self.tree.get_children():
            self.tree.delete(i)

        for aula in self.todas_as_aulas:
            data_aula = datetime.fromisoformat(aula['data_hora_inicio']).strftime('%d/%m/%Y')
            if data_aula == data_selecionada:
                self.inserir_aula_na_tabela(aula)

    def mostrar_todas_as_aulas(self):
        # Limpa a tabela
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Re-insere todas as aulas
        for aula in self.todas_as_aulas:
            self.inserir_aula_na_tabela(aula)

    def inserir_aula_na_tabela(self, aula):
        data_formatada = datetime.fromisoformat(aula['data_hora_inicio']).strftime('%d/%m/%Y %H:%M')
        self.tree.insert("", tk.END, values=(
            aula['id'], data_formatada, aula['aluno']['nome'],
            aula['instrutor']['nome'], aula['veiculo']['placa'],
            aula['status'].capitalize()
        ))

    def _get_selected_aula_data(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Nenhuma Aula Selecionada", "Por favor, selecione uma aula na lista.")
            return None
        
        selected_id = self.tree.item(selection[0])['values'][0]
        for aula in self.todas_as_aulas:
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
        self.todas_as_aulas = self.api.listar_aulas()
        if 'erro' in self.todas_as_aulas:
            messagebox.showerror("Erro de API", "Não foi possível carregar as aulas.")
            self.todas_as_aulas = []
        
        self.mostrar_todas_as_aulas()