# Deploy da Aplicação

## Opções de Deploy Gratuito

### 1️⃣ Render.com (Recomendado)

**Passos:**

1. Crie uma conta em [render.com](https://render.com)
2. Clique em "New +" → "Web Service"
3. Conecte seu repositório GitHub
4. Configure:
   - **Name:** satisfaction-survey
   - **Environment:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
5. Clique em "Create Web Service"

✅ **Vantagens:** SSL grátis, domínio próprio, fácil configuração

---

### 2️⃣ Railway.app

**Passos:**

1. Crie uma conta em [railway.app](https://railway.app)
2. Clique em "New Project" → "Deploy from GitHub repo"
3. Selecione seu repositório
4. Railway detecta automaticamente Flask
5. Deploy automático!

✅ **Vantagens:** Muito simples, CI/CD automático

---

### 3️⃣ PythonAnywhere

**Passos:**

1. Crie uma conta em [pythonanywhere.com](https://www.pythonanywhere.com)
2. Vá para "Web" → "Add a new web app"
3. Escolha Flask
4. Faça upload dos arquivos ou clone do GitHub
5. Configure o arquivo WSGI

✅ **Vantagens:** Especializado em Python

---

### 4️⃣ Vercel (com limitações)

**Passos:**

1. Instale Vercel CLI: `npm i -g vercel`
2. No diretório do projeto: `vercel`
3. Siga as instruções

⚠️ **Nota:** Vercel é mais adequado para Next.js, pode ter limitações com Flask

---

## Configuração do GitHub

```bash
# Inicializar repositório
git init

# Adicionar arquivos
git add .

# Commit inicial
git commit -m "Initial commit: Sistema de avaliação de satisfação"

# Adicionar remote (substitua pela sua URL)
git remote add origin https://github.com/seu-usuario/seu-repositorio.git

# Push para GitHub
git branch -M main
git push -u origin main
```

---

## Variáveis de Ambiente

Para deploy em produção, configure:

- `SECRET_KEY`: Chave secreta para sessões Flask
- `FLASK_ENV`: `production`

---

## Banco de Dados em Produção

O SQLite funciona bem para aplicações pequenas/médias. Para produção maior, considere:

- **PostgreSQL** (gratuito no Render/Railway)
- **MySQL**

---

## Monitoramento

Após o deploy, verifique:

- ✅ Interface de votação funcionando
- ✅ Registro de votos no banco
- ✅ Área administrativa acessível
- ✅ Gráficos carregando corretamente

---

## SSL/HTTPS

Todas as plataformas recomendadas fornecem SSL gratuito automaticamente!

---

## Custom Domain (Opcional)

Você pode adicionar um domínio personalizado em qualquer uma das plataformas:

1. Compre um domínio (Namecheap, GoDaddy, etc.)
2. Configure os DNS apontando para a plataforma
3. Adicione o domínio nas configurações da plataforma

---

## Suporte

Se encontrar problemas:

1. Verifique os logs na plataforma de deploy
2. Confirme que todas as dependências estão em `requirements.txt`
3. Teste localmente primeiro: `python app.py`
