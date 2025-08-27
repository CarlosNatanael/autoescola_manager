import tkinter as tk
from tkinter import ttk, messagebox

class CadastroUsuarioWindow(tk.Toplevel):
    def __init__(self, parent, api_client, on_success, role, usuario_existente=None):
        super().__init__(parent)
        self.api = api_client
        self.on_success = on_success
        self.usuario_existente = usuario_existente
        self.role = role

        titulo_acao = "Editar" if self.usuario_existente else "Cadastrar Novo"
        self.title(f"{titulo_acao} {self.role.capitalize()}")
            
        self.geometry("450x480")
        self.iconbitmap("icone.ico")
        self.transient(parent)
        self.grab_set()

        self.entries = {}
        self.create_widgets()
        if self.usuario_existente:
            self.preencher_dados()

    def create_widgets(self):
        frame = ttk.Frame(self, padding="20")
        frame.pack(expand=True, fill=tk.BOTH)

        campos = ['Nome', 'Email', 'CPF', 'Telefone']
        for i, campo in enumerate(campos):
            label = ttk.Label(frame, text=f"{campo}:")
            label.grid(row=i, column=0, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame, width=35)
            entry.grid(row=i, column=1, sticky=(tk.W, tk.E), pady=5)
            self.entries[campo.lower()] = entry

        row_seguinte = len(campos)

        if self.role == 'aluno':
            label_categoria = ttk.Label(frame, text="Categoria CNH:")
            label_categoria.grid(row=row_seguinte, column=0, sticky=tk.W, pady=5)
            categorias = ['A', 'B', 'C', 'D', 'E', 'AB']
            self.categoria_combo = ttk.Combobox(frame, values=categorias, state="readonly")
            self.categoria_combo.grid(row=row_seguinte, column=1, sticky=(tk.W, tk.E), pady=5)
            self.categoria_combo.set('B')
            row_seguinte += 1
            
            ttk.Label(frame, text="Aulas Práticas:").grid(row=row_seguinte, column=0, sticky=tk.W, pady=2)
            self.aulas_praticas_entry = ttk.Entry(frame, width=10)
            self.aulas_praticas_entry.grid(row=row_seguinte, column=1, sticky=tk.W, pady=2)
            self.aulas_praticas_entry.insert(0, "20")
            row_seguinte += 1

            ttk.Label(frame, text="Aulas Simulador:").grid(row=row_seguinte, column=0, sticky=tk.W, pady=2)
            self.aulas_simulador_entry = ttk.Entry(frame, width=10)
            self.aulas_simulador_entry.grid(row=row_seguinte, column=1, sticky=tk.W, pady=2)
            self.aulas_simulador_entry.insert(0, "0")
            row_seguinte += 1

            ttk.Label(frame, text="Aulas Extras:").grid(row=row_seguinte, column=0, sticky=tk.W, pady=2)
            self.aulas_extras_entry = ttk.Entry(frame, width=10)
            self.aulas_extras_entry.grid(row=row_seguinte, column=1, sticky=tk.W, pady=2)
            self.aulas_extras_entry.insert(0, "0")
            row_seguinte += 1

        if self.role == 'instrutor':
            label_cnh = ttk.Label(frame, text="CNH:")
            label_cnh.grid(row=row_seguinte, column=0, sticky=tk.W, pady=5)
            entry_cnh = ttk.Entry(frame, width=35)
            entry_cnh.grid(row=row_seguinte, column=1, sticky=(tk.W, tk.E), pady=5)
            self.entries['cnh'] = entry_cnh
            row_seguinte += 1
        
        texto_botao = "Atualizar" if self.usuario_existente else "Salvar"
        btn_salvar = ttk.Button(frame, text=texto_botao, command=self.salvar_usuario)
        btn_salvar.grid(row=row_seguinte, column=0, columnspan=2, pady=20)

    def preencher_dados(self):
        for campo_key, entry in self.entries.items():
            valor = self.usuario_existente.get(campo_key, "")
            entry.insert(0, valor if valor else "")
        if self.role == 'aluno':
            if self.usuario_existente.get('categoria'):
                self.categoria_combo.set(self.usuario_existente['categoria'])
            self.aulas_praticas_entry.delete(0, tk.END)
            self.aulas_praticas_entry.insert(0, self.usuario_existente.get('aulas_praticas_contratadas', 20))
            self.aulas_simulador_entry.delete(0, tk.END)
            self.aulas_simulador_entry.insert(0, self.usuario_existente.get('aulas_simulador_contratadas', 0))
            self.aulas_extras_entry.delete(0, tk.END)
            self.aulas_extras_entry.insert(0, self.usuario_existente.get('aulas_extras_contratadas', 0))

    def salvar_usuario(self):
        dados_usuario = {campo: entry.get() for campo, entry in self.entries.items()}

        if self.role == 'aluno':
            dados_usuario['categoria'] = self.categoria_combo.get()
            dados_usuario['aulas_praticas_contratadas'] = int(self.aulas_praticas_entry.get() or 0)
            dados_usuario['aulas_simulador_contratadas'] = int(self.aulas_simulador_entry.get() or 0)
            dados_usuario['aulas_extras_contratadas'] = int(self.aulas_extras_entry.get() or 0)

        campos_obrigatorios = ['nome', 'email', 'cpf']
        if self.role == 'instrutor':
            campos_obrigatorios.append('cnh')
        if self.role == 'aluno':
            campos_obrigatorios.append('categoria')

        if not all(dados_usuario.get(key) for key in campos_obrigatorios):
            messagebox.showwarning("Campos Obrigatórios", "Por favor, preencha todos os campos obrigatórios.")
            return

        resultado = None
        mensagem_sucesso = ""

        if self.usuario_existente:
            if self.role == 'aluno':
                resultado = self.api.atualizar_aluno(self.usuario_existente['id'], dados_usuario)
            else:
                resultado = self.api.atualizar_instrutor(self.usuario_existente['id'], dados_usuario)
            mensagem_sucesso = f"{self.role.capitalize()} atualizado com sucesso!"
        else:
            if self.role == 'aluno':
                resultado = self.api.cadastrar_aluno(dados_usuario)
            else:
                resultado = self.api.cadastrar_instrutor(dados_usuario)
            mensagem_sucesso = f"{self.role.capitalize()} cadastrado com sucesso!"
        
        if resultado and 'erro' not in resultado:
            messagebox.showinfo("Sucesso", mensagem_sucesso)
            self.on_success()
            self.destroy()
        elif resultado:
            messagebox.showerror("Erro", resultado['erro'])