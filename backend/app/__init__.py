from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    """
    Cria e configura uma instância da aplicação Flask.
    Isso é conhecido como o padrão 'Application Factory'.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.api.veiculos import bp as veiculos_bp
    app.register_blueprint(veiculos_bp, url_prefix='/api')

    from app.api.alunos import bp as alunos_bp
    app.register_blueprint(alunos_bp, url_prefix='/api')

    from app.api.instrutores import bp as instrutores_bp
    app.register_blueprint(instrutores_bp, url_prefix='/api')

    from app.api.aula import bp as aula_bp
    app.register_blueprint(aula_bp, url_prefix='/api')

    @app.route('/health')
    def health_check():
        return "Backend está saudável"
    
    return app

from app import models
