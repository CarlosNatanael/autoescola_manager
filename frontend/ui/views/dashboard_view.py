import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DashboardView(ttk.Frame):
    def __init__(self, parent, api_client):
        super().__init__(parent, padding="10")
        self.api = api_client
        
        self.style = ttk.Style(self)
        self.style.configure('View.TFrame', background='#FFFFFF')
        self.configure(style='View.TFrame')

        self.total_alunos_var = tk.StringVar(value="--")
        self.total_instrutores_var = tk.StringVar(value="--")
        self.total_veiculos_var = tk.StringVar(value="--")
        self.aulas_mes_var = tk.StringVar(value="--")

        self.create_widgets()
        self.carregar_dados_dashboard()

    def create_widgets(self):
        main_frame = ttk.Frame(self, style='View.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame, style='View.TFrame')
        header_frame.pack(fill=tk.X)

        label_titulo = ttk.Label(header_frame, text="Dashboard Geral", style='Title.TLabel')
        label_titulo.pack(side=tk.LEFT, pady=10)
        
        ttk.Button(header_frame, text="Atualizar Dados", command=self.carregar_dados_dashboard).pack(side=tk.RIGHT)

        kpi_frame = ttk.Frame(main_frame, style='View.TFrame')
        kpi_frame.pack(fill=tk.X, pady=10, anchor=tk.N)
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.criar_card(kpi_frame, self.total_alunos_var, "Alunos Ativos", 0)
        self.criar_card(kpi_frame, self.total_instrutores_var, "Instrutores", 1)
        self.criar_card(kpi_frame, self.total_veiculos_var, "Veículos em Operação", 2)
        self.criar_card(kpi_frame, self.aulas_mes_var, "Aulas Concluídas no Mês", 3)

        # --- Painel para Gráficos ---
        self.graficos_frame = ttk.Frame(main_frame, style='View.TFrame')
        self.graficos_frame.pack(fill=tk.BOTH, expand=True, pady=20)

    def criar_card(self, parent, text_variable, title, column):
        """Função auxiliar para criar um card de KPI."""
        card_frame = ttk.Frame(parent, style='Card.TFrame', padding=15)
        card_frame.grid(row=0, column=column, padx=10, sticky="ew")

        label_valor = ttk.Label(card_frame, textvariable=text_variable, font=("Segoe UI", 24, "bold"), foreground="#007BFF", anchor="center")
        label_valor.pack(pady=(0, 5))
        label_titulo = ttk.Label(card_frame, text=title, anchor="center")
        label_titulo.pack()

    def carregar_dados_dashboard(self):
        """Carrega todos os dados para o dashboard, incluindo KPIs e gráficos."""
        # Carregar KPIs
        stats = self.api.get_dashboard_stats()
        if stats and 'erro' not in stats:
            self.total_alunos_var.set(stats.get('total_alunos', '--'))
            self.total_instrutores_var.set(stats.get('total_instrutores', '--'))
            self.total_veiculos_var.set(stats.get('total_veiculos_ativos', '--'))
            self.aulas_mes_var.set(stats.get('aulas_concluidas_mes', '--'))
        else:
            self.total_alunos_var.set("Erro")
            self.total_instrutores_var.set("Erro")
            self.total_veiculos_var.set("Erro")
            self.aulas_mes_var.set("Erro")
        
        # Limpa os gráficos antigos antes de desenhar os novos
        for widget in self.graficos_frame.winfo_children():
            widget.destroy()

        # Carregar e desenhar gráficos
        self.desenhar_grafico_aulas_mes()
        self.desenhar_grafico_aulas_instrutor()

    def desenhar_grafico_aulas_mes(self):
        dados = self.api.get_aulas_por_mes()
        if not dados or 'erro' in dados:
            ttk.Label(self.graficos_frame, text="Não foi possível carregar o gráfico de aulas por mês.").pack()
            return

        meses = [item['mes'] for item in dados]
        aulas = [item['aulas'] for item in dados]

        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.bar(meses, aulas, color='#007BFF')
        ax.set_title("Aulas Concluídas nos Últimos 6 Meses")
        ax.set_ylabel("Nº de Aulas")
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.graficos_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    
    def desenhar_grafico_aulas_instrutor(self):
        dados = self.api.get_aulas_por_instrutor()
        if not dados or 'erro' in dados:
            ttk.Label(self.graficos_frame, text="Não foi possível carregar o gráfico de aulas por instrutor.").pack()
            return
            
        nomes = [item['instrutor'] for item in dados]
        aulas = [item['aulas'] for item in dados]

        fig = Figure(figsize=(5, 4), dpi=100)
        ax = fig.add_subplot(111)
        ax.pie(aulas, labels=nomes, autopct='%1.1f%%', startangle=90)
        ax.set_title("Distribuição de Aulas por Instrutor (Mês Atual)")
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, master=self.graficos_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)