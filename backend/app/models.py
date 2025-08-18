from app import db
from datetime import datetime
import enum

class UserRole(enum.Enum):
    ADMIN = 'admin'
    INSTRUTOR = 'instrutor'
    ALUNO = 'aluno'

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(128))
    telefone = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.Enum(UserRole), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'usuario',
        'polymorphic_on': role
    }

class Aluno(Usuario):
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    matricula = db.Column(db.String(20), unique=True)
    
    __mapper_args__ = {
        'polymorphic_identity': UserRole.ALUNO
    }

class Instrutor(Usuario):
    id = db.Column(db.Integer, db.ForeignKey('usuario.id'), primary_key=True)
    cnh = db.Column(db.String(20), unique=True)
    
    __mapper_args__ = {
        'polymorphic_identity': UserRole.INSTRUTOR
    }

class Veiculo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(8), unique=True, nullable=False)
    modelo = db.Column(db.String(50), nullable=False)
    marca = db.Column(db.String(50))
    ano = db.Column(db.Integer)
    tipo = db.Column(db.String(20))
    ativo = db.Column(db.Boolean, default=True)
