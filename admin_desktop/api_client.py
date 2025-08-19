import requests
import json

class ApiCliente:
    def __init__(self, base_url="https://vn75t0lq-5000.brs.devtunnels.ms/api"):
        """
        Inicializa o cliente com a URL base da API.
        """
        self.base_url = base_url

    # --- Métodos de Veículos ---
    def listar_veiculos(self):
        try:
            url = f"{self.base_url}/veiculos"
            response = requests.get(url, timeout=5)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com a API: {e}")
            return None

    def cadastrar_veiculo(self, dados_veiculo):
        try:
            url = f"{self.base_url}/veiculos"
            response = requests.post(url, json=dados_veiculo, timeout=5)
            return response.json() if response.status_code == 201 else None
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com a API: {e}")
            return None

    # --- Métodos de Utilizadores ---
    def listar_usuarios(self):
        """Busca a lista de todos os utilizadores (alunos e instrutores)."""
        try:
            url = f"{self.base_url}/usuarios"
            response = requests.get(url, timeout=5)
            return response.json() if response.status_code == 200 else None
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com a API: {e}")
            return None

    def cadastrar_usuario(self, dados_usuario):
        """Envia os dados de um novo utilizador para a API."""
        try:
            url = f"{self.base_url}/usuarios"
            response = requests.post(url, json=dados_usuario, timeout=5)
            return response.json() if response.status_code == 201 else None
        except requests.exceptions.RequestException as e:
            print(f"Erro de conexão com a API: {e}")
            return None
        
    # --- Métodos de aulas ---
    def listar_aulas(self):
        """Busca todas as aulas agendadas na API."""
        try:
            response = requests.get(f"{self.base_url}/aulas")
            response.raise_for_status()  # Lança uma exceção para respostas de erro (4xx ou 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar aulas: {e}")
            return None

    def agendar_aula(self, dados_aula):
        """Envia os dados de uma nova aula para a API."""
        try:
            response = requests.post(f"{self.base_url}/aulas", json=dados_aula)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao agendar aula: {e}")
            try:
                return {'erro': response.json().get('erro', 'Erro desconhecido')}
            except (ValueError, AttributeError):
                return {'erro': str(e)}