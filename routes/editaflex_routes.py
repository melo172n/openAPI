from flask import Flask, jsonify, request, send_file, redirect, Blueprint, current_app, Response
from extensions import db
from models import UsoProduto, Usuario
from flask_jwt_extended import JWTManager
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import os
from io import BytesIO
import json

api_bp = Blueprint('funcoes', __name__)

# BINARY FILE PROCESSING CONFIGURATION
# ===========================================
# These patterns are examples for educational purposes only.
# Replace with your own patterns and offsets for your specific binary format.

# Configuration for reading specific bytes from binary files
# Format: list of hex offsets to read from
FILE_READ_OFFSETS = [
    0x0CA0, 0x0CA1, 0x0CA2, 0x0CA3,
    0x0CA4, 0x0CA5, 0x0CA6, 0x0CA7,
    0x0CA8, 0x0CA9, 0x0CAA, 0x0CAB,
    0x0CAC, 0x0CAD, 0x0CAE, 0x0CAF
]

# Standard binary modification patterns
# Format: (base_address, offset, hex_value_to_set)
# These are generic examples - customize for your binary format
FILE_FIXES_STANDARD = [
    # Generic header correction patterns
    (0x00E0, 11, 'FF'), (0x00E0, 12, 'FF'), 
    (0x0C20, 7, '00'), (0x02D0, 8, '00'),
    # Add your binary-specific patterns here
]

# Enhanced modification patterns with additional corrections
# Use these for files that need more comprehensive modifications
FILE_FIXES_ENHANCED = [
    # Include all standard fixes
    (0x00E0, 11, 'FF'), (0x00E0, 12, 'FF'), 
    (0x0C20, 7, '00'), (0x02D0, 8, '00'),
    # Additional enhanced corrections
    (0x59B0, 2, '00'), (0x59B0, 3, '00'),
    (0x6160, 5, '01')
]

# Special mode activation patterns
# These patterns enable additional functionality in binary files
WORKSHOP_MODE_PATTERNS = [
    # Generic activation patterns - replace with your specific values
    (0x5A20, 1, '00'),
    (0x5A20, 2, '0D'),
    (0x7000, 2, '24')
]

# Error correction patterns for common file issues
# Use these to fix corrupted or problematic binary files
ERROR_FIXES = [
    # Generic error correction patterns
    (0x0E0, 11, 'FF'), (0x0E0, 12, 'FF'),
    (0x0C20, 6, '00'), (0x0C20, 7, '00'),
    (0x5A20, 1, '00'), (0x5A20, 2, '0D'),
    (0x7000, 2, '24')
]

@api_bp.route('/api', methods=['POST'])
@jwt_required()
def listar_arquivos_exemplo():
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'sample_files')
    if os.path.exists(upload_folder):
        arquivos = os.listdir(upload_folder)
        arquivos = [arq for arq in arquivos if arq.endswith(('.bin', '.BIN'))]
    else:
        arquivos = []
    return jsonify({'arquivos_exemplo': arquivos})


@api_bp.route('/api/sample-data', methods=['GET'])
def listar_dados_exemplo():
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        json_path = os.path.join(base_dir, 'arquivos.json')

        if not os.path.exists(json_path):
            return jsonify({"erro": "Arquivo JSON não encontrado"}), 404

        with open(json_path, 'r', encoding='utf-8') as file:
            dados = json.load(file)

        return jsonify(dados)

    except Exception as e:
        return jsonify({"erro": str(e)}), 500


@api_bp.route('/api/load', methods=['POST'])
@jwt_required()
def carregar_arquivo():
    
    VALORES_LIDOS = []
    conteudo = bytearray()

    if 'arquivo' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo enviado.'})

    arquivo = request.files['arquivo']

    if not arquivo.filename.endswith(('.bin', '.BIN')):
        return jsonify({'erro': 'O arquivo deve ser .bin'})

    conteudo = arquivo.read()

    VALORES_LIDOS = []
    for endereco in FILE_READ_OFFSETS:
        if endereco < len(conteudo):
            VALORES_LIDOS.append(conteudo[endereco])
        else:
            VALORES_LIDOS.append(None)

    return jsonify({'valores_lidos': VALORES_LIDOS}), 200

@api_bp.route('/api/load-pessoal', methods=['POST'])
@jwt_required()
def carregar_arquivo_pessoal():
    conteudo = bytearray()

    if 'arquivo_doador_pessoal' not in request.files:
        return jsonify({'erro': 'Nenhum arquivo foi enviado.'})

    arquivo_doador_pessoal = request.files['arquivo_doador_pessoal']

    if not arquivo_doador_pessoal.filename.endswith(('.bin', '.BIN')):
        return jsonify({'erro': 'O arquivo deve ser .bin'})
    
    conteudo = bytearray(arquivo_doador_pessoal.read())

    return Response(
    bytes(conteudo),
    mimetype='application/octet-stream'
    )


@api_bp.route('/api/download', methods=['POST'])
@jwt_required()
def baixar_arquivo():
    # Returns a sample reset file for demonstration purposes
    caminho_arquivo = os.path.join(current_app.config['UPLOAD_FOLDER'], 'sample_reset.BIN')

    try:
        return send_file(caminho_arquivo, as_attachment=True)
    except FileNotFoundError:
        return jsonify({'erro': 'Arquivo de exemplo não encontrado. Adicione arquivos de exemplo na pasta sample_files/'}), 404


