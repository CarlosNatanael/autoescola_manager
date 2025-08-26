import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from tkcalendar import DateEntry

class CadastroAulaWindow(tk.Toplevel):
    def __init__(self, parent, api_client, callback_sucesso, aula_existente=None):
        super().__init__(parent)
        
        self.api_client = api_client
        self.callback_sucesso = callback_sucesso
        self.aula_existente = aula_existente

        # Armazenamento de dados
        self.todos_veiculos = []
        self.aluno_map = {}
        self.instrutor_map = {}
        self.veiculo_map = {}

        self.title("Editar Aula" if self.aula_existente else "Agendar Nova Aula")
        self.geometry("550x300")
        self.iconbitmap("icone.ico")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.carregar_dados_iniciais()
        
        if self.aula_existente:
            self.preencher_dados()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Aluno:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.aluno_combo = ttk.Combobox(frame, state="readonly", width=40)
        self.aluno_combo.grid(row=0, column=1, sticky=tk.EW, pady=5)
        self.aluno_combo.bind("<<ComboboxSelected>>", self.on_aluno_selecionado)

        ttk.Label(frame, text="Instrutor:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.instrutor_combo = ttk.Combobox(frame, state="readonly", width=40)
        self.instrutor_combo.grid(row=1, column=1, sticky=tk.EW, pady=5)

        ttk.Label(frame, text="Veículo:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.veiculo_combo = ttk.Combobox(frame, state="readonly", width=40)
        self.veiculo_combo.grid(row=2, column=1, sticky=tk.EW, pady=5)
        self.veiculo_combo.set("Selecione um aluno primeiro...")

        ttk.Label(frame, text="Data:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.data_entry = DateEntry(frame, width=18, background='darkblue', foreground='white', borderwidth=2, date_pattern='dd/mm/yyyy')
        self.data_entry.grid(row=3, column=1, sticky=tk.W, pady=5)

        ttk.Label(frame, text="Hora:").grid(row=3, column=1, sticky=tk.E, padx=(0, 90))
        # Gera uma lista de horários de 30 em 30 minutos
        horarios = [f"{h:02d}:{m:02d}" for h in range(7, 21) for m in (0, 30)]
        self.hora_combo = ttk.Combobox(frame, values=horarios, state="readonly", width=6)
        self.hora_combo.grid(row=3, column=1, sticky=tk.E)
        self.hora_combo.set("10:00")

        if self.aula_existente:
            ttk.Label(frame, text="Status:").grid(row=4, column=0, sticky=tk.W, pady=5)
            self.status_combo = ttk.Combobox(frame, state="readonly", values=['AGENDADA', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA'])
            self.status_combo.grid(row=4, column=1, columnspan=2, sticky=tk.EW, pady=5)

        texto_botao = "Atualizar" if self.aula_existente else "Agendar Aula"
        agendar_btn = ttk.Button(frame, text=texto_botao, command=self.salvar)
        agendar_btn.grid(row=5, columnspan=3, pady=20)

    def carregar_dados_iniciais(self):
        alunos_data = self.api_client.listar_alunos()
        if alunos_data and 'erro' not in alunos_data:
            self.aluno_map = {f"{u['nome']} ({u.get('matricula', 'N/A')})": u['id'] for u in alunos_data}
            self.aluno_combo['values'] = list(self.aluno_map.keys())

        instrutores_data = self.api_client.listar_instrutores()
        if instrutores_data and 'erro' not in instrutores_data:
            self.instrutor_map = {f"{u['nome']} ({u.get('cnh', 'N/A')})": u['id'] for u in instrutores_data}
            self.instrutor_combo['values'] = list(self.instrutor_map.keys())

        self.todos_veiculos = self.api_client.listar_veiculos()
        if not self.todos_veiculos or 'erro' in self.todos_veiculos:
            self.todos_veiculos = []
            messagebox.showerror("Erro", "Não foi possível carregar a lista de veículos.")

    def on_aluno_selecionado(self, event=None):
        aluno_selecionado = self.aluno_combo.get()
        aluno_id = self.aluno_map.get(aluno_selecionado)

        if not aluno_id: return

        aluno_info = self.api_client.get_aluno(aluno_id)
        if not aluno_info or 'erro' in aluno_info:
            messagebox.showerror("Erro", "Não foi possível obter a categoria do aluno.")
            return
        categoria_aluno = aluno_info.get('categoria')
        if not categoria_aluno:
             messagebox.showwarning("Aviso", "Este aluno não possui uma categoria de CNH definida.")
             return
        tipos_permitidos = []
        if 'A' in categoria_aluno:
            tipos_permitidos.append('Motocicleta')
        if 'B' in categoria_aluno:
            tipos_permitidos.append('Carro')
        if 'C' in categoria_aluno:
            tipos_permitidos.append('Caminhão')
        if 'D' in categoria_aluno:
            tipos_permitidos.append('Ônibus')
        if 'E' in categoria_aluno:
             tipos_permitidos.extend(['Caminhão', 'Ônibus'])
        veiculos_filtrados = [v for v in self.todos_veiculos if v.get('tipo') in tipos_permitidos and v.get('ativo', True)]
        
        self.veiculo_map = {f"{v['modelo']} - {v['placa']}": v['id'] for v in veiculos_filtrados}
        self.veiculo_combo['values'] = list(self.veiculo_map.keys())
        self.veiculo_combo.set("")

    def preencher_dados(self):
        data_hora = datetime.fromisoformat(self.aula_existente['data_hora_inicio'])
        self.data_hora_entry.delete(0, tk.END)
        self.data_hora_entry.insert(0, data_hora.strftime('%Y-%m-%d %H:%M'))
        
        self.status_combo.set(self.aula_existente['status'].upper())
        
        aluno_nome = next((key for key, val in self.aluno_map.items() if val == self.aula_existente['aluno']['id']), None)
        if aluno_nome:
            self.aluno_combo.set(aluno_nome)
            self.on_aluno_selecionado()

        instrutor_nome = next((key for key, val in self.instrutor_map.items() if val == self.aula_existente['instrutor']['id']), None)
        if instrutor_nome: self.instrutor_combo.set(instrutor_nome)

        veiculo_nome = next((key for key, val in self.veiculo_map.items() if val == self.aula_existente['veiculo']['id']), None)
        if veiculo_nome: self.veiculo_combo.set(veiculo_nome)

    def salvar(self):
        aluno_selecionado = self.aluno_combo.get()
        instrutor_selecionado = self.instrutor_combo.get()
        veiculo_selecionado = self.veiculo_combo.get()
        data_selecionada = self.data_entry.get_date()
        hora_selecionada = self.hora_combo.get()

        if not hora_selecionada:
            messagebox.showerror("Erro de Validação", "Por favor, selecione um horário.")
            return

        try:
            # Combina a data do calendário com a hora do combobox
            data_hora_obj = datetime.combine(data_selecionada, datetime.strptime(hora_selecionada, '%H:%M').time())
            data_hora_iso = data_hora_obj.isoformat()
        except Exception as e:
            messagebox.showerror("Erro de Formato", f"Data ou hora inválida: {e}")
            return
        
        if not all([aluno_selecionado, instrutor_selecionado, veiculo_selecionado]):
            messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios.")
            return

        dados_aula = {
            "aluno_id": self.aluno_map[aluno_selecionado],
            "instrutor_id": self.instrutor_map[instrutor_selecionado],
            "veiculo_id": self.veiculo_map[veiculo_selecionado],
            "data_hora_inicio": data_hora_iso
        }
        if self.aula_existente:
            dados_aula['status'] = self.status_combo.get().lower()

        if self.aula_existente:
            resultado = self.api_client.atualizar_aula(self.aula_existente['id'], dados_aula)
            msg_sucesso = "Aula atualizada com sucesso!"
        else:
            resultado = self.api_client.agendar_aula(dados_aula)
            msg_sucesso = "Aula agendada com sucesso!"

        if resultado and 'erro' not in resultado:
            messagebox.showinfo("Sucesso", msg_sucesso)
            self.callback_sucesso()
            self.destroy()
        elif resultado:
            messagebox.showerror("Erro", resultado['erro'])