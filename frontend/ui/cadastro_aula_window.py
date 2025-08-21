import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

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

        ttk.Label(frame, text="Data e Hora (AAAA-MM-DD HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.data_hora_entry = ttk.Entry(frame)
        self.data_hora_entry.grid(row=3, column=1, sticky=tk.EW, pady=5)
        
        if not self.aula_existente:
            self.data_hora_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:00'))

        if self.aula_existente:
            ttk.Label(frame, text="Status:").grid(row=4, column=0, sticky=tk.W, pady=5)
            self.status_combo = ttk.Combobox(frame, state="readonly", values=['AGENDADA', 'EM_ANDAMENTO', 'CONCLUIDA', 'CANCELADA'])
            self.status_combo.grid(row=4, column=1, sticky=tk.EW, pady=5)

        texto_botao = "Atualizar" if self.aula_existente else "Agendar Aula"
        agendar_btn = ttk.Button(frame, text=texto_botao, command=self.salvar)
        agendar_btn.grid(row=5, columnspan=2, pady=20)

    def carregar_dados_iniciais(self):
        """Carrega alunos, instrutores e veículos de seus endpoints separados."""
        # Carrega Alunos
        alunos_data = self.api_client.listar_alunos()
        if alunos_data and 'erro' not in alunos_data:
            alunos = {f"{u['nome']} ({u.get('matricula', 'N/A')})": u['id'] for u in alunos_data}
            self.aluno_combo['values'] = list(alunos.keys())
            self.aluno_map = alunos

        # Carrega Instrutores
        instrutores_data = self.api_client.listar_instrutores()
        if instrutores_data and 'erro' not in instrutores_data:
            instrutores = {f"{u['nome']} ({u.get('cnh', 'N/A')})": u['id'] for u in instrutores_data}
            self.instrutor_combo['values'] = list(instrutores.keys())
            self.instrutor_map = instrutores

        # Carrega Veículos
        veiculos = self.api_client.listar_veiculos()
        if veiculos and 'erro' not in veiculos:
            veiculos_map = {f"{v['modelo']} - {v['placa']}": v['id'] for v in veiculos if v.get('ativo', True)}
            self.veiculo_combo['values'] = list(veiculos_map.keys())
            self.veiculo_map = veiculos_map

    def preencher_dados(self):
        """Preenche o formulário com dados de uma aula existente."""
        data_hora = datetime.fromisoformat(self.aula_existente['data_hora_inicio'])
        self.data_hora_entry.delete(0, tk.END)
        self.data_hora_entry.insert(0, data_hora.strftime('%Y-%m-%d %H:%M'))
        
        self.status_combo.set(self.aula_existente['status'].upper())
        
        # Encontra e define o valor nos comboboxes
        aluno_nome = next((key for key, val in self.aluno_map.items() if val == self.aula_existente['aluno']['id']), None)
        if aluno_nome: self.aluno_combo.set(aluno_nome)

        instrutor_nome = next((key for key, val in self.instrutor_map.items() if val == self.aula_existente['instrutor']['id']), None)
        if instrutor_nome: self.instrutor_combo.set(instrutor_nome)

        veiculo_nome = next((key for key, val in self.veiculo_map.items() if val == self.aula_existente['veiculo']['id']), None)
        if veiculo_nome: self.veiculo_combo.set(veiculo_nome)

    def salvar(self):
        aluno_selecionado = self.aluno_combo.get()
        instrutor_selecionado = self.instrutor_combo.get()
        veiculo_selecionado = self.veiculo_combo.get()
        data_hora_str = self.data_hora_entry.get()

        if not all([aluno_selecionado, instrutor_selecionado, veiculo_selecionado, data_hora_str]):
            messagebox.showerror("Erro de Validação", "Todos os campos são obrigatórios.")
            return

        try:
            data_hora_obj = datetime.strptime(data_hora_str, '%Y-%m-%d %H:%M')
            data_hora_iso = data_hora_obj.isoformat()
        except ValueError:
            messagebox.showerror("Erro de Formato", "O formato da data e hora está incorreto. Use AAAA-MM-DD HH:MM.")
            return

        dados_aula = {
            "aluno_id": self.aluno_map[aluno_selecionado],
            "instrutor_id": self.instrutor_map[instrutor_selecionado],
            "veiculo_id": self.veiculo_map[veiculo_selecionado],
            "data_hora_inicio": data_hora_iso
        }
        if self.aula_existente:
            # Garante que o status é enviado em minúsculas, como a API espera
            dados_aula['status'] = self.status_combo.get().lower()

        if self.aula_existente:
            resultado = self.api_client.atualizar_aula(self.aula_existente['id'], dados_aula)
            msg_sucesso = "Aula atualizada com sucesso!"
        else:
            resultado = self.api_client.agendar_aula(dados_aula)
            msg_sucesso = "Aula agendada com sucesso!"

        if 'erro' in resultado:
            messagebox.showerror("Erro", resultado['erro'])
        else:
            messagebox.showinfo("Sucesso", msg_sucesso)
            self.callback_sucesso()
            self.destroy()