import tkinter as tk
from tkinter import ttk, messagebox

class CadastroVeiculoWindow(tk.Toplevel):
    """
    Janela para cadastrar um novo veículo.
    """
    def __init__(self, parent, api_client, on_success):
        super().__init__(parent)
        self.title("Cadastrar Novo Veículo")
        self.geometry("400x300")
        self.transient(parent) # Mantém a janela sobre a janela principal
        self.grab_set() # Bloqueia a janela principal enquanto esta estiver aberta

        self.api = api_client
        self.on_success = on_success # Função a ser chamada após o sucesso

        # Dicionário para guardar as entradas do formulário
        self.entries = {}

        self.create_widgets()

    def create_widgets(self):
        """Cria os widgets do formulário."""
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill=tk.BOTH)

        # Labels e Entradas para cada campo do veículo
        campos = ['Placa', 'Modelo', 'Marca', 'Ano', 'Tipo']
        for i, campo in enumerate(campos):
            label = ttk.Label(frame, text=f"{campo}:")
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            
            entry = ttk.Entry(frame, width=30)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
            self.entries[campo.lower()] = entry

        # Botão de Salvar
        btn_salvar = ttk.Button(frame, text="Salvar", command=self.salvar_veiculo)
        btn_salvar.grid(row=len(campos), column=0, columnspan=2, pady=20)

    def salvar_veiculo(self):
        """Coleta os dados do formulário e envia para a API."""
        # Coleta os dados das entradas
        dados_veiculo = {campo: entry.get() for campo, entry in self.entries.items()}

        # Validação simples
        if not dados_veiculo['placa'] or not dados_veiculo['modelo']:
            messagebox.showwarning("Campo Obrigatório", "Placa e Modelo são obrigatórios.")
            return

        # Chama o método da API para cadastrar
        resultado = self.api.cadastrar_veiculo(dados_veiculo)

        if resultado:
            messagebox.showinfo("Sucesso", "Veículo cadastrado com sucesso!")
            self.on_success() # Chama a função de callback (para atualizar a lista)
            self.destroy() # Fecha a janela de cadastro
        else:
            messagebox.showerror("Erro", "Não foi possível cadastrar o veículo.")

