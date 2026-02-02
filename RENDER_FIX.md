# 🔧 Corrigir Erro de Deploy no Render

## O que causou o erro:

`Exited with status 1 while building your code.` = Problema nas dependências ou configuração

---

## ✅ Solução - Reconfigurar no Render

### Passo 1: Fazer push das correções

```bash
git add .
git commit -m "Fix: Render deployment configuration"
git push
```

### Passo 2: Reimplementar no Render

1. Acesse: https://dashboard.render.com
2. Clique no serviço "satisfaction-survey"
3. **Settings** → **Delete service** (abaixo)
4. Confirme

### Passo 3: Criar novo serviço

1. Clique: **New +** → **Web Service**
2. Selecione: **Close0099/testelp**
3. Configure:
   - **Name:** satisfaction-survey
   - **Root Directory:** (deixe vazio)
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Environment:** (clique Add)
     - KEY: `FLASK_ENV`
     - VALUE: `production`
     - KEY: `ADMIN_PASSWORD`
     - VALUE: `1234` (ou seu código)
4. **Create Web Service**

---

## 🔍 Alternativa: Verificar Logs

Se ainda der erro:

1. Render Dashboard → satisfaction-survey
2. **Logs** → **Live tail**
3. Procure por mensagens de erro específicas
4. Envie a mensagem de erro completa

---

## 🚀 Se der certo:

A URL será: `https://satisfaction-survey.onrender.com`

- Votação: https://satisfaction-survey.onrender.com
- Admin: https://satisfaction-survey.onrender.com/admin (código: 1234)

---

## ⚠️ Nota sobre dados:

O Render usa armazenamento efémero, então:
- ✅ Dados salvos enquanto o app está rodando
- ❌ Dados perdidos ao restart
- 💡 Solução: Usar PostgreSQL (pago) ou guardar em ficheiro

Para agora, funciona bem para testes!
