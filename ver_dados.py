import sqlite3
from datetime import datetime

# Conecta ao banco de dados
conn = sqlite3.connect('satisfaction.db')
cursor = conn.cursor()

# Verifica se a tabela existe
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='avaliacoes'")
if not cursor.fetchone():
    print("❌ Tabela 'avaliacoes' ainda não foi criada.")
    print("Execute o app.py primeiro para criar o banco de dados.")
else:
    # Conta total de registros
    cursor.execute("SELECT COUNT(*) FROM avaliacoes")
    total = cursor.fetchone()[0]
    
    print(f"\n{'='*60}")
    print(f"📊 TOTAL DE AVALIAÇÕES: {total}")
    print(f"{'='*60}\n")
    
    if total > 0:
        # Mostra estatísticas
        cursor.execute("""
            SELECT grau_satisfacao, COUNT(*) as count 
            FROM avaliacoes 
            GROUP BY grau_satisfacao
        """)
        
        print("📈 DISTRIBUIÇÃO:")
        for row in cursor.fetchall():
            emoji = "😊" if row[0] == "muito_satisfeito" else "😐" if row[0] == "satisfeito" else "😞"
            print(f"   {emoji} {row[0]}: {row[1]} ({(row[1]/total*100):.1f}%)")
        
        # Mostra últimos 10 registros
        cursor.execute("""
            SELECT id, grau_satisfacao, data, hora, dia_semana 
            FROM avaliacoes 
            ORDER BY id DESC 
            LIMIT 10
        """)
        
        print(f"\n{'='*60}")
        print("🕒 ÚLTIMAS 10 AVALIAÇÕES:")
        print(f"{'='*60}")
        print(f"{'ID':<5} {'Satisfação':<20} {'Data':<12} {'Hora':<10} {'Dia':<10}")
        print("-" * 60)
        
        for row in cursor.fetchall():
            emoji = "😊" if row[1] == "muito_satisfeito" else "😐" if row[1] == "satisfeito" else "😞"
            satisfacao_texto = row[1].replace('_', ' ').title()
            print(f"{row[0]:<5} {emoji} {satisfacao_texto:<18} {row[2]:<12} {row[3]:<10} {row[4]:<10}")
    else:
        print("⚠️  Nenhuma avaliação registrada ainda.")
        print("Acesse http://localhost:5000 e clique em um botão para testar!")

conn.close()

print(f"\n{'='*60}")
print("✅ Consulta concluída!")
print(f"{'='*60}\n")
