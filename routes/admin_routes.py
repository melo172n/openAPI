from flask import Flask, jsonify, request, redirect, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from flask_mail import Mail, Message
from extensions import db
from models import Usuario

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/users', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([usuario.to_dict() for usuario in usuarios]), 201

@admin_bp.route('/users', methods=['POST'])
def criar_usuario():
    data = request.get_json()
    novo_usuario = Usuario(nome=data['nome'], email=data['email'], senha=data['senha'])
    db.session.add(novo_usuario)
    db.session.commit()
    return jsonify(novo_usuario.dict()), 201

@admin_bp.route('/users/<int:id>', methods=['PUT'])
def atualizar_usuario():
    usuario = Usuario.query.get_or_404(id)
    data = request.get_json()
    nome_usuario = data.get('nome', nome_usuario)
    email_usuario = data.get('email', email_usuario)
    db.session.commit()
    return jsonify(usuario.to_dict())

@admin_bp.route('/users/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"mensagem": "Usuário deletado"})

