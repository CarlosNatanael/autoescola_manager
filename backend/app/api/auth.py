from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timedelta
from app.models import Usuario
import jwt

bp = Blueprint('auth', __name__)

@bp.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    if not dados or not 'email' in dados or not 'senha' in dados:
        return jsonify({'erro': 'Email e senha são obrigatórios.'})
    
    email = dados['email']
    senha = dados['senha']

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario or not usuario.check_password(senha):
        return jsonify({'erro': 'Credenciais inválidas.'})
    
    token = jwt.encode({
        'user_id': usuario.id,
        'exp': datetime.utcnow() + timedelta(hours=8)
    }, current_app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({'token': token})