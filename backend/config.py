import os
from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configurações base da aplicação."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'A1D2D6A9A5E8'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'autoescola.db')
        
    SQLALCHEMY_TRACK_MODIFICATIONS = False