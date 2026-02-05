from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime
import os
from io import StringIO, BytesIO
import csv
from functools import wraps
import psycopg2
from contextlib import contextmanager

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

app = Flask(__name__)
CORS(app)

app.secret_key = os.environ.get('SECRET_KEY', 'sua-chave-secreta-mude-em-producao')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '1234')

# Replit PostgreSQL
DATABASE_URL = os.environ.get('DATABASE_URL')

@contextmanager
def get_db():
    if not DATABASE_URL:
        raise RuntimeError('DATABASE_URL não configurado')
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    if not DATABASE_URL:
        return
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS avaliacoes (
                    id SERIAL PRIMARY KEY,
                    grau_satisfacao TEXT NOT NULL,
                    data TEXT NOT NULL,
                    hora TEXT NOT NULL,
                    dia_semana TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()

init_db()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_authenticated' not in session:
            return redirect(url_for('login_admin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['admin_authenticated'] = True
            return redirect(url_for('admin'))
        else:
            return render_template('login.html', error='Código de acesso incorreto!')
    if 'admin_authenticated' in session:
        return redirect(url_for('admin'))
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.pop('admin_authenticated', None)
    return redirect(url_for('index'))

@app.route('/api/vote', methods=['POST'])
def vote():
    try:
        if not DATABASE_URL:
            return jsonify({'error': 'Banco de dados não disponível'}), 500
        
        data = request.get_json()
        satisfacao = data.get('satisfacao')
        
        if satisfacao not in ['muito_satisfeito', 'satisfeito', 'insatisfeito']:
            return jsonify({'error': 'Opção inválida'}), 400
        
        agora = datetime.now()
        data_str = agora.strftime('%Y-%m-%d')
        hora_str = agora.strftime('%H:%M:%S')
        
        dias_semana = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        dia_semana = dias_semana[agora.weekday()]
        
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO avaliacoes (grau_satisfacao, data, hora, dia_semana) VALUES (%s, %s, %s, %s)',
                    (satisfacao, data_str, hora_str, dia_semana)
                )
            conn.commit()
        
        return jsonify({'success': True, 'message': 'Obrigado pelo seu feedback!'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        if not DATABASE_URL:
            return jsonify({'error': 'Banco de dados não disponível'}), 500
        
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        pagina = int(request.args.get('pagina', 1))
        limite = 20
        
        with get_db() as conn:
            with conn.cursor() as cur:
                if data_inicio and data_fim:
                    cur.execute(
                        'SELECT grau_satisfacao, data, hora, dia_semana FROM avaliacoes WHERE data BETWEEN %s AND %s',
                        (data_inicio, data_fim)
                    )
                else:
                    cur.execute('SELECT grau_satisfacao, data, hora, dia_semana FROM avaliacoes')
                docs = cur.fetchall()

        docs = [
            {
                'grau_satisfacao': row[0],
                'data': row[1],
                'hora': row[2],
                'dia_semana': row[3]
            }
            for row in docs
        ]
        total = len(docs)
        
        satisfacao_counts = {}
        dia_counts = {}
        avaliacoes_diarias = {}
        
        for doc in docs:
            grau = doc.get('grau_satisfacao')
            satisfacao_counts[grau] = satisfacao_counts.get(grau, 0) + 1
            
            dia = doc.get('dia_semana')
            dia_counts[dia] = dia_counts.get(dia, 0) + 1
            
            data = doc.get('data')
            avaliacoes_diarias[data] = avaliacoes_diarias.get(data, 0) + 1
        
        ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        dia_counts_ordenado = {dia: dia_counts.get(dia, 0) for dia in ordem_dias}
        
        offset = (pagina - 1) * limite
        ultimas = docs[-offset-limite:-offset if offset else None]
        if ultimas:
            ultimas.reverse()
        else:
            ultimas = []
        
        # sem ids na resposta
        
        total_paginas = (total + limite - 1) // limite
        
        return jsonify({
            'total': total,
            'satisfacao': satisfacao_counts,
            'dia_semana': dia_counts_ordenado,
            'avaliacoes_diarias': [{'data': k, 'count': v} for k, v in sorted(avaliacoes_diarias.items())],
            'ultimas_avaliacoes': ultimas,
            'paginacao': {
                'pagina_atual': pagina,
                'total_paginas': total_paginas,
                'total_registos': total,
                'registos_por_pagina': limite
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats/comparacao', methods=['GET'])
def stats_comparacao():
    try:
        if not DATABASE_URL:
            return jsonify({'error': 'Banco de dados não disponível'}), 500
        
        dia1 = request.args.get('dia1')
        dia2 = request.args.get('dia2')
        
        if not dia1 or not dia2:
            return jsonify({'error': 'Parâmetros dia1 e dia2 obrigatórios'}), 400
        
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT grau_satisfacao FROM avaliacoes WHERE data = %s', (dia1,))
                docs1 = cur.fetchall()
        stats_dia1 = {}
        for doc in docs1:
            grau = doc[0]
            stats_dia1[grau] = stats_dia1.get(grau, 0) + 1
        
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT grau_satisfacao FROM avaliacoes WHERE data = %s', (dia2,))
                docs2 = cur.fetchall()
        stats_dia2 = {}
        for doc in docs2:
            grau = doc[0]
            stats_dia2[grau] = stats_dia2.get(grau, 0) + 1
        
        return jsonify({
            'dia1': {
                'data': dia1,
                'total': len(docs1),
                'distribuicao': stats_dia1
            },
            'dia2': {
                'data': dia2,
                'total': len(docs2),
                'distribuicao': stats_dia2
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    try:
        if not DATABASE_URL:
            return jsonify({'error': 'Banco de dados não disponível'}), 500
        
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT grau_satisfacao, data, hora, dia_semana FROM avaliacoes ORDER BY timestamp ASC')
                rows = cur.fetchall()
        
        if not rows:
            return jsonify({'error': 'Sem dados para exportar'}), 400
        
        if HAS_OPENPYXL:
            wb = Workbook()
            ws = wb.active
            ws.title = "Avaliações"
            
            header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF", size=12)
            border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            headers = ['Grau de Satisfação', 'Data', 'Hora', 'Dia da Semana']
            for col, header in enumerate(headers, start=1):
                cell = ws.cell(row=1, column=col)
                cell.value = header
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
                cell.border = border
            
            emoji_map = {
                'muito_satisfeito': '😊 Muito Satisfeito',
                'satisfeito': '😐 Satisfeito',
                'insatisfeito': '😞 Insatisfeito'
            }
            
            for row_idx, row in enumerate(rows, start=2):
                satisfacao_display = emoji_map.get(row.get('grau_satisfacao'), row.get('grau_satisfacao'))
                data = [satisfacao_display, row.get('data'), row.get('hora'), row.get('dia_semana')]
                for col, value in enumerate(data, start=1):
                    cell = ws.cell(row=row_idx, column=col)
                    cell.value = value
                    cell.border = border
                    if col in [2, 3]:
                        cell.alignment = Alignment(horizontal='center')
            
            ws.column_dimensions['A'].width = 25
            ws.column_dimensions['B'].width = 15
            ws.column_dimensions['C'].width = 12
            ws.column_dimensions['D'].width = 18
            
            mem_file = BytesIO()
            wb.save(mem_file)
            mem_file.seek(0)
            
            return send_file(
                mem_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'avaliacoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            )
        
        else:
            output = StringIO()
            writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_ALL)
            writer.writerow(['Grau de Satisfação', 'Data', 'Hora', 'Dia da Semana'])
            for row in rows:
                writer.writerow([row[0], row[1], row[2], row[3]])
            
            output.seek(0)
            mem_file = BytesIO()
            mem_file.write(output.getvalue().encode('utf-8'))
            mem_file.seek(0)
            
            return send_file(
                mem_file,
                mimetype='text/csv',
                as_attachment=True,
                download_name=f'avaliacoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/txt', methods=['POST'])
def export_txt():
    try:
        if not DATABASE_URL:
            return jsonify({'error': 'Banco de dados não disponível'}), 500
        
        data = request.get_json() if request.is_json else {}
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        
        with get_db() as conn:
            with conn.cursor() as cur:
                if data_inicio and data_fim:
                    cur.execute(
                        'SELECT grau_satisfacao, data, hora, dia_semana FROM avaliacoes WHERE data BETWEEN %s AND %s ORDER BY timestamp ASC',
                        (data_inicio, data_fim)
                    )
                else:
                    cur.execute('SELECT grau_satisfacao, data, hora, dia_semana FROM avaliacoes ORDER BY timestamp ASC')
                rows = cur.fetchall()
        
        output = StringIO()
        
        output.write('=' * 100 + '\n')
        output.write('RELATÓRIO DE AVALIAÇÕES DE SATISFAÇÃO\n')
        output.write('=' * 100 + '\n\n')
        
        if data_inicio and data_fim:
            output.write(f'Período: {data_inicio} até {data_fim}\n')
        else:
            output.write(f'Data de Geração: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')
        
        output.write(f'Total de Registros: {len(rows)}\n')
        output.write('=' * 100 + '\n\n')
        
        output.write(f"{'Satisfação':<25} | {'Data':<12} | {'Hora':<10} | {'Dia da Semana':<15}\n")
        output.write('-' * 100 + '\n')
        
        for row in rows:
            grau = row[0]
            emoji = '😊' if grau == 'muito_satisfeito' else '😐' if grau == 'satisfeito' else '😞'
            satisfacao_texto = f"{emoji} {grau.replace('_', ' ').title()}"
            
            output.write(f"{satisfacao_texto:<25} | {row[1]:<12} | {row[2]:<10} | {row[3]:<15}\n")
        
        output.write('\n' + '=' * 100 + '\n')
        output.write('Fim do Relatório\n')
        output.write('=' * 100 + '\n')
        
        output.seek(0)
        mem_file = BytesIO()
        mem_file.write(output.getvalue().encode('utf-8'))
        mem_file.seek(0)
        
        return send_file(
            mem_file,
            mimetype='text/plain',
            as_attachment=True,
            download_name=f'avaliacoes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt'
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
