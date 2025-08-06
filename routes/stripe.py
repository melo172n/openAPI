import stripe
from flask import Flask, jsonify, request, send_file, redirect, Blueprint
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from extensions import db
from models import Usuario, UsoProduto
import traceback
import os

api_stripe = Blueprint('stripe_bp', __name__)

# Use environment variables for security
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'sk_test_your_stripe_secret_key_here')
WEBHOOK_SECRET = os.getenv('STRIPE_WEBHOOK_SECRET', 'whsec_your_webhook_secret_here')

#////////////////////////////////////////////////// --- CONFIGURAÇÃO STRIPE --- /////////////////////////////////////////////////////////////////////////////////#

@api_stripe.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, WEBHOOK_SECRET
        )
    except stripe.error.SignatureVerificationError:
        return "Assinatura inválida", 400
    except Exception as e:
        return f"Erro ao processar webhook: {str(e)}", 400

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        cliente_email = session.get('customer_email') or session.get('customer_details', {}).get('email')

        usuario = Usuario.query.filter_by(email=cliente_email).first()
        if not usuario:
            return jsonify({"erro": "Usuário não encontrado"}), 404
        
        try:
            items = stripe.checkout.Session.list_line_items(session['id'])
        except Exception as e:
            error_msg = traceback.format_exc()
            print("Erro ao listar line_items:", error_msg)
            return f"Erro ao buscar produtos: {str(e)}", 500
        


        for item in items.data:
            product_id = item.price.product
            quantity = item.quantity or 1

            # Product mappings - replace with your actual product IDs
            if product_id == 'prod_EXAMPLE_CLEANER_5PACK':
                produto = 'file_cleaner'
                usos_por_item = 5
            elif product_id == 'prod_EXAMPLE_ADJUSTER_5PACK':
                produto = 'file_adjuster'
                usos_por_item = 5
            elif product_id == 'prod_EXAMPLE_ADJUSTER_SINGLE':
                produto = 'file_adjuster'
                usos_por_item = 1
            else:
                print(f"Produto desconhecido: {product_id}")
                continue

            usos_totais = quantity * usos_por_item

            uso = UsoProduto.query.filter_by(usuario_id=usuario.id, produto=produto).first()
            if not uso:
                uso = UsoProduto(usuario_id=usuario.id, produto=produto, usos_restantes=0)
                db.session.add(uso)

            uso.usos_restantes += usos_totais

        db.session.commit()
        print(f"Produtos atualizados para {cliente_email}")

    return jsonify({"status": "ok"})

