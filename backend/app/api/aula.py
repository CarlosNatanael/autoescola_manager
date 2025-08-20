from flask import Blueprint, request, jsonify
from app.models import Aula, Aluno, Instrutor, Veiculo
from app import db
from datetime import datetime, timedelta

bp = Blueprint('aulas', __name__)

@bp.route('/aulas', methods=['POST'])
def agendar_aula():
    """
    Endpoint para agendar uma nova aula.
    A duração da aula é fixada em 50 minutos.
    """
    dados = request.get_json()
    campos_obrigatorios = ['aluno_id', 'instrutor_id', 'veiculo_id', 'data_hora_inicio']
    if not dados or not all(campo in dados for campo in campos_obrigatorios):
        return jsonify({'erro': 'Dados incompletos.'}), 400

    try:
        inicio_aula = datetime.fromisoformat(dados['data_hora_inicio'])
        fim_aula = inicio_aula + timedelta(minutes=50)
    except ValueError:
        return jsonify({'erro': 'Formato de data inválido. Use o formato ISO (YYYY-MM-DDTHH:MM:SS).'}), 400

    # --- Validação de Conflitos ---
    # Verifica se o instrutor está disponível
    conflito_instrutor = Aula.query.filter(
        Aula.instrutor_id == dados['instrutor_id'],
        Aula.data_hora_inicio < fim_aula,
        Aula.data_hora_fim > inicio_aula
    ).first()
    if conflito_instrutor:
        return jsonify({'erro': 'Instrutor já possui uma aula neste horário.'}), 409

    # Verifica se o aluno está disponível
    conflito_aluno = Aula.query.filter(
        Aula.aluno_id == dados['aluno_id'],
        Aula.data_hora_inicio < fim_aula,
        Aula.data_hora_fim > inicio_aula
    ).first()
    if conflito_aluno:
        return jsonify({'erro': 'Aluno já possui uma aula neste horário.'}), 409

    # Verifica se o veículo está disponível
    conflito_veiculo = Aula.query.filter(
        Aula.veiculo_id == dados['veiculo_id'],
        Aula.data_hora_inicio < fim_aula,
        Aula.data_hora_fim > inicio_aula
    ).first()
    if conflito_veiculo:
        return jsonify({'erro': 'Veículo já está em uso neste horário.'}), 409

    nova_aula = Aula(
        aluno_id=dados['aluno_id'],
        instrutor_id=dados['instrutor_id'],
        veiculo_id=dados['veiculo_id'],
        data_hora_inicio=inicio_aula,
        data_hora_fim=fim_aula
    )

    db.session.add(nova_aula)
    db.session.commit()

    return jsonify({'mensagem': 'Aula agendada com sucesso!', 'id': nova_aula.id}), 201

@bp.route('/aulas/<int:id>', methods=['PUT'])
def atualizar_aula(id):
    """Endpoint para atualizar uma aula existente."""
    aula = Aula.query.get_or_404(id)
    dados = request.get_json()

    if not dados:
        return jsonify({'erro': 'Dados incompletos.'}), 400
    try:
        inicio_aula = datetime.fromisoformat(dados['data_hora_inicio'])
        fim_aula = inicio_aula + timedelta(minutes=50)
    except (ValueError, KeyError):
        return jsonify({'erro': 'Formato de data inválida ou ausente.'}), 400
    
    query_filter = lambda model, field_id: (
        model.query.filter(
            field_id == dados.get(field_id.key),
            model.data_hora_inicio < fim_aula,
            model.data_hora_fim > inicio_aula,
            model.id != id
        ).first()
    )

    if query_filter(Aula, Aula.instrutor_id):
        return jsonify({'erro': 'Instrutor já possui uma aula neste horário.'}), 409
    if query_filter(Aula, Aula.aluno_id):
        return jsonify({'erro': 'Aluno já possui uma aula neste horário'}), 409
    if query_filter(Aula, Aula.veiculo_id):
        return jsonify({'erro': 'Veículo já está em uso neste horário.'}), 409
    
    aula.aluno_id = dados.get('aluno_id', aula.aluno_id)
    aula.intrutor_id = dados.get('instrutor_id', aula.instrutor_id)
    aula.veiculo_id = dados.get('veiculo_id', aula.veiculo_id)
    aula.data_hora_inicio = inicio_aula
    aula.data_hora_fim = fim_aula
    aula.status = dados.get('status', aula.status)

    db.session.commit()
    return jsonify({'mensagem': 'Aula atualizada com sucesso!'})

@bp.route('/aulas/<int:id>', methods=['DELETE'])
def deletar_aula(id):
    """Endpoint para deletar uma aula"""
    aula = Aula.query.get_or_404(id)
    db.session.delete(aula)
    db.session.commit()
    return jsonify({'mensagem': 'Aula deletada com sucesso!'})

@bp.route('/aulas', methods=['GET'])
def listar_aulas():
    """
    Endpoint para listar todas as aulas agendadas.
    """
    aulas = Aula.query.order_by(Aula.data_hora_inicio.asc()).all()
    lista_de_aulas = [
        {
            'id': aula.id,
            'data_hora_inicio': aula.data_hora_inicio.isoformat(),
            'data_hora_fim': aula.data_hora_fim.isoformat(),
            'status': aula.status.value,
            'aluno': {
                'id': aula.aluno.id,
                'nome': aula.aluno.nome
            },
            'instrutor': {
                'id': aula.instrutor.id,
                'nome': aula.instrutor.nome
            },
            'veiculo': {
                'id': aula.veiculo.id,
                'placa': aula.veiculo.placa
            }
        } for aula in aulas
    ]
    return jsonify(lista_de_aulas)
