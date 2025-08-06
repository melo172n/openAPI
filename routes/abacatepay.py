import requests
from flask import Flask, jsonify, request, send_file, redirect, Blueprint
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from extensions import db
from models import Usuario, UsoProduto

api_abacate = Blueprint('abacate_bp', __name__)

ABACATEPAY_TOKEN = "abc_dev_35xztjZgewJnDcqSmgGGrRL1"

ABACATEPAY_API = "https://api.abacatepay.com/v1"

def criar_pagamento(cliente, produto):
    url = f"{ABACATEPAY_API}/billing/create"
    headers = {
        "Authorization": f"Bearer {ABACATEPAY_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "frequency": "ONE_TIME",
        "methods": ["PIX"],
        "products": [produto],
        "returnUrl": "https://editaflex.com/retorno",       # se cliente cancela
        "completionUrl": "https://editaflex.com/sucesso",   # se cliente paga
        "customerId": cliente["email"],
        "customer": cliente
    }
    response = requests.post(url, json=payload, headers=headers)
    return response.json()

@api_abacate.route("/criar-pagamento", methods=['POST'])
def iniciar_pagamento():
    try:
        data = request.get_json()

        cliente = {
            "name": data["nome"],
            "cellphone": data["celular"],
            "email": data["email"],
            "cpf": data["cpf"]
        }

        produto = {
            "externalId": "prod-bvdr",
            "name": "BVDR Adjuster",
            "description": "5 Usos para BVDR Adjuster",
            "quantity": 1,
            "price": 45000  # em centavos: R$10,00
        }

        resposta = criar_pagamento(cliente, produto)

        if "paymentUrl" in resposta:
            return jsonify({"url_pagamento": resposta["paymentUrl"]})
        else:
            return jsonify({"erro": "Erro ao criar pagamento", "detalhes": resposta}), 400

    except Exception as e:
        return jsonify({"erro": "Erro interno", "detalhes": str(e)}), 500
    
@api_abacate.route('/completado/bvdradj', methods=['POST'])
def pagamento_completado_bvdradj():
    dados = request.get_json()
    external_id = dados.get("externalId")

    if not external_id or not external_id.startswith("user-"):
        return jsonify({"erro": "ID inválido"}), 400

    usuario_id = int(external_id.replace("user-", ""))
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    produto = 'bvdr_adjuster'
    uso = UsoProduto.query.filter_by(usuario_id=usuario.id, produto=produto).first()
    if uso:
        uso.usos_restantes += 5
    else:
        novo_uso = UsoProduto(usuario_id=usuario.id, produto=produto, usos_restantes=5)
        db.session.add(novo_uso)

    db.session.commit()
    return jsonify({"mensagem": "Pagamento confirmado e créditos adicionados"}), 200

@api_abacate.route('/completado/bsgcleaner', methods=['POST'])
def pagamento_completado_bsg():
    dados = request.get_json()
    external_id = dados.get("externalId")

    if not external_id or not external_id.startswith("user-"):
        return jsonify({"erro": "ID inválido"}), 400

    usuario_id = int(external_id.replace("user-", ""))
    usuario = Usuario.query.get(usuario_id)

    if not usuario:
        return jsonify({"erro": "Usuário não encontrado"}), 404

    # Créditos nos produtos (exemplo: 10 para cada)
    produto = 'bsg_cleaner'
    uso = UsoProduto.query.filter_by(usuario_id=usuario.id, produto=produto).first()
    if uso:
        uso.usos_restantes += 5
    else:
        novo_uso = UsoProduto(usuario_id=usuario.id, produto=produto, usos_restantes=10)
        db.session.add(novo_uso)

    db.session.commit()
    return jsonify({"mensagem": "Pagamento confirmado e créditos adicionados"}), 200

@api_abacate.route("/abacate/webhook", methods=["POST"])
def webhook_abacatepay():
    try:
        payload = request.get_json()
        print("Webhook recebido:", payload)

        if payload.get("status") == "PAID":
            email = payload["customer"]["email"]
            produto_id = payload["products"][0]["externalId"]

            # Aqui você adicionaria o crédito ao usuário no banco de dados
            print(f"Pagamento confirmado para {email}, produto {produto_id}")

        return jsonify({"status": "recebido"}), 200

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


