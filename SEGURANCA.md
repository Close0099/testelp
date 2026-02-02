# 🔐 Segurança - Código de Acesso Admin

## Código Padrão

Por padrão, o código de acesso ao painel administrativo é: **1234**

## Acessar o Painel

1. Clique em ⚙️ no canto inferior direito da página de votação
2. Ou acesse diretamente: `http://localhost:5000/admin`
3. Digite o código: **1234**

## Mudar o Código de Acesso

### Opção 1: Variável de Ambiente (Recomendado para Produção)

**No Windows (CMD):**
```bash
set ADMIN_PASSWORD=seu-novo-codigo
python app.py
```

**No Windows (PowerShell):**
```bash
$env:ADMIN_PASSWORD="seu-novo-codigo"
python app.py
```

**No Linux/Mac:**
```bash
export ADMIN_PASSWORD=seu-novo-codigo
python app.py
```

### Opção 2: Arquivo .env (Local)

Crie um arquivo `.env` na raiz do projeto:

```
ADMIN_PASSWORD=seu-novo-codigo-aqui
SECRET_KEY=sua-chave-secreta-aleatorizada
```

Depois execute:
```bash
python app.py
```

## Deploy em Produção

### Render.com

1. No dashboard do Render
2. Vá para "Environment"
3. Adicione as variáveis:
   - `ADMIN_PASSWORD=seu-codigo-seguro`
   - `SECRET_KEY=gere-uma-chave-aleatorizada`

### Railway.app

1. Projeto → Variáveis
2. Adicione:
   - `ADMIN_PASSWORD=seu-codigo-seguro`
   - `SECRET_KEY=gere-uma-chave-aleatorizada`

## Dicas de Segurança

⚠️ **Use um código forte:**
- Mínimo 6 caracteres
- Misture números e letras
- Evite padrões óbvios (1234, 0000, etc.)

✅ **Exemplo de código bom:**
- `Avaliacao2026!`
- `Admin@Survey123`
- `Feedback#2026`

## Logout

Clique no botão "🚪 Sair" no canto superior direito do painel para fazer logout.

## Sessão

- A sessão fica ativa enquanto o navegador estiver aberto
- Fechar o navegador não faz logout automático
- Sempre use "Sair" antes de deixar o computador
