from flask import Blueprint, request, jsonify
from app.models import Veiculo
from app import db

bp = Blueprint('veiculos', __name__)

@bp.route('/veiculos', methods=['POST'])
def criar_veiculo():
    """
    Endpoint para cadastrar um novo veículo.
    """
    dados = request.get_json()

    if not dados or not 'placa' in dados or not 'modelo' in dados:
        return jsonify({'erro': 'Dados incompletos. Placa e modelo são obrigatórios.'}), 400

    if Veiculo.query.filter_by(placa=dados['placa']).first():
        return jsonify({'erro': 'Veículo com esta placa já cadastrado.'}), 409

    novo_veiculo = Veiculo(
        placa=dados['placa'],
        modelo=dados['modelo'],
        marca=dados.get('marca'),
        ano=dados.get('ano'),
        tipo=dados.get('tipo')
    )

    db.session.add(novo_veiculo)
    db.session.commit()

    return jsonify({'mensagem': 'Veículo cadastrado com sucesso!', 'id': novo_veiculo.id}), 201

@bp.route('/veiculos/<int:id>', methods=['PUT'])
def atualizar_veiculo(id):
    """
    Endpoint para atualizar os dados de um veículo existente.
    """
    veiculo = Veiculo.query.get_or_404(id)
    dados = request.get_json()

    if not dados:
        return jsonify({'erro': 'Nenhum dado fornecido para atualização.'}), 400
    
    if 'placa' in dados and dados['placa'] != veiculo.placa:
        if Veiculo.query.filter_by(placa=dados['placa']).first():
            return jsonify({'erro': 'Já existe um veículo com esta placa.'}), 409
        
    veiculo.placa = dados.get('placa', veiculo.placa)
    veiculo.modelo = dados.get('modelo', veiculo.modelo)
    veiculo.marca = dados.get('marca', veiculo.marca)
    veiculo.ano = dados.get('ano', veiculo.ano)
    veiculo.tipo = dados.get('tipo', veiculo.tipo)

    db.session.commit()
    return jsonify({'mensagem': 'Veículo atualizado com sucesso!'})

@bp.route('/veiculos/<int:id>', methods=['DELETE'])
def deletar_veiculo(id):
    """
    Endpoint para deletar um veículo.
    """
    veiculo = Veiculo.query.get_or_404(id)
    
    if veiculo.aulas.first():
        return jsonify({'erro': 'Não é possível excluir um veículo que já está associado a aulas.'}), 409

    db.session.delete(veiculo)
    db.session.commit()
    return jsonify({'mensagem': 'Veículo deletado com sucesso!'})

@bp.route('/veiculos', methods=['GET'])
def listar_veiculos():
    """
    Endpoint para listar todos os veículos cadastrados.
    """
    
    veiculos = Veiculo.query.all()
    lista_de_veiculos = [
        {
            'id': v.id,
            'placa': v.placa,
            'modelo': v.modelo,
            'marca': v.marca,
            'ano': v.ano,
            'tipo': v.tipo,
            'ativo': v.ativo
        } for v in veiculos
    ]

    return jsonify(lista_de_veiculos)
