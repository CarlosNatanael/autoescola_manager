import tkinter as tk
from tkinter import ttk

class DashboardView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent, padding="10")
        self.api = api_client

        self.style = ttk.Style(self)
        self.style.configure('View.TFrame', background='#FFFFFF')
        self.configure(style='View.TFrame')

        # Variáveis para guardar os valores dos KPIs
        self.total_alunos_var = tk.StringVar(value="--")

        self.create_widgets()
        self.carregar_stats()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='View.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        label_titulo = ttk.Label(main_frame, text="Dashboard Geral", style='Title.TLabel')
        label_titulo.pack(pady=10, anchor=tk.W)

        # --- Painel de KPIs (Indicadores) ---
        kpi_frame = ttk.Frame(main_frame, style='View.TFrame')
        kpi_frame.pack(fill=tk.X, pady=10)

        # Card de Alunos Ativos
        card_alunos = ttk.Frame(kpi_frame, style='Card.TFrame', padding=15)
        card_alunos.pack(side=tk.LEFT, padx=(0, 10))

        label_alunos_valor = ttk.Label(card_alunos, textvariable=self.total_alunos_var, font=("Segoe UI", 24, "bold"), foreground="#007BFF")
        label_alunos_valor.pack()
        label_alunos_titulo = ttk.Label(card_alunos, text="Alunos Ativos")
        label_alunos_titulo.pack()

        # (Poderíamos adicionar outros cards aqui no futuro)

        # --- Painel para Gráficos ---
        graficos_frame = ttk.Frame(main_frame, style='View.TFrame')
        graficos_frame.pack(fill=tk.BOTH, expand=True, pady=20)

        label_graficos = ttk.Label(graficos_frame, text="Relatórios Gráficos (em desenvolvimento)", style='Title.TLabel', font=("Segoe UI", 12))
        label_graficos.pack()

    def carregar_stats(self):
        stats = self.api.get_dashboard_stats()
        if stats and 'erro' not in stats:
            self.total_alunos_var.set(stats.get('total_alunos', '--'))
        else:
            self.total_alunos_var.set("Erro")