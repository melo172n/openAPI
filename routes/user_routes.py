from flask import Flask, jsonify, request, redirect, Blueprint, url_for, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, decode_token, set_access_cookies, get_csrf_token
from flask_mail import Mail, Message
from flask import make_response
from email_validator import validate_email, EmailNotValidError
from datetime import timedelta, datetime, timezone
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy import cast, literal
from extensions import db, mail
from models import Usuario, UsoProduto
import uuid
import os

user_bp = Blueprint('user', __name__)

PRODUTOS_VALIDOS = ['file_adjuster', 'file_cleaner']

@user_bp.route('/register', methods=['POST'])
def registrar():
    try:
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        
        print(nome)
        print(email)
        print(senha)

        if Usuario.query.filter_by(email=email).first():
            return jsonify({'erro': 'Email já registrado'}), 400

        if not nome or not email or not senha:
            return jsonify({"msg": "Nome, e-mail e senha são obrigatórios."}), 400

        if len(senha) < 7:
            return jsonify({"msg": "A senha deve ter pelo menos 7 caracteres."}), 400

        try:
            validate_email(email)
        except EmailNotValidError:
            return jsonify({"msg": "E-mail inválido."}), 400
        
        verification_token = str(uuid.uuid4())
        
        novo_usuario = Usuario(
            nome=nome,  
            email=email,
            senha=generate_password_hash(senha),
            is_verified=False,
            email_token=verification_token,
            email_token_created_at=datetime.now(timezone.utc),
            is_admin=False
    )
        db.session.add(novo_usuario)
        db.session.commit()

        domain = current_app.config.get('DOMAIN_NAME', 'localhost:3000')
        link = f"{domain}/verify-email?guid={verification_token}"
        msg = Message("Confirme seu e-mail", recipients=[email])
        msg.body = f"Clique no link para confirmar seu e-mail: {link}"
        mail.send(msg)

        produtos = [
            {'produto': 'file_adjuster', 'usos_restantes': 0},
            {'produto': 'file_cleaner', 'usos_restantes': 0}
        ]
        
        tipo_produto_enum = ENUM(name='tipoproduto')

        for produto in produtos:
            if produto['produto'] not in PRODUTOS_VALIDOS:
                return jsonify({'erro': 'Produto inválido'}), 400
            
            novo_uso = UsoProduto(
                usuario_id=novo_usuario.id, 
                produto=cast(literal(produto['produto']), tipo_produto_enum), 
                usos_restantes=produto['usos_restantes']
            )
            db.session.add(novo_uso)

        db.session.commit()

        access_token = create_access_token(identity=str(novo_usuario.id), additional_claims={"is_admin": novo_usuario.is_admin})
        response = make_response(jsonify({'mensagem': 'Registro concluído. Verifique seu E-mail para continuar !', 'E-mail': email}))
        set_access_cookies(response, access_token)

        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": str(e)}), 500
    
@user_bp.route('/verificar-email/<token>')
def verificar_email(token):
    try:
        usuario = Usuario.query.filter_by(email_token=token).first()

        if not usuario:
            return "Token Inválido.", 400

        agora = datetime.now(timezone.utc)
        created_at = usuario.email_token_created_at
        expiracao = created_at + timedelta(minutes=15)

        if agora > expiracao:
            return "Token inválido! Tempo expirado.", 400

        usuario.is_verified = True
        usuario.email_token = None
        usuario.email_token_created_at = None
        db.session.commit()

        return make_response(jsonify({'mensagem':'E-mail verificado com sucesso!'}), 200)
    except Exception as e:
        return make_response(jsonify({
            'mensagem': f'Token inválido ou expirado: {str(e)}'
        }), 400)
    
@user_bp.route('/reenviar-codigo', methods=['POST'])
def reenviar_codigo():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"erro": "Email é obrigatório"}), 400

    usuario = Usuario.query.filter_by(email=email).first()
    if not usuario:
        return jsonify({"erro": "E-mail não encontrado."}), 404

    if usuario.is_verified:
        return jsonify({"erro": "Este E-mail já foi verificado."}), 400

    agora = datetime.now(timezone.utc)
    limite = timedelta(minutes=15)


    novo_token = str(uuid.uuid4())
    usuario.email_token = novo_token
    usuario.email_token_created_at = agora
    db.session.commit()

    domain = current_app.config.get('DOMAIN_NAME', 'localhost:3000')
    link_confirmacao = f"{domain}/verify-email?guid={novo_token}"

    msg = Message("Confirme seu e-mail", recipients=[email])
    msg.body = f"Clique no link para confirmar seu e-mail: {link_confirmacao}"
    mail.send(msg)

    return jsonify({"mensagem": "Código de confirmação reenviado para o seu e-mail."})


