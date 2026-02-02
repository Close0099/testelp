# Sistema de Avaliação de Satisfação

Aplicação web full-stack para coleta de feedback de satisfação com interface responsiva e área administrativa com estatísticas.

## 🚀 Tecnologias

- **Backend:** Python 3, Flask
- **Database:** SQLite
- **Frontend:** HTML5, CSS3, JavaScript
- **Gráficos:** Chart.js
- **Deploy:** Render / Railway (gratuito)

## 📦 Instalação

```bash
# Clonar repositório
git clone <seu-repositorio>
cd testelp

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## ▶️ Executar Localmente

```bash
python app.py
```

Acesse:
- **Interface de Votação:** http://localhost:5000
- **Área Administrativa:** http://localhost:5000/admin

## 🌐 Deploy

### Render.com (Gratuito)
1. Faça fork deste repositório
2. Crie conta no Render.com
3. Conecte seu repositório GitHub
4. Configure como Web Service
5. Deploy automático!

### Railway.app (Gratuito)
1. Crie conta no Railway.app
2. New Project → Deploy from GitHub
3. Selecione o repositório
4. Deploy automático!

## 📊 Funcionalidades

- ✅ Interface full-screen responsiva
- ✅ 3 botões de avaliação com emojis
- ✅ Feedback visual após votação
- ✅ Bloqueio de múltiplos cliques (timeout de 3 segundos)
- ✅ Registro automático com data/hora
- ✅ Área administrativa protegida
- ✅ Estatísticas em tempo real com gráficos
- ✅ Análise por período (dia, semana, mês)

## 📝 Licença

MIT License