@api_bp.route('/api/fix-errors', methods=['POST'])
@jwt_required()
def corrigir_erros_arquivo():

    arquivo = request.files['arquivo']

    conteudo = bytearray(arquivo.read())

    if conteudo is None:
        return jsonify({'erro': 'Nenhum arquivo foi carregado'}), 400

    for base, pos, hexval in ERROR_FIXES:
        idx = base + pos
        byte_val = bytes.fromhex(hexval)[0]
        if idx < len(conteudo):
            conteudo[idx] = byte_val
        else:
            conteudo.extend([0x00] * (idx - len(conteudo) + 1))
            conteudo[idx] = byte_val

    erro = descontar_uso('file_adjuster')
    if erro:
        return erro

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_corrigido.bin",
        mimetype="application/octet-stream"
    )


@api_bp.route('/api/process-standard', methods=['POST', 'GET'])
@jwt_required()
def processar_arquivo_padrao():

    response, status = carregar_arquivo()
    if status != 200:
        return response, status

    VALORES_LIDOS = response.get_json().get('valores_lidos', [])
    arquivo_doador_pessoal = None
    arquivo_doador = None

    if 'arquivo_doador_pessoal' in request.files:
        arquivo_doador_pessoal = request.files['arquivo_doador_pessoal']
        conteudo = bytearray(arquivo_doador_pessoal.read())
    else:
        arquivo_doador = request.form.get('arquivo_doador')
        if not arquivo_doador:
            return jsonify({'erro': 'Campo "arquivo_doador" não foi enviado'}), 400
        
    if arquivo_doador:
        caminho_doador = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            arquivo_doador
        )
        if not os.path.exists(caminho_doador):
            return jsonify({'erro': 'Arquivo doador não encontrado'}), 404

        with open(caminho_doador, 'rb') as f:
            conteudo = bytearray(f.read())


    for i, offset in enumerate(FILE_READ_OFFSETS):
        if i < len(VALORES_LIDOS) and offset < len(conteudo):
            conteudo[offset] = VALORES_LIDOS[i]

    for addr in range(0x0600, 0x063F + 1):
        if addr < len(conteudo):
            conteudo[addr] = 0x00
        else:
            conteudo.extend([0x00] * (addr - len(conteudo) + 1))

    for base, pos, hexval in FILE_FIXES_STANDARD:
        idx = base + pos
        byte_val = bytes.fromhex(hexval)[0]
        if idx < len(conteudo):
            conteudo[idx] = byte_val
        else:
            conteudo.extend([0x00] * (idx - len(conteudo) + 1))
            conteudo[idx] = byte_val

    erro = descontar_uso('file_adjuster')
    if erro:
        return erro

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_modificado.bin",
        mimetype="application/octet-stream"
    )



@api_bp.route('/api/process-enhanced', methods=['POST', 'GET'])
@jwt_required()
def processar_arquivo_avancado():

    response, status = carregar_arquivo()
    if status != 200:
        return response, status

    VALORES_LIDOS = response.get_json().get('valores_lidos', [])
    arquivo_doador_pessoal = None
    arquivo_doador = None

    if 'arquivo_doador_pessoal' in request.files:
        arquivo_doador_pessoal = request.files['arquivo_doador_pessoal']
        conteudo = bytearray(arquivo_doador_pessoal.read())
    else:
        arquivo_doador = request.form.get('arquivo_doador')
        if not arquivo_doador:
            return jsonify({'erro': 'Campo "arquivo_doador" não foi enviado'}), 400
        
    if arquivo_doador:
        caminho_doador = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            arquivo_doador
        )
        if not os.path.exists(caminho_doador):
            return jsonify({'erro': 'Arquivo doador não encontrado'}), 404

        with open(caminho_doador, 'rb') as f:
            conteudo = bytearray(f.read())


    for i, offset in enumerate(FILE_READ_OFFSETS):
        if i < len(VALORES_LIDOS) and offset < len(conteudo):
            conteudo[offset] = VALORES_LIDOS[i]

    for addr in range(0x0600, 0x063F + 1):
        if addr < len(conteudo):
            conteudo[addr] = 0x00
        else:
            conteudo.extend([0x00] * (addr - len(conteudo) + 1))

    for base, pos, hexval in FILE_FIXES_ENHANCED:
        idx = base + pos
        byte_val = bytes.fromhex(hexval)[0]
        if idx < len(conteudo):
            conteudo[idx] = byte_val
        else:
            conteudo.extend([0x00] * (idx - len(conteudo) + 1))
            conteudo[idx] = byte_val

    erro = descontar_uso('file_adjuster')
    if erro:
        return erro

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_modificado.bin",
        mimetype="application/octet-stream"
    )

@api_bp.route('/api/activate-special-mode', methods=['POST'])
@jwt_required()
def ativar_modo_especial():

    erro = descontar_uso('file_adjuster')
    if erro:
        return erro  # Retorna o erro se não houver créditos

    conteudo = bytearray()

    if conteudo is None:
        return jsonify({'erro': 'Nenhum arquivo foi carregado'}), 400
    
    for base, pos, hexval in WORKSHOP_MODE_PATTERNS:
        idx = base + pos
        byte_val = bytes.fromhex(hexval)[0]
        if idx < len(conteudo):
            conteudo[idx] = byte_val
        else:
            conteudo.extend([0x00] * (idx - len(conteudo) + 1))
            conteudo[idx] = byte_val

    buffer = BytesIO(conteudo)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="arquivo_modificado.bin",
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
        return jsonify({"erro": "Sem créditos restantes para File Adjuster."}), 400

    uso_produto.usos_restantes -= 1
    db.session.commit()

    return None  # Retorna None se tudo ocorrer bem

def erro_usuarios_sem_creditos(produto_nome):
    erro_response = {
        "erro": f"Você não tem créditos suficientes para o produto {produto_nome}."
    }
    return jsonify(erro_response), 403