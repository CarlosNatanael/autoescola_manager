from app import create_app, db
from app.models import Usuario, UserRole
from getpass import getpass

app = create_app()

with app.app_context():
    print("--- Criação do Utilizador Administrador ---")
    
    # Obter os dados do novo administrador
    email = input("Digite o email do administrador: ")
    # --- NOVO CAMPO ADICIONADO ---
    cpf = input("Digite um CPF para o administrador (ex: 000.000.000-00): ")
    senha = getpass("Digite a senha do administrador: ")
    confirma_senha = getpass("Confirme a senha: ")

    # Validar os dados
    if senha != confirma_senha:
        print("\n[ERRO] As senhas não coincidem. Operação cancelada.")
        exit()

    if Usuario.query.filter_by(email=email).first():
        print(f"\n[ERRO] O email '{email}' já existe na base de dados. Operação cancelada.")
        exit()
        
    if Usuario.query.filter_by(cpf=cpf).first():
        print(f"\n[ERRO] O CPF '{cpf}' já existe na base de dados. Operação cancelada.")
        exit()

    # Criar o novo utilizador administrador
    try:
        admin = Usuario(
            nome="Administrador",
            email=email,
            # --- NOVO CAMPO ADICIONADO ---
            cpf=cpf, 
            role=UserRole.ADMIN
        )
        admin.set_password(senha)

        db.session.add(admin)
        db.session.commit()
        
        print(f"\n[SUCESSO] Utilizador administrador '{email}' criado com sucesso!")

    except Exception as e:
        print(f"\n[ERRO] Ocorreu um erro ao criar o utilizador: {e}")