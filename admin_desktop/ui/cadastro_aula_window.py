# Em admin_desktop/ui/cadastro_aula_window.py

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class CadastroAulaWindow(tk.Toplevel):
    def __init__(self, parent, api_client, callback_sucesso):
        super().__init__(parent)
        self.title("Agendar Nova Aula")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        self.api_client = api_client
        self.callback_sucesso = callback_sucesso

        self.create_widgets()
        self.carregar_dados_iniciais()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Aluno:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.aluno_combo = ttk.Combobox(frame, state="readonly")
        self.aluno_combo.grid(row=0, column=1, sticky=tk.EW, pady=2)

        ttk.Label(frame, text="Instrutor:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.instrutor_combo = ttk.Combobox(frame, state="readonly")
        self.instrutor_combo.grid(row=1, column=1, sticky=tk.EW, pady=2)

        ttk.Label(frame, text="Veículo:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.veiculo_combo = ttk.Combobox(frame, state="readonly")
        self.veiculo_combo.grid(row=2, column=1, sticky=tk.EW, pady=2)

        ttk.Label(frame, text="Data e Hora (AAAA-MM-DD HH:MM):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.data_hora_entry = ttk.Entry(frame)
        self.data_hora_entry.grid(row=3, column=1, sticky=tk.EW, pady=2)
        self.data_hora_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:00'))


        agendar_btn = ttk.Button(frame, text="Agendar Aula", command=self.agendar)
        agendar_btn.grid(row=4, columnspan=2, pady=10)

    def carregar_dados_iniciais(self):
        usuarios = self.api_client.listar_usuarios()
        if usuarios:
            alunos = {f"{u['nome']} ({u['matricula']})": u['id'] for u in usuarios if u['role'] == 'aluno'}
            instrutores = {f"{u['nome']} ({u['cnh']})": u['id'] for u in usuarios if u['role'] == 'instrutor'}
            
            self.aluno_combo['values'] = list(alunos.keys())
            self.aluno_map = alunos
            
            self.instrutor_combo['values'] = list(instrutores.keys())
            self.instrutor_map = instrutores

        veiculos = self.api_client.listar_veiculos()
        if veiculos:
            veiculos_map = {f"{v['modelo']} - {v['placa']}": v['id'] for v in veiculos if v['ativo']}
            self.veiculo_combo['values'] = list(veiculos_map.keys())
            self.veiculo_map = veiculos_map

    def agendar(self):
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
            messagebox.showerror("Erro de Formato", "O formato da data e hora está incorreto.")
            return

        dados_aula = {
            "aluno_id": self.aluno_map[aluno_selecionado],
            "instrutor_id": self.instrutor_map[instrutor_selecionado],
            "veiculo_id": self.veiculo_map[veiculo_selecionado],
            "data_hora_inicio": data_hora_iso
        }

        resultado = self.api_client.agendar_aula(dados_aula)

        if 'erro' in resultado:
            messagebox.showerror("Erro no Agendamento", resultado['erro'])
        else:
            messagebox.showinfo("Sucesso", "Aula agendada com sucesso!")
            self.callback_sucesso()
            self.destroy()