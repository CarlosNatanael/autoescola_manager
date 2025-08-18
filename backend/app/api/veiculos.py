from flask import Blueprint, request, jsonify
from app.models import Veiculo
from app import db

bp = Blueprint('veiculos', __name__)

@bp.route('/veiculos', methods=['POST'])
def criar_veiculo():
    """
    Endpoint para cadastrar um novo veículo.
    Espera receber um JSON com os dados do veículo.
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
