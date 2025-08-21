import tkinter as tk
from tkinter import ttk, messagebox

class CadastroVeiculoWindow(tk.Toplevel):
    def __init__(self, parent, api_client, on_success, veiculo_existente=None):
        super().__init__(parent)
        self.api = api_client
        self.on_success = on_success
        self.veiculo_existente = veiculo_existente

        # Define o título e o modo (Cadastro vs. Edição)
        if self.veiculo_existente:
            self.title("Editar Veículo")
        else:
            self.title("Cadastrar Novo Veículo")

        self.geometry("400x300")
        self.transient(parent)
        self.grab_set()

        self.entries = {}
        self.create_widgets()
        if self.veiculo_existente:
            self.preencher_dados()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill=tk.BOTH)

        campos = ['Placa', 'Modelo', 'Marca', 'Ano', 'Tipo']
        for i, campo in enumerate(campos):
            label = ttk.Label(frame, text=f"{campo}:")
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame, width=30)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
            self.entries[campo.lower()] = entry

        texto_botao = "Atualizar" if self.veiculo_existente else "Salvar"
        btn_salvar = ttk.Button(frame, text=texto_botao, command=self.salvar)
        btn_salvar.grid(row=len(campos), column=0, columnspan=2, pady=20)

    def preencher_dados(self):
        """Preenche o formulário com os dados do veículo existente."""
        for campo, entry in self.entries.items():
            valor = self.veiculo_existente.get(campo, "")
            entry.insert(0, valor if valor else "")

    def salvar(self):
        dados_veiculo = {campo: entry.get() for campo, entry in self.entries.items()}

        if not dados_veiculo['placa'] or not dados_veiculo['modelo']:
            messagebox.showwarning("Campo Obrigatório", "Placa e Modelo são obrigatórios.")
            return

        if self.veiculo_existente: # Modo Edição
            resultado = self.api.atualizar_veiculo(self.veiculo_existente['id'], dados_veiculo)
            mensagem_sucesso = "Veículo atualizado com sucesso!"
        else: # Modo Cadastro
            resultado = self.api.cadastrar_veiculo(dados_veiculo)
            mensagem_sucesso = "Veículo cadastrado com sucesso!"
        
        if 'erro' not in resultado:
            messagebox.showinfo("Sucesso", mensagem_sucesso)
            self.on_success()
            self.destroy()
        else:
            messagebox.showerror("Erro", resultado['erro'])