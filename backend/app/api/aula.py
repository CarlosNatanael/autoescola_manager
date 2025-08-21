from flask import Blueprint, request, jsonify
from app.models import Aula, Aluno, Instrutor, Veiculo, AulaStatus
from app import db
from datetime import datetime, timedelta, date

bp = Blueprint('aulas', __name__)

@bp.route('/aulas/hoje', methods=['GET'])
def listar_aulas_hoje():
    """
    Endpoint para listar apenas as aulas agendadas para o dia corrente.
    """
    hoje_inicio = datetime.combine(date.today(), datetime.min.time())
    hoje_fim = datetime.combine(date.today(), datetime.max.time())

    aulas = Aula.query.filter(
        Aula.data_hora_inicio >= hoje_inicio,
        Aula.data_hora_inicio <= hoje_fim
    ).order_by(Aula.data_hora_inicio.asc()).all()
    
    lista_de_aulas = [
        {
            'id': aula.id,
            'data_hora_inicio': aula.data_hora_inicio.isoformat(),
            'aluno': { 'nome': aula.aluno.nome },
            'instrutor': { 'nome': aula.instrutor.nome },
            'status': aula.status.value,
        } for aula in aulas
    ]
    return jsonify(lista_de_aulas)

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
    conflito_instrutor = Aula.query.filter(
        Aula.instrutor_id == dados['instrutor_id'],
        Aula.data_hora_inicio < fim_aula,
        Aula.data_hora_fim > inicio_aula
    ).first()
    if conflito_instrutor:
        return jsonify({'erro': 'Instrutor já possui uma aula neste horário.'}), 409

    conflito_aluno = Aula.query.filter(
        Aula.aluno_id == dados['aluno_id'],
        Aula.data_hora_inicio < fim_aula,
        Aula.data_hora_fim > inicio_aula
    ).first()
    if conflito_aluno:
        return jsonify({'erro': 'Aluno já possui uma aula neste horário.'}), 409

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
        return jsonify({'erro': 'Formato de data inválido ou ausente.'}), 400
    
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
    aula.instrutor_id = dados.get('instrutor_id', aula.instrutor_id)
    aula.veiculo_id = dados.get('veiculo_id', aula.veiculo_id)
    if 'data_hora_inicio' in dados:
        try:
            inicio_aula = datetime.fromisoformat(dados['data_hora_inicio'])
            fim_aula = inicio_aula + timedelta(minutes=50)
            aula.data_hora_inicio = inicio_aula
            aula.data_hora_fim = fim_aula
        except (ValueError, KeyError):
            return jsonify({'erro': 'Formato de data inválido ou ausente.'}), 400

    # CORREÇÃO AQUI: Normaliza o status antes de salvar
    if 'status' in dados:
        try:
            # Converte o texto recebido (ex: 'agendada') para o membro do Enum (AulaStatus.AGENDADA)
            status_str = dados.get('status').upper() 
            aula.status = AulaStatus[status_str]
        except KeyError:
            return jsonify({'erro': f"Status '{dados.get('status')}' é inválido."}), 400

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
