from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from flask_cors import CORS
from datetime import datetime
import os
from io import StringIO, BytesIO
import csv
from functools import wraps

import firebase_admin
from firebase_admin import credentials, firestore

try:
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

app = Flask(__name__)
CORS(app)

# Configuração de sessão
app.secret_key = os.environ.get('SECRET_KEY', 'sua-chave-secreta-mude-em-producao')

# Código de acesso ao admin
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', '1234')

# Inicializar Firebase
try:
    cred = credentials.Certificate('testelp-798d4-firebase-adminsdk-fbsvc-72781ceda7.json')
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    FIRESTORE_ENABLED = True
except Exception as e:
    print(f"Erro ao inicializar Firebase: {e}")
    FIRESTORE_ENABLED = False
    db = None

# Decorator para proteger rotas admin
def login_required(f):
    """Verifica se o utilizador está autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_authenticated' not in session:
            return redirect(url_for('login_admin'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    """Página principal de votação"""
    return render_template('index.html')

@app.route('/login-admin', methods=['GET', 'POST'])
def login_admin():
    """Página de login para o admin"""
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
    """Página administrativa"""
    return render_template('admin.html')

@app.route('/logout')
def logout():
    """Faz logout do admin"""
    session.pop('admin_authenticated', None)
    return redirect(url_for('index'))

@app.route('/api/vote', methods=['POST'])
def vote():
    """Registra um voto"""
    try:
        if not FIRESTORE_ENABLED:
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
        
        db.collection('avaliacoes').add({
            'grau_satisfacao': satisfacao,
            'data': data_str,
            'hora': hora_str,
            'dia_semana': dia_semana,
            'timestamp': agora
        })
        
        return jsonify({
            'success': True,
            'message': 'Obrigado pelo seu feedback!'
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas das avaliações"""
    try:
        if not FIRESTORE_ENABLED:
            return jsonify({'error': 'Banco de dados não disponível'}), 500
        
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        pagina = int(request.args.get('pagina', 1))
        limite = 20
        
        query = db.collection('avaliacoes')
        
        if data_inicio and data_fim:
            query = query.where('data', '>=', data_inicio)
            query = query.where('data', '<=', data_fim)
        
        docs = query.stream()
        avaliacoes = []
        for doc in docs:
            avaliacoes.append(doc.to_dict())
        
        total = len(avaliacoes)
        
        satisfacao_counts = {}
        dia_counts = {}
        avaliacoes_diarias = {}
        
        for av in avaliacoes:
            grau = av.get('grau_satisfacao')
            satisfacao_counts[grau] = satisfacao_counts.get(grau, 0) + 1
            
            dia = av.get('dia_semana')
            dia_counts[dia] = dia_counts.get(dia, 0) + 1
            
            data = av.get('data')
            avaliacoes_diarias[data] = avaliacoes_diarias.get(data, 0) + 1
        
        ordem_dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
        dia_counts_ordenado = {dia: dia_counts.get(dia, 0) for dia in ordem_dias}
        
        offset = (pagina - 1) * limite
        ultimas = avaliacoes[-offset-limite:-offset if offset else None]
        if ultimas:
            ultimas.reverse()
        else:
            ultimas = []
        
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
    """Compara estatísticas entre dois dias"""
    try:
        if not FIRESTORE_ENABLED:
            return jsonify({'error': 'Banco de dados não disponível'}), 500
        
        dia1 = request.args.get('dia1')
        dia2 = request.args.get('dia2')
        
        if not dia1 or not dia2:
            return jsonify({'error': 'Parâmetros dia1 e dia2 obrigatórios'}), 400
        
        docs1 = db.collection('avaliacoes').where('data', '==', dia1).stream()
        stats_dia1 = {}
        total_dia1 = 0
        for doc in docs1:
            total_dia1 += 1
            grau = doc.to_dict().get('grau_satisfacao')
            stats_dia1[grau] = stats_dia1.get(grau, 0) + 1
        
        docs2 = db.collection('avaliacoes').where('data', '==', dia2).stream()
        stats_dia2 = {}
        total_dia2 = 0
        for doc in docs2:
            total_dia2 += 1
            grau = doc.to_dict().get('grau_satisfacao')
            stats_dia2[grau] = stats_dia2.get(grau, 0) + 1
        
        return jsonify({
            'dia1': {
                'data': dia1,
                'total': total_dia1,
                'distribuicao': stats_dia1
            },
            'dia2': {
                'data': dia2,
                'total': total_dia2,
                'distribuicao': stats_dia2
            }
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/export/excel', methods=['GET'])
def export_excel():
    """Exporta dados para Excel (.xlsx)"""
    try:
        if not FIRESTORE_ENABLED:
            return jsonify({'error': 'Banco de dados não disponível'}), 500
        
        docs = db.collection('avaliacoes').order_by('timestamp').stream()
        rows = [doc.to_dict() for doc in docs]
        
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
                writer.writerow([row.get('grau_satisfacao'), row.get('data'), row.get('hora'), row.get('dia_semana')])
            
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
    """Exporta dados para TXT com filtro opcional por data"""
    try:
        if not FIRESTORE_ENABLED:
            return jsonify({'error': 'Banco de dados não disponível'}), 500
        
        data = request.get_json() if request.is_json else {}
        data_inicio = data.get('data_inicio')
        data_fim = data.get('data_fim')
        
        query = db.collection('avaliacoes')
        if data_inicio and data_fim:
            query = query.where('data', '>=', data_inicio)
            query = query.where('data', '<=', data_fim)
        
        docs = query.order_by('timestamp').stream()
        rows = [doc.to_dict() for doc in docs]
        
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
            grau = row.get('grau_satisfacao')
            emoji = '😊' if grau == 'muito_satisfeito' else '😐' if grau == 'satisfeito' else '😞'
            satisfacao_texto = f"{emoji} {grau.replace('_', ' ').title()}"
            
            output.write(f"{satisfacao_texto:<25} | {row.get('data'):<12} | {row.get('hora'):<10} | {row.get('dia_semana'):<15}\n")
        
        output.write('\n' + '=' * 100 + '\n')
        output.write(f'Fim do Relatório\n')
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
    """Endpoint de health check"""
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
