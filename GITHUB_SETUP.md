# 🚀 Guia Completo - GitHub

## Pré-requisitos

1. **Git instalado**: https://git-scm.com/download/win
   - Instale com as opções padrão

2. **Conta GitHub**: https://github.com/join
   - Crie uma conta gratuitamente

---

## Método 1: Automático (Recomendado)

Clique duas vezes em `git_setup.bat` e siga as instruções.

---

## Método 2: Manual pelo Terminal

### Passo 1: Inicializar Repositório
```bash
cd c:\Users\ESRP\Desktop\testelp
git init
git config user.name "Seu Nome"
git config user.email "seu.email@gmail.com"
```

### Passo 2: Adicionar Arquivos
```bash
git add .
```

### Passo 3: Fazer Commit
```bash
git commit -m "Initial commit: Sistema de avaliação de satisfação full-stack"
```

### Passo 4: Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Nome: `testelp`
3. Descrição: `Sistema web full-stack de avaliação de satisfação`
4. Selecione: **Public** (para ser acessível)
5. **NÃO** marque "Initialize this repository"
6. Clique em **"Create repository"**

### Passo 5: Conectar ao GitHub
```bash
git remote add origin https://github.com/SEU-USUARIO/testelp.git
git branch -M main
git push -u origin main
```

---

## Configurar Personal Access Token (Recomendado)

Para não ter que digitar password toda vez:

1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token
3. Nome: `git-cli`
4. Scope: marque `repo`
5. Copy o token
6. Usar como password quando Git pedir

---

## Depois de Fazer Push

### Cada vez que fizer mudanças:

```bash
git add .
git commit -m "Descrição da mudança"
git push
```

---

## Verificar Status

```bash
git status
git log
git remote -v
```

---

## Estrutura no GitHub

Após o push, o repositório terá:

```
testelp/
├── app.py
├── requirements.txt
├── templates/
├── static/
├── README.md
├── DEPLOY.md
├── SEGURANCA.md
├── ADMIN_FEATURES.md
└── ... (todos os arquivos)
```

---

## Deploy Automático (Opcional)

### Render.com
1. Vá para render.com
2. "New +" → "Web Service"
3. "Connect account" (GitHub)
4. Selecione `testelp`
5. Deploy automático! ✨

### Railway.app
1. railway.app
2. "New Project" → "Deploy from GitHub"
3. Autorize e selecione `testelp`
4. Deploy automático! ✨

---

## Dúvidas Comuns

**P: Preciso ter SSH key configurada?**
R: Não, pode usar HTTPS (password + token)

**P: Posso tornar privado depois?**
R: Sim, Settings → Visibility

**P: Como invito colaboradores?**
R: Settings → Collaborators → Add people

**P: Perderei os dados ao fazer push?**
R: Não! Os dados ficam em `.db` local e no seu computador. Git só armazena código.

---

## Próximos Passos

1. ✅ Push para GitHub
2. 📢 Compartilhar link: `https://github.com/SEU-USUARIO/testelp`
3. 🚀 Deploy em Render/Railway
4. 🎉 Sistema em produção!
