# Binary File Processing System

Uma aplicação Flask completa para processamento e modificação de arquivos binários com sistema de autenticação, pagamentos e gerenciamento de créditos.

## 🚀 Características Principais

- **Processamento de Arquivos Binários**: Sistema flexível para modificação de arquivos .BIN usando padrões personalizáveis
- **Autenticação Completa**: Sistema de registro, login e verificação por email
- **Sistema de Créditos**: Pay-as-you-go com integração ao Stripe
- **Interface RESTful**: APIs bem estruturadas para todas as funcionalidades
- **Múltiplos Algoritmos**: Diferentes tipos de processamento (padrão, avançado, limpeza)
- **Gestão de Usuários**: Sistema completo de administração de usuários

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python)
- **Banco de Dados**: PostgreSQL
- **Autenticação**: JWT com cookies seguros
- **Email**: Flask-Mail
- **Pagamentos**: Stripe
- **ORM**: SQLAlchemy

## 📁 Estrutura do Projeto

```
backend/
├── app.py                  # Aplicação principal
├── config.py               # Configurações
├── models.py               # Modelos do banco de dados
├── extensions.py           # Extensões Flask
├── routes/                 # Rotas da aplicação
│   ├── user_routes.py      # Autenticação e usuários
│   ├── editaflex_routes.py # Processamento de arquivos
│   ├── bsgc_routes.py      # Limpeza de arquivos
│   ├── admin_routes.py     # Administração
│   └── stripe.py           # Integração pagamentos
├── sample_files/           # Arquivos de exemplo
└── requirements.txt        # Dependências
```

## ⚙️ Instalação e Configuração

### 1. Clonar o Repositório
```bash
git clone [your-repository-url]
cd backend
```

### 2. Criar Ambiente Virtual
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instalar Dependências
```bash
pip install -r requirements.txt
```

### 4. Configurar Variáveis de Ambiente
```bash
# Copiar arquivo de exemplo
cp config_example.env .env

# Editar .env com suas configurações
nano .env
```

### 5. Configurar Banco de Dados
```bash
# Criar banco PostgreSQL
# Atualizar DATABASE_URL no .env

# Executar aplicação (criará as tabelas automaticamente)
python app.py
```

## 🔧 Configuração

### Variáveis de Ambiente Essenciais

```env
# Banco de Dados
DATABASE_URL=postgresql://usuario:senha@localhost:5432/nome_db

# Autenticação
JWT_SECRET_KEY=sua-chave-jwt-super-secreta
SECRET_KEY=sua-chave-flask-super-secreta

# Email
MAIL_USERNAME=seu.email@gmail.com
MAIL_PASSWORD=sua-senha-de-app

# Stripe (opcional)
STRIPE_SECRET_KEY=sk_test_sua_chave_stripe
STRIPE_WEBHOOK_SECRET=whsec_seu_webhook_secret
```

## 🚀 Uso da API

### Autenticação

#### Registro
```bash
POST /register
Content-Type: application/json

{
  "nome": "Seu Nome",
  "email": "seu@email.com", 
  "senha": "suasenha123"
}
```

#### Login
```bash
POST /login
Content-Type: application/json

{
  "email": "seu@email.com",
  "senha": "suasenha123"
}
```

### Processamento de Arquivos

#### Upload e Processamento Padrão
```bash
POST /api/process-standard
Authorization: Bearer seu-jwt-token
Content-Type: multipart/form-data

arquivo: [arquivo.BIN]
arquivo_doador: nome_do_arquivo_template.BIN
```

#### Processamento Avançado
```bash
POST /api/process-enhanced
Authorization: Bearer seu-jwt-token
Content-Type: multipart/form-data

arquivo: [arquivo.BIN]
```

#### Limpeza de Arquivos
```bash
POST /cleaner/standard-format
Authorization: Bearer seu-jwt-token
Content-Type: multipart/form-data

arquivo: [arquivo.BIN]
```

## 📊 Sistema de Créditos

O sistema utiliza um modelo pay-as-you-go onde:

- **file_adjuster**: Processamento e modificação de arquivos
- **file_cleaner**: Limpeza e reset de arquivos

Créditos são gerenciados automaticamente via integração com Stripe.

## 🎯 Customização

### Adicionando Novos Padrões de Processamento

1. **Editar padrões em `routes/editaflex_routes.py`**:
```python
# Adicionar novos padrões
CUSTOM_PATTERNS = [
    (0x1000, 0, 'FF'),  # (endereço, offset, valor_hex)
    (0x2000, 5, '00'),
]
```

2. **Criar nova rota**:
```python
@api_bp.route('/api/custom-process', methods=['POST'])
@jwt_required()
def processar_customizado():
    # Sua lógica aqui
    pass
```

### Configuração de Tipos de Arquivo

Edite `arquivos.json` para adicionar novos tipos de arquivo:
```json
{
  "sample_files": {
    "SEU_TIPO": [
      {
        "modelo": "Modelo Exemplo",
        "nomearquivo": "arquivo_exemplo.BIN",
        "advanced_features": false
      }
    ]
  }
}
```

## 🔒 Segurança

- JWT tokens com cookies HTTPOnly
- Validação CSRF
- Rate limiting (configurável)
- Sanitização de uploads
- Configurações de CORS restritivas

## 🧪 Desenvolvimento

### Executar em Modo Debug
```bash
FLASK_ENV=development python app.py
```

### Testes
```bash
# Adicionar seus testes aqui
python -m pytest tests/
```

## 📝 Contribuição

1. Fork o projeto
2. Crie sua feature branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para dúvidas e suporte:
- Abra uma issue no repositório
- Consulte a documentação das APIs
- Verifique os logs da aplicação

---

**Nota**: Este é um projeto educacional/portfólio. Os padrões de processamento são exemplos genéricos. Para uso em produção, substitua pelos padrões específicos do seu domínio de aplicação.
