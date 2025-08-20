import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class CadastroAulaWindow(tk.Toplevel):
    def __init__(self, parent, api_client, callback_sucesso, aula_existente=None):
        super().__init__(parent)
        
        self.api_client = api_client
        self.callback_sucesso = callback_sucesso
        self.aula_existente = aula_existente

        # Define o título com base no modo (edição ou criação)
        self.title("Editar Aula" if self.aula_existente else "Agendar Nova Aula")
        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        self.create_widgets()
        self.carregar_dados_iniciais()
        
        if self.aula_existente:
            self.preencher_dados()

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
        
        if not self.aula_existente:
            self.data_hora_entry.insert(0, datetime.now().strftime('%Y-%m-%d %H:00'))

        texto_botao = "Atualizar" if self.aula_existente else "Agendar Aula"
        agendar_btn = ttk.Button(frame, text=texto_botao, command=self.salvar)
        agendar_btn.grid(row=4, columnspan=2, pady=10)


    def preencher_dados(self):
        """Preenche o formulário com dados de uma aula existente."""
        data_hora = datetime.fromisoformat(self.aula_existente['data_hora_inicio'])
        self.data_hora_entry.delete(0, tk.END)
        self.data_hora_entry.insert(0, data_hora.strftime('%Y-%m-%d %H:%M'))
        
        aluno_nome = next((key for key, val in self.aluno_map.items() if val == self.aula_existente['aluno']['id']), None)
        if aluno_nome: self.aluno_combo.set(aluno_nome)

        instrutor_nome = next((key for key, val in self.instrutor_map.items() if val == self.aula_existente['instrutor']['id']), None)
        if instrutor_nome: self.instrutor_combo.set(instrutor_nome)

        veiculo_nome = next((key for key, val in self.veiculo_map.items() if val == self.aula_existente['veiculo']['id']), None)
        if veiculo_nome: self.veiculo_combo.set(veiculo_nome)

    def carregar_dados_iniciais(self):
        usuarios = self.api_client.listar_usuarios()
        if usuarios and 'erro' not in usuarios:
            alunos = {f"{u['nome']} ({u.get('matricula', 'N/A')})": u['id'] for u in usuarios if u['role'] == 'aluno'}
            instrutores = {f"{u['nome']} ({u.get('cnh', 'N/A')})": u['id'] for u in usuarios if u['role'] == 'instrutor'}
            
            self.aluno_combo['values'] = list(alunos.keys())
            self.aluno_map = alunos
            
            self.instrutor_combo['values'] = list(instrutores.keys())
            self.instrutor_map = instrutores

        veiculos = self.api_client.listar_veiculos()
        if veiculos and 'erro' not in veiculos:
            veiculos_map = {f"{v['modelo']} - {v['placa']}": v['id'] for v in veiculos if v.get('ativo', True)}
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
            messagebox.showerror("Erro de Formato", "O formato da data e hora está incorreto.")
            return

        dados_aula = {
            "aluno_id": self.aluno_map[aluno_selecionado],
            "instrutor_id": self.instrutor_map[instrutor_selecionado],
            "veiculo_id": self.veiculo_map[veiculo_selecionado],
            "data_hora_inicio": data_hora_iso
        }

        # Decide se chama a API de atualização ou de criação
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