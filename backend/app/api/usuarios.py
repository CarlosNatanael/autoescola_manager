from flask import Blueprint, request, jsonify
from app.models import Aluno, Instrutor, Usuario, UserRole
from app import db

bp = Blueprint('usuarios', __name__)

@bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    """
    Endpoint para cadastrar um novo usuário (Aluno ou Instrutor).
    """
    dados = request.get_json()

    campos_obrigatorios = ['nome', 'email', 'cpf', 'role']
    if not dados or not all(campo in dados for campo in campos_obrigatorios):
        return jsonify({'erro': 'Dados incompletos. Nome, email, cpf e role são obrigatórios.'}), 400

    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({'erro': 'Este email já está em uso.'}), 409
    if Usuario.query.filter_by(cpf=dados['cpf']).first():
        return jsonify({'erro': 'Este CPF já está cadastrado.'}), 409

    role_str = dados['role'].lower()
    novo_usuario = None

    if role_str == 'aluno':
        novo_usuario = Aluno(
            nome=dados['nome'],
            email=dados['email'],
            cpf=dados['cpf'],
            telefone=dados.get('telefone'),
            matricula=dados.get('matricula')
        )
    elif role_str == 'instrutor':
        if 'cnh' not in dados:
            return jsonify({'erro': 'O campo CNH é obrigatório para instrutores.'}), 400
        
        novo_usuario = Instrutor(
            nome=dados['nome'],
            email=dados['email'],
            cpf=dados['cpf'],
            telefone=dados.get('telefone'),
            cnh=dados['cnh']
        )
    else:
        return jsonify({'erro': "Role inválida. Use 'aluno' ou 'instrutor'."}), 400

    db.session.add(novo_usuario)
    db.session.commit()

    return jsonify({'mensagem': f'{role_str.capitalize()} cadastrado com sucesso!', 'id': novo_usuario.id}), 201

@bp.route('/usuarios/<int:id>', methods=['POST'])
def atualizar_usuario(id):
    """
    Endpoint para atualizar os dados de um usuário existente.
    """
    usuario = Usuario.query.get_or_404(id)
    dados = request.get_json()

    if not dados:
        return jsonify({'erro': 'Nenhum dado fornecido para atualizção'}), 400
    
    if 'email' in dados and dados['email'] != usuario.email and Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({'erro': 'Este email já está em uso.'}), 409
    if 'cpf' in dados and dados['cpf'] != usuario.cpf and Usuario.query.filter_by(cpf=dados['cpf']).first():
        return jsonify({'erro': 'Este CPF já está cadastrado.'}), 409
    
    usuario.nome = dados.get('nome', usuario.nome)
    usuario.email = dados.get('email', usuario.email)
    usuario.cpf = dados.get('cpf', usuario.cpf)
    usuario.telefone = dados.get('telefone', usuario.telefone)

    if usuario.role == UserRole.ALUNO and 'matricula' in dados:
        usuario.matricula = dados.get('matricula')

@bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    """
    Endpoint para listar todos os usuários (alunos e instrutores).
    """
    usuarios = Usuario.query.all()
    lista_de_usuarios = []
    for usuario in usuarios:
        dados_usuario = {
            'id': usuario.id,
            'nome': usuario.nome,
            'email': usuario.email,
            'cpf': usuario.cpf,
            'telefone': usuario.telefone,
            'role': usuario.role.value
        }
        if usuario.role == UserRole.ALUNO:
            dados_usuario['matricula'] = usuario.matricula
        elif usuario.role == UserRole.INSTRUTOR:
            dados_usuario['cnh'] = usuario.cnh
        
        lista_de_usuarios.append(dados_usuario)

    return jsonify(lista_de_usuarios)