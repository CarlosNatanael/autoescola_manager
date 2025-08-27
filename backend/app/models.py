from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app import db
import enum

# --- ENUMs ---
class UserRole(enum.Enum):
    ADMIN = 'admin'
    INSTRUTOR = 'instrutor'
    ALUNO = 'aluno'

class AulaStatus(enum.Enum):
    AGENDADA = 'agendada'
    CONCLUIDA = 'concluida'
    CANCELADA = 'cancelada'
    EM_ANDAMENTO = 'em_andamento'

class CategoriaCNH(enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    AB = 'AB'

class TipoVeiculo(enum.Enum):
    MOTOCICLETA = 'Motocicleta'
    CARRO = 'Carro'
    ONIBUS = 'Ônibus'
    CAMINHAO = 'Caminhão'

class TipoAula(enum.Enum):
    PRATICA = 'Prática'
    SIMULADOR = 'Simulador'
    EXTRA = 'Extra'


# --- Modelos de Usuário ---
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    telefone = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    senha_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole, native_enum=False), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'usuario',
        'polymorphic_on': role
    }

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

class Aluno(Usuario):
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    matricula = db.Column(db.String(20), unique=True)
    aulas = db.relationship('Aula', back_populates='aluno', lazy='dynamic')
    categoria = db.Column(db.Enum(CategoriaCNH, native_enum=False), nullable=False)
    
    # --- CAMPOS PARA CONTROLO DE AULAS ---
    aulas_praticas_contratadas = db.Column(db.Integer, nullable=False, default=20)
    aulas_simulador_contratadas = db.Column(db.Integer, nullable=False, default=0)
    aulas_extras_contratadas = db.Column(db.Integer, nullable=False, default=0)
    __mapper_args__ = {
        'polymorphic_identity': UserRole.ALUNO
    }

class Instrutor(Usuario):
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    cnh = db.Column(db.String(20), unique=True)
    aulas = db.relationship('Aula', back_populates='instrutor', lazy='dynamic')
    
    __mapper_args__ = {
        'polymorphic_identity': UserRole.INSTRUTOR
    }

# --- CLASSE ADMIN ---
class Admin(Usuario):
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    
    __mapper_args__ = {
        'polymorphic_identity': UserRole.ADMIN
    }

# --- Modelo de Veículo ---
class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(8), unique=True, nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50))
    ano = db.Column(db.Integer)
    tipo = db.Column(db.Enum(TipoVeiculo, native_enum=False), nullable=False)
    ativo = db.Column(db.Boolean, default=True)
    aulas = db.relationship('Aula', back_populates='veiculo', lazy='dynamic')

# --- Modelo Aula ---
class Aula(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_hora_inicio = db.Column(db.DateTime, nullable=False)
    data_hora_fim = db.Column(db.DateTime, nullable=False)
    
    status = db.Column(db.Enum(AulaStatus, native_enum=False), nullable=False, default=AulaStatus.AGENDADA)
    tipo_aula = db.Column(db.Enum(TipoAula, native_enum=False), nullable=False, default=TipoAula.PRATICA)
    
    aluno_id = db.Column(db.Integer, db.ForeignKey('aluno.id'), nullable=False)
    instrutor_id = db.Column(db.Integer, db.ForeignKey('instrutor.id'), nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculo.id'), nullable=False)

    aluno = db.relationship('Aluno', back_populates='aulas')
    instrutor = db.relationship('Instrutor', back_populates='aulas')
    veiculo = db.relationship('Veiculo', back_populates='aulas')