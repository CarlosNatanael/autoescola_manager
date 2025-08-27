from flask import Blueprint, jsonify
from app.models import Aluno, Instrutor, Veiculo, Aula, AulaStatus
from sqlalchemy import func, extract
from app import db
from datetime import datetime, timedelta

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard/stats', methods=['GET'])
def get_stats():
    """
    Endpoint que calcula e retorna as principais estatísticas para o dashboard.
    """
    try:
        total_instrutores = db.session.query(func.count(Instrutor.id)).scalar() or 0
        total_veiculos_ativos = Veiculo.query.filter_by(ativo=True).count()
        
        hoje = datetime.utcnow()
        primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        if hoje.month == 12:
            proximo_mes_inicio = hoje.replace(year=hoje.year + 1, month=1, day=1)
        else:
            proximo_mes_inicio = hoje.replace(month=hoje.month + 1, day=1)
            
        ultimo_dia_mes = proximo_mes_inicio - timedelta(microseconds=1)

        aulas_concluidas_mes = Aula.query.filter(
            Aula.status == AulaStatus.CONCLUIDA,
            Aula.data_hora_inicio.between(primeiro_dia_mes, ultimo_dia_mes)
        ).count()

        total_alunos = db.session.query(func.count(Aluno.id)).scalar() or 0

        stats = {
            'total_alunos': total_alunos,
            'total_instrutores': total_instrutores,
            'total_veiculos_ativos': total_veiculos_ativos,
            'aulas_concluidas_mes': aulas_concluidas_mes
        }
        return jsonify(stats)

    except Exception as e:
        print(f"Erro ao calcular estatísticas do dashboard: {e}")
        return jsonify({'erro': str(e)}), 500

# --- ENDPOINTS PARA GRÁFICOS ---

@bp.route('/dashboard/aulas_por_mes', methods=['GET'])
def get_aulas_por_mes():
    """Retorna o número de aulas concluídas nos últimos 6 meses."""
    hoje = datetime.utcnow()
    dados_grafico = []
    
    for i in range(6):
        mes_alvo = hoje.month - i
        ano_alvo = hoje.year
        if mes_alvo <= 0:
            mes_alvo += 12
            ano_alvo -= 1
        
        contagem = Aula.query.filter(
            Aula.status == AulaStatus.CONCLUIDA,
            extract('year', Aula.data_hora_inicio) == ano_alvo,
            extract('month', Aula.data_hora_inicio) == mes_alvo
        ).count()
        

        nome_mes = datetime(ano_alvo, mes_alvo, 1).strftime("%b/%y")
        dados_grafico.append({'mes': nome_mes, 'aulas': contagem})
        
    return jsonify(list(reversed(dados_grafico)))

@bp.route('/dashboard/aulas_por_instrutor', methods=['GET'])
def get_aulas_por_instrutor():
    """Retorna a distribuição de aulas concluídas por instrutor no mês atual."""
    hoje = datetime.utcnow()
    primeiro_dia_mes = hoje.replace(day=1, hour=0, minute=0, second=0)

    resultado = db.session.query(
        Instrutor.nome,
        func.count(Aula.id)
    ).join(Aula, Instrutor.id == Aula.instrutor_id).filter(
        Aula.status == AulaStatus.CONCLUIDA,
        Aula.data_hora_inicio >= primeiro_dia_mes
    ).group_by(Instrutor.nome).order_by(func.count(Aula.id).desc()).all()

    dados_grafico = [{'instrutor': nome, 'aulas': contagem} for nome, contagem in resultado]
    return jsonify(dados_grafico)