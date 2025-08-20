from flask import Blueprint, request, jsonify
from app.models import Aluno, Instrutor, Usuario, UserRole
from app import db
from datetime import datetime

bp = Blueprint('usuarios', __name__)

@bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    """Endpoint para cadastrar um novo usuário (Aluno ou Instrutor)."""
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
        nova_matricula = gerar_proxima_matricula()
        novo_usuario = Aluno(
            nome=dados['nome'],
            email=dados['email'],
            cpf=dados['cpf'],
            telefone=dados.get('telefone'),
            matricula=nova_matricula
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
    elif usuario.role == UserRole.INSTRUTOR and 'cnh' in dados:
        usuario.cnh = dados.get('cnh')

    db.session.commit()
    return jsonify({'mensagem': 'Usúario atualizado com sucesso'})

@bp.route('/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    """
    Endpoint para deletar um usuário.
    """
    usuario = Usuario.query.get_or_404(id)
    
    if (usuario.role == UserRole.ALUNO and usuario.aulas.first()) or \
       (usuario.role == UserRole.INSTRUTOR and usuario.aulas.first()):
        return jsonify({'erro': 'Não é possível excluir um usuário que já está associado a aulas.'}), 409

    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário deletado com sucesso!'})

def gerar_proxima_matricula():
    """
    Gera uma nova matrícula baseada na última existente.
    Formato: A0125 (Letra-Sequencial-Ano)
    """
    ano_atual = datetime.now().strftime('%y')
    ultimo_aluno = Aluno.query.order_by(Aluno.id.desc()).first()

    if not ultimo_aluno or not ultimo_aluno.matricula or len(ultimo_aluno.matricula) < 5:
        # Nenhum aluno ou matrícula inválida, começa do zero
        return f"A01{ano_atual}"

    letra = ultimo_aluno.matricula[0]
    num_str = ultimo_aluno.matricula[1:3]
    ano_antigo = ultimo_aluno.matricula[3:5]
    
    if ano_atual != ano_antigo:
        # Ano mudou, reseta a contagem
        return f"A01{ano_atual}"

    num = int(num_str)
    if num < 99:
        novo_num = num + 1
        return f"{letra}{novo_num:02d}{ano_atual}"
    else:
        # Chegou em 99, avança a letra e reseta o número
        nova_letra = chr(ord(letra) + 1)
        return f"{nova_letra}01{ano_atual}"

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