@user_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario:
            return jsonify({'erro': 'Usuário não cadastrado'}), 404

        if not check_password_hash(usuario.senha, senha):
            return jsonify({'erro': 'Senha incorreta, tente novamente'}), 401
        
        if not usuario.is_verified:
            return jsonify({'erro': 'E-mail não verificado.'}), 403

        access_token = create_access_token(
            identity=str(usuario.id),
            additional_claims={"is_admin": usuario.is_admin}
        )

        csrf_token = get_csrf_token(access_token)
        
        response = make_response(jsonify({
            'mensagem': 'Logado com sucesso!',
            'usuario': usuario.email,
            'usuario_id': usuario.id,
            'csrf_token': csrf_token
        }))
        
        set_access_cookies(response, access_token)

        return response

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"erro": "Erro interno no servidor"}), 500

@user_bp.route('/recuperar-senha/<token>', methods=['POST'])
def recuperar_senha(token):
    data = request.get_json()
    nova_senha = data.get('nova_senha')

    if not nova_senha:
        return jsonify({"msg": "Preencha o campo com a nova senha!"}), 400

    usuario = Usuario.query.filter_by(token_pw=token).first()

    if not usuario:
        return jsonify({"msg": "Token inválido ou expirado."}), 400

    print("Usuário encontrado:", usuario.email)

    usuario.senha = generate_password_hash(nova_senha)
    usuario.token_pw = None

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print("Erro ao salvar no banco:", e)
        return jsonify({"msg": "Erro interno ao redefinir a senha."}), 500

    print("Senha redefinida com sucesso!")
    return jsonify({"msg": "Senha redefinida com sucesso!"}), 200


@user_bp.route('/esqueceu-senha', methods=['POST'])
def esqueceu_senha():
    data = request.get_json()
    email = data.get('email')

    usuario = Usuario.query.filter_by(email=email).first()

    if not usuario:
        return jsonify({"msg": "E-mail não encontrado."}), 404 

    reset_password_token = str(uuid.uuid4())

    usuario.token_pw = reset_password_token
    db.session.commit()

    domain = current_app.config.get('DOMAIN_NAME', 'localhost:3000')
    reset_link = f"{domain}/reset-password?guid={reset_password_token}"

    link = reset_link
    msg = Message("Alterar senha", recipients=[email])
    msg.body = f"Clique no link para alterar sua senha: {link}"

    msg.html = f"""
    <html>
        <body>
            <h2>Recuperar Senha</h2>
            <p>Clique no link para redefinir sua senha:</p>
            <a href="{reset_link}">{reset_link}</a>
            <br><br>
            <p>Se você não solicitou a alteração de senha, ignore este e-mail.</p>
        </body>
    </html>
    """
    
    try:
        mail.send(msg)
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return jsonify({"error": "Erro ao enviar e-mail de recuperação"}), 500

    return jsonify({"msg": "E-mail de recuperação enviado!"}), 200

@user_bp.route('/check-token', methods=['GET'])
@jwt_required()
def check_token():
    usuario_id = get_jwt_identity()
    
    # Busca o usuário com todos os relacionamentos
    usuario = Usuario.query.options(db.joinedload(Usuario.usos_produto)).get(usuario_id)
    
    if not usuario:
        return jsonify({'status': 'error', 'message': 'Usuário não encontrado'}), 404
    
    # Formata a resposta incluindo os produtos
    response_data = {
        'status': 'ok',
        'usuario_id': usuario.id,
        'is_admin': usuario.is_admin,
        'produtos': [
            {
                'produto': uso.produto,
                'usos_restantes': uso.usos_restantes
            } for uso in usuario.usos_produto
        ]
    }
    
    return jsonify(response_data), 200