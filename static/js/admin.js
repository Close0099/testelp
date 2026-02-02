// Variáveis globais para os gráficos e paginação
let satisfacaoChart, diaSemanaChart, evolucaoDiariaChart;
let paginacaoAtual = 1;
let filtroDataInicio = null;
let filtroDataFim = null;

// Mapeamento de labels
const satisfacaoLabels = {
    'muito_satisfeito': 'Muito Satisfeito',
    'satisfeito': 'Satisfeito',
    'insatisfeito': 'Insatisfeito'
};

const satisfacaoEmojis = {
    'muito_satisfeito': '😊',
    'satisfeito': '😐',
    'insatisfeito': '😞'
};

// Carrega estatísticas ao carregar a página
document.addEventListener('DOMContentLoaded', () => {
    // Mostra a data atual
    atualizarDataAtual();
    
    // Carrega os dados do dia atual por padrão
    const hoje = new Date().toISOString().split('T')[0];
    document.getElementById('dataInicio').value = hoje;
    document.getElementById('dataFim').value = hoje;
    
    filtroDataInicio = hoje;
    filtroDataFim = hoje;
    
    loadStats();
    
    // Atualiza a cada 30 segundos
    setInterval(loadStats, 30000);
    
    // Verifica se mudou de dia e recarrega
    setInterval(() => {
        const novoHoje = new Date().toISOString().split('T')[0];
        if (novoHoje !== hoje) {
            window.location.reload();
        }
    }, 60000); // Verifica a cada minuto
});

// Função para atualizar a data exibida
function atualizarDataAtual() {
    const hoje = new Date();
    const diasSemana = ['Domingo', 'Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado'];
    const diaSemanaNome = diasSemana[hoje.getDay()];
    const dataFormatada = hoje.toLocaleDateString('pt-BR');
    
    document.getElementById('dataAtualTexto').textContent = 
        `${diaSemanaNome}, ${dataFormatada}`;
}

