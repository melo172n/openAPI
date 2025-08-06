# API EditaFlex

## 📋 Sobre o Projeto

Este é um sistema web desenvolvido em Flask para processamento de arquivos binários, com foco em manipulação de dados hexadecimais e correção de padrões específicos. O projeto foi originalmente desenvolvido para uma empresa do setor automotivo e foi adaptado para versão pública removendo informações confidenciais.

## 🚀 Tecnologias Utilizadas

### Backend
- **Python 3.13**
- **Flask** - Framework web principal
- **SQLAlchemy** - ORM para banco de dados
- **Flask-JWT-Extended** - Autenticação e autorização JWT
- **Flask-Mail** - Sistema de envio de emails
- **PostgreSQL/MySQL** - Banco de dados (configurável)

### Integrações
- **Stripe API** - Processamento de pagamentos
- **Email Validation** - Validação de endereços de email

### Processamento de Arquivos
- **Manipulação de arquivos binários (.bin/.BIN)**
- **Processamento de dados hexadecimais**
- **Padrões de correção customizáveis**

## 🏗️ Arquitetura do Sistema

### Estrutura de Rotas

```
routes/
├── __init__.py
├── user_routes.py          # Autenticação e gestão de usuários
├── editaflex_routes.py     # Processamento principal de arquivos
├── bsgc_routes.py          # Limpeza e correção de arquivos
├── stripe.py               # Integração de pagamentos
├── admin_routes.py         # Funcionalidades administrativas
└── static/                 # Recursos estáticos
```

### Funcionalidades Principais

#### 1. Sistema de Usuários
- ✅ Registro com validação de email
- ✅ Login/Logout com JWT
- ✅ Recuperação de senha
- ✅ Verificação de email obrigatória
- ✅ Sistema de créditos por produto

#### 2. Processamento de Arquivos
- ✅ Upload de arquivos binários
- ✅ Leitura de offsets específicos
- ✅ Aplicação de padrões de correção
- ✅ Múltiplos tipos de processamento:
  - File Cleaner (Tipos A, B, C, D, E)
  - File Adjuster (padrões de correção)
  - Workshop Mode (ativação de modo oficina)
  - Error Corrections (correções específicas)

#### 3. Sistema de Pagamentos
- ✅ Integração com Stripe
- ✅ Webhook handling para confirmação de pagamentos
- ✅ Sistema de créditos automático
- ✅ Diferentes pacotes de produtos

#### 4. Administração
- ✅ Dashboard administrativo
- ✅ Gestão de usuários e créditos
- ✅ Bypass de cobrança para administradores

## 🛠️ Configuração e Instalação

### Pré-requisitos
- Python 3.8+
- PostgreSQL ou MySQL
- Conta Stripe (para pagamentos)
- Servidor SMTP (para emails)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/melo172n/openAPI.git
cd file-processing-platform
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
export STRIPE_SECRET_KEY="sk_test_your_stripe_key"
export STRIPE_WEBHOOK_SECRET="whsec_your_webhook_secret"
export DATABASE_URL="postgresql://user:pass@localhost/dbname"
export MAIL_SERVER="smtp.gmail.com"
export MAIL_USERNAME="your_email@gmail.com"
export MAIL_PASSWORD="your_password"
```

5. Inicialize o banco de dados:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Execute o servidor:
```bash
python app.py
```

## 📊 Padrões de Processamento

O sistema utiliza arrays de padrões para processar arquivos binários:

```python
# Exemplo de padrão de limpeza
FILE_CLEANER_TYPE_A = [
    (0x0100, 0, '00'),  # (endereço, posição, valor_hex)
    (0x0200, 0, 'FF'),
    # ... mais padrões
]
```

### Tipos de Processamento Disponíveis:

1. **File Cleaner** - Limpeza de dados específicos
2. **File Adjuster** - Ajustes e correções
3. **Workshop Mode** - Ativação de funcionalidades especiais
4. **Error Corrections** - Correções de erros específicos

## 🔧 Customização

### Adicionando Novos Padrões

1. Defina seu array de padrões em `editaflex_routes.py` ou `bsgc_routes.py`
2. Crie uma nova rota para processar o padrão
3. Adicione a lógica de aplicação dos padrões

### Exemplo:
```python
NEW_PATTERN = [
    (0x1000, 0, 'AA'),
    (0x1001, 0, 'BB'),
]

@api_bp.route('/api/new-process', methods=['POST'])
@jwt_required()
def new_process():
    # Lógica de processamento
    for base, pos, hexval in NEW_PATTERN:
        # Aplicar padrão
        pass
```

## 📁 Arquivos Binários

Os arquivos binários devem ser colocados na pasta `arquivos_montadoras/`. O sistema suporta:
- Arquivos `.bin` e `.BIN`
- Processamento de arquivos de até 32KB
- Múltiplos formatos de entrada

## 🔒 Segurança

- ✅ Autenticação JWT com refresh tokens
- ✅ Validação de entrada em todas as rotas
- ✅ CSRF protection
- ✅ Rate limiting implementável
- ✅ Sanitização de uploads de arquivo

## 📈 Sistema de Créditos

- Usuários compram créditos via Stripe
- Cada processamento consome 1 crédito
- Administradores têm acesso ilimitado
- Sistema automático de cobrança

## 🌟 Destaques Técnicos

### Manipulação de Dados Binários
- Leitura e escrita eficiente de arquivos binários
- Processamento de dados hexadecimais
- Aplicação de padrões complexos de correção

### Arquitetura Modular
- Separação clara de responsabilidades
- Rotas organizadas por funcionalidade
- Fácil extensibilidade

### Integração Completa
- Sistema completo de e-commerce
- Gestão de usuários robusta
- Processamento de pagamentos automatizado

## 📞 Suporte

Este projeto foi desenvolvido como demonstração de habilidades em:
- Desenvolvimento Backend com Python/Flask
- Integração de APIs (Stripe, Email)
- Processamento de arquivos binários
- Sistemas de autenticação e autorização
- Arquitetura de software modular

## ⚠️ Nota Importante

Esta é uma versão pública do projeto. Os dados específicos, arquivos binários proprietários e informações confidenciais foram removidos ou substituídos por exemplos genéricos.

---

**Desenvolvido por:** João Vitor de Oliveira Melo
**Tecnologia:** Python, Flask, SQLAlchemy, PostgreSQL, Stripe  
**Tipo:** Sistema Web para Processamento de Arquivos
