import tkinter as tk
from tkinter import ttk, font
import os

# --- Imports ---
from ui.views.agenda_completa_view import AgendaCompletaView
from ui.dashboard.agenda_dia_view import AgendaDiaView
from ui.views.instrutores_view import InstrutoresView
from ui.views.dashboard_view import DashboardView
from ui.views.veiculos_view import VeiculosView
from ui.views.alunos_view import AlunosView
from ui.login_window import LoginWindow
from api_client import ApiCliente

class App(tk.Toplevel):
    def __init__(self, master, api_client):
        super().__init__(master)
        self.title("Gestão de Autoescola")
        self.geometry("1200x700")

        try:
            script_dir = os.path.dirname(__file__)
            icon_path = os.path.join(script_dir, "..", "icone.ico")
            if not os.path.exists(icon_path):
                 icon_path = os.path.join(script_dir, "icone.ico")
            self.iconbitmap(icon_path)
        except tk.TclError:
            print("Aviso: Arquivo 'icone.ico' não encontrado.")

        self.api = api_client
        self.style = ttk.Style(self)
        self.style.theme_use('clam')
        self.configure_styles()
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.create_widgets()
        # --- Iniciar mostrando o Dashboard ---
        self.show_view(DashboardView)

    def configure_styles(self):
        COR_FUNDO = "#ECEFF1"
        COR_FUNDO_FRAME = "#FFFFFF"
        self.configure(background=COR_FUNDO)
        self.style.configure('TFrame', background=COR_FUNDO)
        self.style.configure('Toolbar.TFrame', background='#343a40')
        self.style.configure('View.TFrame', background=COR_FUNDO_FRAME) 
        self.style.configure('Title.TLabel', background=COR_FUNDO_FRAME, foreground="#007BFF", font=("Segoe UI", 16, "bold"))
        self.style.configure('Toolbar.TButton', background='#343a40', foreground='white', font=("Segoe UI", 10, "bold"), padding=10)
        self.style.map('Toolbar.TButton', background=[('active', '#495057'), ('pressed', '#212529')])
        self.style.configure('Card.TFrame', background='#F8F9FA', relief='solid', borderwidth=1)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), padding=5)


    def create_widgets(self):
        toolbar_frame = ttk.Frame(self.main_frame, style='Toolbar.TFrame')
        toolbar_frame.pack(side=tk.TOP, fill=tk.X)


        btn_dashboard = ttk.Button(toolbar_frame, text="Dashboard", style='Toolbar.TButton', command=lambda: self.show_view
        (DashboardView))
        btn_dashboard.pack(side=tk.LEFT, padx=2, pady=2)
        btn_alunos = ttk.Button(toolbar_frame, text="Alunos", style='Toolbar.TButton', command=lambda: self.show_view
        (AlunosView))
        btn_alunos.pack(side=tk.LEFT, padx=2, pady=2)
        btn_instrutores = ttk.Button(toolbar_frame, text="Instrutores", style='Toolbar.TButton', command=lambda: self.show_view(InstrutoresView))
        btn_instrutores.pack(side=tk.LEFT, padx=2, pady=2)
        btn_veiculos = ttk.Button(toolbar_frame, text="Veículos", style='Toolbar.TButton', command=lambda: self.show_view
        (VeiculosView))
        btn_veiculos.pack(side=tk.LEFT, padx=2, pady=2)
        btn_agenda = ttk.Button(toolbar_frame, text="Agenda Completa", style='Toolbar.TButton',command=lambda: self.show_view(AgendaCompletaView))
        btn_agenda.pack(side=tk.LEFT, padx=2, pady=2)

        paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        self.content_frame = ttk.Frame(paned_window, style='View.TFrame')
        paned_window.add(self.content_frame, weight=3) 

        dashboard_container = ttk.Frame(paned_window, style='View.TFrame')
        paned_window.add(dashboard_container, weight=1)

        agenda_view = AgendaDiaView(dashboard_container, self.api)
        agenda_view.pack(fill=tk.BOTH, expand=True)

    def show_view(self, ViewClass):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        view = ViewClass(self.content_frame, self.api)
        view.pack(fill=tk.BOTH, expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    api = ApiCliente()

    def on_login_success():
        main_app = App(root, api)
        main_app.protocol("WM_DELETE_WINDOW", root.destroy)

    login_window = LoginWindow(root, api, on_login_success)
    root.deiconify()
    root.overrideredirect(True)
    root.geometry("0x0+9999+9999")
    login_window.focus_force()

    root.mainloop()