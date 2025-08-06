from extensions import db
from sqlalchemy import Enum, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    email_token = db.Column(db.String(36), unique=True, nullable=False)
    email_token_created_at = db.Column(db.DateTime(timezone=True), default=func.now())
    token_pw = db.Column(db.String(36), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    usos_produto = relationship("UsoProduto", backref="usuario", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'is_verified': self.is_verified,
            'email_token': self.email_token,
            'email_token_created_at': self.email_token_created_at,
            'token_pw': self.token_pw,
            'is_admin': self.is_admin,
            'produtos': [
                {
                    'produto': uso.produto,
                    'usos_restantes': uso.usos_restantes
                } for uso in self.usos_produto
            ]
        }

class UsoProduto(db.Model):
    __tablename__ = 'usos_produto'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    produto = db.Column(db.String(50), nullable=False)  # 'bsg_cleaner' ou 'bvdr_adjuster'
    usos_restantes = db.Column(db.Integer, default=0)

    table_args = (
        db.UniqueConstraint('usuario_id', 'produto', name='usuario_produto_unique'),
    )