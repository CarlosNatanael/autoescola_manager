import requests
import json

class ApiCliente:
    def __init__(self, base_url="https://vn75t0lq-5000.brs.devtunnels.ms/api"):
        """Inicializa o cliente com a URL base da API."""
        self.base_url = base_url

    def _handle_response(self, response):
        """Função auxiliar para tratar as respostas e extrair JSON."""
        try:
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            print(f"Erro na API: {e}")
            try:
                return {'erro': response.json().get('erro', response.text)}
            except json.JSONDecodeError:
                return {'erro': response.text}

    # --- Métodos de Veículos ---
    def listar_veiculos(self):
        try:
            response = requests.get(f"{self.base_url}/veiculos")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def cadastrar_veiculo(self, dados):
        try:
            response = requests.post(f"{self.base_url}/veiculos", json=dados)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def atualizar_veiculo(self, veiculo_id, dados):
        try:
            response = requests.put(f"{self.base_url}/veiculos/{veiculo_id}", json=dados)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def deletar_veiculo(self, veiculo_id):
        try:
            response = requests.delete(f"{self.base_url}/veiculos/{veiculo_id}")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    # --- MÉTODOS DE ALUNOS ---
    def listar_alunos(self):
        try:
            response = requests.get(f"{self.base_url}/alunos")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def cadastrar_aluno(self, dados):
        try:
            response = requests.post(f"{self.base_url}/alunos", json=dados)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}
        
    def get_aluno(self, aluno_id):
        try:
            response = requests.get(f"{self.base_url}/alunos/{aluno_id}")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}
        
    def atualizar_aluno(self, aluno_id, dados):
        try:
            response = requests.put(f"{self.base_url}/alunos/{aluno_id}", json=dados)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def deletar_aluno(self, aluno_id):
        try:
            response = requests.delete(f"{self.base_url}/alunos/{aluno_id}")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}
        
    # --- MÉTODOS DE INSTRUTORES ---
    def listar_instrutores(self):
        try:
            response = requests.get(f"{self.base_url}/instrutores")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def cadastrar_instrutor(self, dados):
        try:
            response = requests.post(f"{self.base_url}/instrutores", json=dados)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def atualizar_instrutor(self, instrutor_id, dados):
        try:
            response = requests.put(f"{self.base_url}/instrutores/{instrutor_id}", json=dados)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def deletar_instrutor(self, instrutor_id):
        try:
            response = requests.delete(f"{self.base_url}/instrutores/{instrutor_id}")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    # --- Métodos de Aulas ---

    def listar_aulas_hoje(self):
        try:
            response = requests.get(f"{self.base_url}/aulas/hoje")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def listar_aulas(self):
        try:
            response = requests.get(f"{self.base_url}/aulas")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def agendar_aula(self, dados):
        try:
            response = requests.post(f"{self.base_url}/aulas", json=dados)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}
        
    def atualizar_aula(self, aula_id, dados):
        try:
            response = requests.put(f"{self.base_url}/aulas/{aula_id}", json=dados)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}

    def deletar_aula(self, aula_id):
        try:
            response = requests.delete(f"{self.base_url}/aulas/{aula_id}")
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'erro': str(e)}