// Função principal para carregar estatísticas
async function loadStats() {
    try {
        let url = '/api/stats?pagina=' + paginacaoAtual;
        
        if (filtroDataInicio && filtroDataFim) {
            url += '&data_inicio=' + filtroDataInicio + '&data_fim=' + filtroDataFim;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (response.ok) {
            updateOverviewStats(data);
            updateCharts(data);
            updateTable(data.ultimas_avaliacoes);
            updatePaginacao(data.paginacao);
        } else {
            console.error('Erro ao carregar estatísticas:', data.error);
        }
    } catch (error) {
        console.error('Erro de conexão:', error);
    }
}

// Atualiza os cards de overview
function updateOverviewStats(data) {
    const total = data.total;
    
    document.getElementById('total-avaliacoes').textContent = total;
    
    const muitoSatisfeito = data.satisfacao.muito_satisfeito || 0;
    const satisfeito = data.satisfacao.satisfeito || 0;
    const insatisfeito = data.satisfacao.insatisfeito || 0;
    
    document.getElementById('muito-satisfeito').textContent = muitoSatisfeito;
    document.getElementById('satisfeito').textContent = satisfeito;
    document.getElementById('insatisfeito').textContent = insatisfeito;
    
    // Calcula percentuais
    if (total > 0) {
        document.getElementById('muito-satisfeito-percent').textContent = 
            `${((muitoSatisfeito / total) * 100).toFixed(1)}%`;
        document.getElementById('satisfeito-percent').textContent = 
            `${((satisfeito / total) * 100).toFixed(1)}%`;
        document.getElementById('insatisfeito-percent').textContent = 
            `${((insatisfeito / total) * 100).toFixed(1)}%`;
    }
}

// Atualiza todos os gráficos
function updateCharts(data) {
    updateSatisfacaoChart(data.satisfacao);
    updateDiaSemanaChart(data.dia_semana);
    updateEvolucaoDiariaChart(data.avaliacoes_diarias);
}

// Gráfico de pizza - Distribuição de Satisfação
function updateSatisfacaoChart(satisfacaoData) {
    const ctx = document.getElementById('satisfacaoChart').getContext('2d');
    
    const labels = Object.keys(satisfacaoData).map(key => satisfacaoLabels[key]);
    const valores = Object.values(satisfacaoData);
    
    if (satisfacaoChart) {
        satisfacaoChart.destroy();
    }
    
    satisfacaoChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: valores,
                backgroundColor: [
                    'rgba(72, 187, 120, 0.8)',
                    'rgba(237, 137, 54, 0.8)',
                    'rgba(245, 101, 101, 0.8)'
                ],
                borderColor: [
                    'rgba(72, 187, 120, 1)',
                    'rgba(237, 137, 54, 1)',
                    'rgba(245, 101, 101, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const percentage = ((value / total) * 100).toFixed(1);
                            return `${label}: ${value} (${percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Gráfico de barras - Avaliações por Dia da Semana
function updateDiaSemanaChart(diaSemanaData) {
    const ctx = document.getElementById('diaSemanaChart').getContext('2d');
    
    const diasOrdenados = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'];
    const valores = diasOrdenados.map(dia => diaSemanaData[dia] || 0);
    
    if (diaSemanaChart) {
        diaSemanaChart.destroy();
    }
    
    diaSemanaChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: diasOrdenados,
            datasets: [{
                label: 'Avaliações',
                data: valores,
                backgroundColor: 'rgba(102, 126, 234, 0.8)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 2,
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Gráfico de linha - Evolução Diária
function updateEvolucaoDiariaChart(avaliacoesDiarias) {
    const ctx = document.getElementById('evolucaoDiariaChart').getContext('2d');
    
    const labels = avaliacoesDiarias.map(item => {
        const date = new Date(item.data);
        return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    });
    const valores = avaliacoesDiarias.map(item => item.count);
    
    if (evolucaoDiariaChart) {
        evolucaoDiariaChart.destroy();
    }
    
    evolucaoDiariaChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Avaliações por Dia',
                data: valores,
                fill: true,
                backgroundColor: 'rgba(102, 126, 234, 0.2)',
                borderColor: 'rgba(102, 126, 234, 1)',
                borderWidth: 3,
                tension: 0.4,
                pointRadius: 4,
                pointHoverRadius: 6,
                pointBackgroundColor: 'rgba(102, 126, 234, 1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Atualiza a tabela de avaliações
function updateTable(avaliacoes) {
    const tbody = document.getElementById('avaliacoes-tbody');
    
    if (avaliacoes.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Nenhuma avaliação registrada ainda.</td></tr>';
        return;
    }
    
    tbody.innerHTML = avaliacoes.map(avaliacao => {
        const badgeClass = 
            avaliacao.grau_satisfacao === 'muito_satisfeito' ? 'badge-success' :
            avaliacao.grau_satisfacao === 'satisfeito' ? 'badge-warning' :
            'badge-danger';
        
        const emoji = satisfacaoEmojis[avaliacao.grau_satisfacao];
        const label = satisfacaoLabels[avaliacao.grau_satisfacao];
        
        const data = new Date(avaliacao.data).toLocaleDateString('pt-BR');
        
        return `
            <tr>
                <td>#${avaliacao.id}</td>
                <td><span class="badge ${badgeClass}">${emoji} ${label}</span></td>
                <td>${data}</td>
                <td>${avaliacao.hora}</td>
                <td>${avaliacao.dia_semana}</td>
            </tr>
        `;
    }).join('');
}

// Funções de Exportação
function exportExcel() {
    window.location.href = '/api/export/excel';
}

function openExportTxt() {
    const modal = document.getElementById('exportModal');
    modal.classList.add('show');
}

function closeExportTxt() {
    const modal = document.getElementById('exportModal');
    modal.classList.remove('show');
}

function exportTxt() {
    const dataInicio = document.getElementById('dataInicio').value;
    const dataFim = document.getElementById('dataFim').value;
    
    const payload = {};
    if (dataInicio) payload.data_inicio = dataInicio;
    if (dataFim) payload.data_fim = dataFim;
    
    fetch('/api/export/txt', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `avaliacoes_${new Date().toISOString().split('T')[0]}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
        closeExportTxt();
    })
    .catch(error => {
        console.error('Erro ao exportar:', error);
        alert('Erro ao exportar o arquivo!');
    });
}

// Fechar modal ao clicar fora dele
window.onclick = function(event) {
    const modal = document.getElementById('exportModal');
    if (event.target == modal) {
        closeExportTxt();
    }
}

// Funções de Filtro
function aplicarFiltros() {
    const dataInicio = document.getElementById('dataInicio').value;
    const dataFim = document.getElementById('dataFim').value;
    
    if (!dataInicio || !dataFim) {
        alert('Por favor, selecione ambas as datas!');
        return;
    }
    
    if (new Date(dataInicio) > new Date(dataFim)) {
        alert('A data inicial não pode ser maior que a data final!');
        return;
    }
    
    filtroDataInicio = dataInicio;
    filtroDataFim = dataFim;
    paginacaoAtual = 1;
    loadStats();
}

