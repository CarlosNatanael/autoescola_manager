from flask import Blueprint, request, jsonify
from app.models import Aluno, Usuario,  CategoriaCNH, AulaStatus, TipoAula
from app import db
from datetime import datetime

bp = Blueprint('alunos', __name__)

def gerar_proxima_matricula():
    """Gera uma nova matrícula baseada na última existente."""
    ano_atual = datetime.now().strftime('%y')
    ultimo_aluno = Aluno.query.order_by(Aluno.id.desc()).first()

    if not ultimo_aluno or not ultimo_aluno.matricula or len(ultimo_aluno.matricula) < 5:
        return f"A01{ano_atual}"

    letra = ultimo_aluno.matricula[0]
    num_str = ultimo_aluno.matricula[1:3]
    ano_antigo = ultimo_aluno.matricula[3:5]
    
    if ano_atual != ano_antigo:
        return f"A01{ano_atual}"

    num = int(num_str)
    if num < 99:
        novo_num = num + 1
        return f"{letra}{novo_num:02d}{ano_atual}"
    else:
        nova_letra = chr(ord(letra) + 1)
        return f"{nova_letra}01{ano_atual}"

@bp.route('/alunos', methods=['POST'])
def criar_aluno():
    """Endpoint para cadastrar um novo aluno."""

    dados = request.get_json()

    campos_obrigatorios = ['nome', 'email', 'cpf', 'categoria']
    if not dados or not all(campo in dados for campo in campos_obrigatorios):
        return jsonify({'erro': 'Nome, email, cpf, categoria são obrigatórios.'}), 400
    if Usuario.query.filter_by(email=dados['email']).first():
        return jsonify({'erro': 'Este email já está em uso.'}), 409
    if Usuario.query.filter_by(cpf=dados['cpf']).first():
        return jsonify({'erro': 'Este CPF já está cadastrado.'}), 409
    try:
        categoria_enum = CategoriaCNH[dados['categoria']]
    except KeyError:
        return jsonify({'erro': f"Categoria '{dados['categoria']}' é inválida."}), 400
    
    novo_aluno = Aluno(
        nome=dados['nome'],
        email=dados['email'],
        cpf=dados['cpf'],
        telefone=dados.get('telefone'),
        matricula=gerar_proxima_matricula(),
        categoria=categoria_enum,
        aulas_praticas_contratadas=dados.get('aulas_praticas_contratadas', 20),
        aulas_simulador_contratadas=dados.get('aulas_simulador_contratadas', 0),
        aulas_extras_contratadas=dados.get('aulas_extras_contratadas', 0)
    )
    db.session.add(novo_aluno)
    db.session.commit()
    return jsonify({'mensagem': 'Aluno cadastrado com sucesso!', 'id': novo_aluno.id}), 201

@bp.route('/alunos/<int:id>', methods=['PUT'])
def atualizar_aluno(id):
    """Endpoint para atualizar os dados de um aluno."""

    aluno = Aluno.query.get_or_404(id)
    dados = request.get_json()

    aluno.nome = dados.get('nome', aluno.nome)
    aluno.email = dados.get('email', aluno.email)
    aluno.cpf = dados.get('cpf', aluno.cpf)
    aluno.telefone = dados.get('telefone', aluno.telefone)
    aluno.aulas_praticas_contratadas = dados.get('aulas_praticas_contratadas', aluno.aulas_praticas_contratadas)
    aluno.aulas_simulador_contratadas = dados.get('aulas_simulador_contratadas', aluno.aulas_simulador_contratadas)
    aluno.aulas_extras_contratadas = dados.get('aulas_extras_contratadas', aluno.aulas_extras_contratadas)
    if 'categoria' in dados:
        try:
            aluno.categoria = CategoriaCNH[dados['categoria']]
        except KeyError:
            return jsonify({'erro': f"Categoria '{dados['categoria']} é inválido'"}), 400
        
    db.session.commit()
    return jsonify({'mensagem': 'Aluno atualizado com sucesso'})

@bp.route('/alunos/<int:id>', methods=['GET'])
def get_aluno(id):
    """Endpoint para buscar um único aluno pelo ID."""
    aluno = Aluno.query.get_or_404(id)
    return jsonify({
        'id': aluno.id,
        'nome': aluno.nome,
        'categoria': aluno.categoria.value if aluno.categoria else None
    })

@bp.route('/alunos/<int:id>', methods=['DELETE'])
def deletar_aluno(id):
    """Endpoint para deletar um aluno."""
    aluno = Aluno.query.get_or_404(id)
    if aluno.aulas.first():
        return jsonify({'erro': 'Não é possível excluir um aluno que já está associado a aulas.'}), 409
    db.session.delete(aluno)
    db.session.commit()
    return jsonify({'mensagem': 'Aluno deletado com sucesso!'})

@bp.route('/alunos', methods=['GET'])
def listar_alunos():
    """Endpoint para listar todos os alunos."""
    alunos = Aluno.query.all()
    lista_de_alunos = []
    for a in alunos:
        # Contar aulas concluídas para cada tipo
        aulas_praticas_feitas = a.aulas.filter_by(status=AulaStatus.CONCLUIDA, tipo_aula=TipoAula.PRATICA).count()
        aulas_simulador_feitas = a.aulas.filter_by(status=AulaStatus.CONCLUIDA, tipo_aula=TipoAula.SIMULADOR).count()
        aulas_extras_feitas = a.aulas.filter_by(status=AulaStatus.CONCLUIDA, tipo_aula=TipoAula.EXTRA).count()

        dados_aluno = {
            'id': a.id, 
            'nome': a.nome, 
            'email': a.email, 
            'cpf': a.cpf,
            'telefone': a.telefone, 
            'matricula': a.matricula, 
            'categoria': a.categoria.value if a.categoria else 'N/D',
            'aulas_praticas_contratadas': a.aulas_praticas_contratadas,
            'aulas_simulador_contratadas': a.aulas_simulador_contratadas,
            'aulas_extras_contratadas': a.aulas_extras_contratadas,
            # --- NOVOS CAMPOS COM O SALDO ---
            'aulas_praticas_feitas': aulas_praticas_feitas,
            'saldo_aulas_praticas': a.aulas_praticas_contratadas - aulas_praticas_feitas,
            'aulas_simulador_feitas': aulas_simulador_feitas,
            'saldo_aulas_simulador': a.aulas_simulador_contratadas - aulas_simulador_feitas,
            'aulas_extras_feitas': aulas_extras_feitas,
            'saldo_aulas_extras': a.aulas_extras_contratadas - aulas_extras_feitas
        }
        lista_de_alunos.append(dados_aluno)
        
    return jsonify(lista_de_alunos)