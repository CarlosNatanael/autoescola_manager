import tkinter as tk
from tkinter import ttk, messagebox

class CadastroVeiculoWindow(tk.Toplevel):
    def __init__(self, parent, api_client, on_success, veiculo_existente=None):
        super().__init__(parent)
        self.api = api_client
        self.on_success = on_success
        self.veiculo_existente = veiculo_existente

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

        campos = ['Placa', 'Modelo', 'Marca', 'Ano']
        for i, campo in enumerate(campos):
            label = ttk.Label(frame, text=f"{campo}:")
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame, width=30)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
            self.entries[campo.lower()] = entry
            
        label_tipo = ttk.Label(frame, text="Tipo:")
        label_tipo.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        tipos_veiculo = ['MOTOCICLETA', 'CARRO', 'ONIBUS', 'CAMINHAO']
        self.tipo_combo = ttk.Combobox(frame, values=tipos_veiculo, state="readonly", width=28)
        self.tipo_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5)
        self.tipo_combo.set('CARRO') # Define um valor padrão

        texto_botao = "Atualizar" if self.veiculo_existente else "Salvar"
        btn_salvar = ttk.Button(frame, text=texto_botao, command=self.salvar)
        btn_salvar.grid(row=5, column=0, columnspan=2, pady=20)

    def preencher_dados(self):
        """Preenche o formulário com os dados do veículo existente."""
        for campo, entry in self.entries.items():
            valor = self.veiculo_existente.get(campo, "")
            entry.insert(0, str(valor) if valor else "")
        
        if self.veiculo_existente.get('tipo'):
            self.tipo_combo.set(self.veiculo_existente['tipo'])

    def salvar(self):
        dados_veiculo = {campo: entry.get() for campo, entry in self.entries.items()}
        dados_veiculo['tipo'] = self.tipo_combo.get()

        if not dados_veiculo['placa'] or not dados_veiculo['modelo']:
            messagebox.showwarning("Campo Obrigatório", "Placa e Modelo são obrigatórios.")
            return
        if self.veiculo_existente:
            resultado = self.api.atualizar_veiculo(self.veiculo_existente['id'], dados_veiculo)
            mensagem_sucesso = "Veículo atualizado com sucesso!"
        else:
            resultado = self.api.cadastrar_veiculo(dados_veiculo)
            mensagem_sucesso = "Veículo cadastrado com sucesso!"
        
        if resultado and 'erro' not in resultado:
            messagebox.showinfo("Sucesso", mensagem_sucesso)
            self.on_success()
            self.destroy()
        elif resultado:
            messagebox.showerror("Erro", resultado['erro'])