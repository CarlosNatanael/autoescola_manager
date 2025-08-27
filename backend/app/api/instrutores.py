from flask import Blueprint, request, jsonify
from app.models import Instrutor, Usuario
from app import db

bp = Blueprint('instrutores', __name__)

@bp.route('/instrutores', methods=['POST'])
def criar_instrutor():
    """Endpoint para cadastrar um novo instrutor."""
    dados = request.get_json()

    campos_obrigatorios = ['nome', 'email', 'cpf', 'cnh']
    if not dados or not all(campo in dados for campo in campos_obrigatorios):
        return jsonify({'erro': 'Nome, email, cpf e CNH são obrigatórios.'}), 400

    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({'erro': 'Este email já está em uso.'}), 409
    if Usuario.query.filter_by(cpf=dados['cpf']).first():
        return jsonify({'erro': 'Este CPF já está cadastrado.'}), 409

    novo_instrutor = Instrutor(
        nome=dados['nome'],
        email=dados['email'],
        cpf=dados['cpf'],
        telefone=dados.get('telefone'),
        cnh=dados['cnh']
    )

    db.session.add(novo_instrutor)
    db.session.commit()
    return jsonify({'mensagem': 'Instrutor cadastrado com sucesso!', 'id': novo_instrutor.id}), 201

@bp.route('/instrutores/<int:id>', methods=['PUT'])
def atualizar_instrutor(id):
    """Endpoint para atualizar os dados de um instrutor."""
    instrutor = Instrutor.query.get_or_404(id)
    dados = request.get_json()
    instrutor.nome = dados.get('nome', instrutor.nome)
    instrutor.email = dados.get('email', instrutor.email)
    instrutor.cpf = dados.get('cpf', instrutor.cpf)
    instrutor.telefone = dados.get('telefone', instrutor.telefone)
    instrutor.cnh = dados.get('cnh', instrutor.cnh)
    db.session.commit()
    return jsonify({'mensagem': 'Instrutor atualizado com sucesso'})

@bp.route('/instrutores/<int:id>', methods=['DELETE'])
def deletar_instrutor(id):
    """Endpoint para deletar um instrutor."""
    instrutor = Instrutor.query.get_or_404(id)
    if instrutor.aulas.first():
        return jsonify({'erro': 'Não é possível excluir um instrutor que já está associado a aulas.'}), 409
    db.session.delete(instrutor)
    db.session.commit()
    return jsonify({'mensagem': 'Instrutor deletado com sucesso!'})

@bp.route('/instrutores', methods=['GET'])
def listar_instrutores():
    """Endpoint para listar todos os instrutores."""
    instrutores = Instrutor.query.all()
    lista_de_instrutores = [{
        'id': i.id, 'nome': i.nome, 'email': i.email, 'cpf': i.cpf,
        'telefone': i.telefone, 'cnh': i.cnh, 'role': 'instrutor'
    } for i in instrutores]
    return jsonify(lista_de_instrutores)