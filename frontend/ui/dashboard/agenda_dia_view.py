import tkinter as tk
from tkinter import ttk
from datetime import datetime

class AgendaDiaView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent)
        self.api = api_client
        
        # Estilos
        self.style = ttk.Style(self)
        self.style.configure('Dashboard.TFrame', background='#FFFFFF')
        self.style.configure('Dashboard.TLabel', background='#FFFFFF')
        self.configure(style='Dashboard.TFrame')

        self.create_widgets()
        self.popular_tabela()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='Dashboard.TFrame', padding=(10, 10))
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título com data
        hoje = datetime.now().strftime("%d de %B de %Y")
        label_titulo = ttk.Label(main_frame, text=f"Agenda de Hoje ({hoje})", font=("Segoe UI", 12, "bold"), style='Dashboard.TLabel')
        label_titulo.pack(pady=(0, 10), anchor=tk.W)

        # Tabela (Treeview)
        colunas = ('hora', 'aluno', 'instrutor', 'status')
        self.tree_aulas = ttk.Treeview(main_frame, columns=colunas, show='headings', height=5) # height controla o tamanho inicial
        self.tree_aulas.heading('hora', text='Hora'); self.tree_aulas.column('hora', width=60, anchor=tk.CENTER)
        self.tree_aulas.heading('aluno', text='Aluno'); self.tree_aulas.column('aluno', width=120)
        self.tree_aulas.heading('instrutor', text='Instrutor'); self.tree_aulas.column('instrutor', width=120)
        self.tree_aulas.heading('status', text='Status'); self.tree_aulas.column('status', width=80, anchor=tk.CENTER)
        self.tree_aulas.pack(expand=True, fill='both')

        # Botão para atualizar manualmente
        btn_atualizar = ttk.Button(main_frame, text="Atualizar Agenda", command=self.popular_tabela)
        btn_atualizar.pack(pady=10)

    def popular_tabela(self):
        # Limpa a tabela antes de popular
        for i in self.tree_aulas.get_children():
            self.tree_aulas.delete(i)
        
        aulas_hoje = self.api.listar_aulas_hoje()

        if aulas_hoje and 'erro' not in aulas_hoje:
            for aula in aulas_hoje:
                hora = datetime.fromisoformat(aula['data_hora_inicio']).strftime('%H:%M')
                aluno = aula['aluno']['nome']
                instrutor = aula['instrutor']['nome']
                status = aula['status'].capitalize()
                self.tree_aulas.insert('', tk.END, values=(hora, aluno, instrutor, status))

        # Agenda a próxima atualização automática para daqui a 5 minutos (300000 ms)
        self.after(300000, self.popular_tabela)