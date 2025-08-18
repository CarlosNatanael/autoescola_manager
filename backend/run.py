from app import create_app, db
from app.models import Aluno, Instrutor, Veiculo

app = create_app()

@app.shell_context_processor
def make_shell_context():
    """
    Permite que você acesse instâncias no shell do Flask
    com o comando `flask shell` sem precisar importá-las.
    Facilita muito a depuração.
    """
    return {'db':db, 'Aluno':Aluno, 'Instrutor':Instrutor, 'Veiculo':Veiculo}

if __name__=='__main__':
    app.run(debug=True)