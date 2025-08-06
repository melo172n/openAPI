from flask import Flask, jsonify, request, send_file, redirect, Blueprint, current_app, Response
from extensions import db
from models import UsoProduto, Usuario
from flask_jwt_extended import JWTManager
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from io import BytesIO

bsgc_bp = Blueprint('file_cleaner', __name__)

# BINARY FILE CLEANING PATTERNS
# ===============================
# These patterns are examples for educational purposes.
# Customize these patterns for your specific binary file format and requirements.

# Cleaning pattern for Standard Type files
# Format: (base_address, offset_from_base, hex_value_to_set)
FILE_CLEANER_STANDARD = [
    # Generic cleaning patterns - modify for your file format
    (0x0100, 0, '00'), (0x0100, 1, '00'),
    (0x0200, 0, 'FF'), (0x0200, 1, 'FF'),
    # Add your specific cleaning patterns here
]

# Cleaning pattern for Compact Type files
FILE_CLEANER_COMPACT = [
    # Compact file cleaning patterns
    (0x0000, 0, '00'), (0x0000, 1, '00'),
    (0x0030, 0, '00'), (0x0030, 1, '00'),
]

# Cleaning pattern for Extended Type files  
FILE_CLEANER_EXTENDED = [
    # Extended format cleaning patterns
    (0x0160, 0, '00'), (0x0160, 1, '00'),
    (0x01A0, 0, '00'), (0x01A0, 1, '00'),
]

# Cleaning pattern for Advanced Type files
FILE_CLEANER_ADVANCED = [
    # Advanced file format cleaning - customize for your needs
    (0x4000, 0, '00'), (0x4000, 1, '00'),
    (0x4010, 0, '00'), (0x4010, 2, '00'),
    # Add your complete pattern array here
    # This is a simplified example
]

# Cleaning pattern for Complex Type files
FILE_CLEANER_COMPLEX = [
    # Complex file format patterns
    (0x0000, 4, '00'), (0x0000, 5, '00'),
    (0x0010, 4, '00'), (0x0010, 5, '00'), 
    (0x0020, 0, '00'), (0x0020, 1, '00'),
    # Add more complex patterns as needed
]

@bsgc_bp.route('/cleaner/load', methods=['POST'])
@jwt_required()
def carregar_arquivo():

    conteudo = bytearray()

    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo foi enviado.'})

    arquivo = request.files['arquivo']

    if not arquivo.filename.endswith(('.bin', '.BIN')):
        return jsonify({'erro': 'O arquivo deve ser .bin'})
    
    conteudo = bytearray(arquivo.read())

    return Response(
    bytes(conteudo),
    mimetype='application/octet-stream'
    )

@bsgc_bp.route('/cleaner/standard-format', methods=['POST'])
@jwt_required()
def clean_standard_format():

    response = carregar_arquivo()
    if response.status_code != 200:
        return response

    if 'arquivo' in request.files:
        arquivo = request.files['arquivo']
        conteudo = bytearray(arquivo.read())

    endereco_inicial = 0x1100
    endereco_final = 0x1530
    valor_fixo = 0xFF

    for endereco in range(endereco_inicial, endereco_final + 1):
        if endereco < len(conteudo):
            conteudo[endereco] = valor_fixo
        else:
            conteudo.append(valor_fixo)
    
    for base, pos, hexval in FILE_CLEANER_STANDARD:
        idx = base + pos
        byte_val = bytes.fromhex(hexval)[0]
        if idx < len(conteudo):
            conteudo[idx] = byte_val
        else:
            conteudo.extend([0x00] * (idx - len(conteudo) + 1))
            conteudo[idx] = byte_val

    erro = descontar_uso('file_cleaner')
    if erro:
        return erro

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_resetado.bin",
        mimetype="application/octet-stream"
    )

@bsgc_bp.route('/cleaner/compact-format', methods=['POST'])
@jwt_required()
def clean_compact_format():

    response = carregar_arquivo()
    if response.status_code != 200:
        return response

    if 'arquivo' in request.files:
        arquivo = request.files['arquivo']
        conteudo = bytearray(arquivo.read())
    
    for base, pos, hexval in FILE_CLEANER_COMPACT:
        idx = base + pos
        byte_val = bytes.fromhex(hexval)[0]
        if idx < len(conteudo):
            conteudo[idx] = byte_val
        else:
            conteudo.extend([0x00] * (idx - len(conteudo) + 1))
            conteudo[idx] = byte_val

    erro = descontar_uso('file_cleaner')
    if erro:
        return erro

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_resetado.bin",
        mimetype="application/octet-stream"
    )

