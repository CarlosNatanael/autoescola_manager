from app.models import Aluno, Aula, AulaStatus
from flask import Blueprint, jsonify
from sqlalchemy import func
from app import db

bp = Blueprint('dashboard', __name__)

@bp.route('/dashboard/stats', methods=['GET'])
def get_status():
    """Endpoint que calcula e retorna as principais estatisticas para o dashboard"""
    try:
        total_alunos = db.session.query(func.count(Aluno.id)).scalar()
        stats = {
            'total_alunos': total_alunos or 0
        }
        return jsonify(stats)
    except Exception as e:
        return jsonify({'erro': str(e)}), 500