function limparFiltros() {
    document.getElementById('dataInicio').value = '';
    document.getElementById('dataFim').value = '';
    document.getElementById('diaComparacao1').value = '';
    document.getElementById('diaComparacao2').value = '';
    document.getElementById('comparacaoResult').style.display = 'none';
    
    filtroDataInicio = null;
    filtroDataFim = null;
    paginacaoAtual = 1;
    loadStats();
}

// Funções rápidas de filtro
function mostrarHoje() {
    const hoje = new Date().toISOString().split('T')[0];
    document.getElementById('dataInicio').value = hoje;
    document.getElementById('dataFim').value = hoje;
    
    filtroDataInicio = hoje;
    filtroDataFim = hoje;
    paginacaoAtual = 1;
    loadStats();
}

function ultimos7Dias() {
    const hoje = new Date();
    const seteDiasAtras = new Date(hoje.getTime() - 7 * 24 * 60 * 60 * 1000);
    
    const dataInicio = seteDiasAtras.toISOString().split('T')[0];
    const dataFim = hoje.toISOString().split('T')[0];
    
    document.getElementById('dataInicio').value = dataInicio;
    document.getElementById('dataFim').value = dataFim;
    
    filtroDataInicio = dataInicio;
    filtroDataFim = dataFim;
    paginacaoAtual = 1;
    loadStats();
}

// Função de Comparação entre Dias
async function compararDias() {
    const dia1 = document.getElementById('diaComparacao1').value;
    const dia2 = document.getElementById('diaComparacao2').value;
    
    if (!dia1 || !dia2) {
        alert('Por favor, selecione ambos os dias para comparar!');
        return;
    }
    
    if (dia1 === dia2) {
        alert('Por favor, selecione dias diferentes!');
        return;
    }
    
    try {
        const response = await fetch(`/api/stats/comparacao?dia1=${dia1}&dia2=${dia2}`);
        const data = await response.json();
        
        if (response.ok) {
            exibirComparacao(data);
        } else {
            alert('Erro ao carregar comparação: ' + data.error);
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao comparar dias!');
    }
}

function exibirComparacao(data) {
    const resultDiv = document.getElementById('comparacaoResult');
    resultDiv.style.display = 'block';
    
    // Dia 1
    document.getElementById('comparacao-dia1-label').textContent = 'Dia 1: ' + data.dia1.data;
    document.getElementById('comparacao-dia1-total').textContent = data.dia1.total;
    document.getElementById('comparacao-dia1-ms').textContent = 
        data.dia1.distribuicao.muito_satisfeito || 0;
    document.getElementById('comparacao-dia1-s').textContent = 
        data.dia1.distribuicao.satisfeito || 0;
    document.getElementById('comparacao-dia1-i').textContent = 
        data.dia1.distribuicao.insatisfeito || 0;
    
    // Dia 2
    document.getElementById('comparacao-dia2-label').textContent = 'Dia 2: ' + data.dia2.data;
    document.getElementById('comparacao-dia2-total').textContent = data.dia2.total;
    document.getElementById('comparacao-dia2-ms').textContent = 
        data.dia2.distribuicao.muito_satisfeito || 0;
    document.getElementById('comparacao-dia2-s').textContent = 
        data.dia2.distribuicao.satisfeito || 0;
    document.getElementById('comparacao-dia2-i').textContent = 
        data.dia2.distribuicao.insatisfeito || 0;
    
    // Scroll até o resultado
    resultDiv.scrollIntoView({ behavior: 'smooth' });
}

// Funções de Paginação
function updatePaginacao(paginacao) {
    document.getElementById('pagina-atual').textContent = paginacao.pagina_atual;
    document.getElementById('total-paginas').textContent = paginacao.total_paginas;
    document.getElementById('total-registos').textContent = paginacao.total_registos;
    
    if (paginacao.total_paginas > 1) {
        document.getElementById('paginacao').style.display = 'flex';
    }
    
    // Desabilitar botões de paginação conforme necessário
    document.querySelectorAll('.btn-paginacao').forEach(btn => {
        btn.disabled = false;
    });
    
    if (paginacao.pagina_atual === 1) {
        document.querySelectorAll('.btn-paginacao')[0].disabled = true;
    }
    if (paginacao.pagina_atual === paginacao.total_paginas) {
        document.querySelectorAll('.btn-paginacao')[1].disabled = true;
    }
}

function paginacaoAnterior() {
    if (paginacaoAtual > 1) {
        paginacaoAtual--;
        loadStats();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

function paginacaoProxima() {
    const totalPaginas = parseInt(document.getElementById('total-paginas').textContent);
    if (paginacaoAtual < totalPaginas) {
        paginacaoAtual++;
        loadStats();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
}