@bsgc_bp.route('/cleaner/extended-format', methods=['POST'])
@jwt_required()
def clean_extended_format():

    response = carregar_arquivo()
    if response.status_code != 200:
        return response

    if 'arquivo' in request.files:
        arquivo = request.files['arquivo']
        conteudo = bytearray(arquivo.read())

    
    for base, pos, hexval in FILE_CLEANER_EXTENDED:
        idx = base + pos
        byte_val = bytes.fromhex(hexval)[0]
        if idx < len(conteudo):
            conteudo[idx] = byte_val
        else:
            conteudo.extend([0x00] * (idx - len(conteudo) + 1))
            conteudo[idx] = byte_val

    erro = descontar_uso('file_cleaner')
    if erro:
        return erro

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_resetado.bin",
        mimetype="application/octet-stream"
    )

@bsgc_bp.route('/cleaner/advanced-format', methods=['POST'])
@jwt_required()
def clean_advanced_format():

    response = carregar_arquivo()
    if response.status_code != 200:
        return response

    if 'arquivo' in request.files:
        arquivo = request.files['arquivo']
        conteudo = bytearray(arquivo.read())

    
    for base, pos, hexval in FILE_CLEANER_ADVANCED:
        idx = base + pos
        byte_val = bytes.fromhex(hexval)[0]
        if idx < len(conteudo):
            conteudo[idx] = byte_val
        else:
            conteudo.extend([0x00] * (idx - len(conteudo) + 1))
            conteudo[idx] = byte_val

    erro = descontar_uso('file_cleaner')
    if erro:
        return erro

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_resetado.bin",
        mimetype="application/octet-stream"
    )

@bsgc_bp.route('/cleaner/pattern-replace', methods=['POST'])
@jwt_required()
def clean_pattern_replace():

    response = carregar_arquivo()
    if response.status_code != 200:
        return response

    if 'arquivo' in request.files:
        arquivo = request.files['arquivo']
        conteudo = bytearray(arquivo.read())

    enderecos = [0x1FF0, 0x1FF1, 0x1FF2, 0x1FF3]

    try:
        padrao = bytes(conteudo[addr] for addr in enderecos)
    except IndexError:
        return jsonify({'erro': 'Endereço fora do tamanho do arquivo.'}), 400
    
    novo_valor = b'\x00\x00\x00\x00'

    conteudo = bytearray(bytes(conteudo).replace(padrao, novo_valor))

    erro = descontar_uso('file_cleaner')
    if erro:
        return erro

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_resetado.bin",
        mimetype="application/octet-stream"
    )

@bsgc_bp.route('/cleaner/complex-format', methods=['POST'])
@jwt_required()
def clean_complex_format():

    response = carregar_arquivo()
    if response.status_code != 200:
        return response

    if 'arquivo' in request.files:
        arquivo = request.files['arquivo']
        conteudo = bytearray(arquivo.read())

    
    for base, pos, hexval in FILE_CLEANER_COMPLEX:
        idx = base + pos
        byte_val = bytes.fromhex(hexval)[0]
        if idx < len(conteudo):
            conteudo[idx] = byte_val
        else:
            conteudo.extend([0x00] * (idx - len(conteudo) + 1))
            conteudo[idx] = byte_val

    erro = descontar_uso('file_cleaner')
    if erro:
        return erro

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_resetado.bin",
        mimetype="application/octet-stream"
    )

def descontar_uso(produto):

    usuario_id = get_jwt_identity()  
    usuario = Usuario.query.get(usuario_id)

    if usuario and usuario.is_admin:
        return None
    
    uso_produto = UsoProduto.query.filter_by(usuario_id=usuario_id, produto=produto).first()

    if not uso_produto:
        return jsonify({"erro": "Produto não encontrado para este usuário."}), 404
    
    if uso_produto.usos_restantes <= 0:
        return jsonify({"erro": "Sem créditos restantes para este produto."}), 400

    uso_produto.usos_restantes -= 1
    db.session.commit()

    return None 

def erro_usuarios_sem_creditos(produto_nome):
    erro_response = {
        "erro": f"Você não tem créditos suficientes para o produto {produto_nome}."
    }
    return jsonify(erro_response), 403



    



    



