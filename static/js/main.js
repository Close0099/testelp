// Controle de timeout para evitar múltiplos cliques
let isBlocked = false;
const TIMEOUT_DURATION = 3000; // 3 segundos

// Seleciona todos os botões de satisfação
const buttons = document.querySelectorAll('.btn-satisfaction');
const feedbackMessage = document.getElementById('feedback-message');

// Adiciona evento de clique para cada botão
buttons.forEach(button => {
    button.addEventListener('click', async () => {
        // Verifica se está bloqueado
        if (isBlocked) {
            return;
        }
        
        const satisfaction = button.getAttribute('data-satisfaction');
        
        // Bloqueia novos cliques
        blockButtons();
        
        // Envia voto para o backend
        try {
            const response = await fetch('/api/vote', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ satisfacao: satisfaction })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                // Mostra mensagem de agradecimento
                showFeedback('✨ Obrigado pelo seu feedback! ✨', 'success');
            } else {
                showFeedback('❌ Erro ao registrar. Tente novamente.', 'error');
                unblockButtons(); // Desbloqueia em caso de erro
            }
        } catch (error) {
            console.error('Erro:', error);
            showFeedback('❌ Erro de conexão. Tente novamente.', 'error');
            unblockButtons(); // Desbloqueia em caso de erro
        }
    });
});

// Função para bloquear botões
function blockButtons() {
    isBlocked = true;
    buttons.forEach(btn => {
        btn.disabled = true;
        btn.style.opacity = '0.6';
    });
}

// Função para desbloquear botões
function unblockButtons() {
    isBlocked = false;
    buttons.forEach(btn => {
        btn.disabled = false;
        btn.style.opacity = '1';
    });
}

// Função para mostrar feedback visual
function showFeedback(message, type = 'success') {
    feedbackMessage.textContent = message;
    feedbackMessage.classList.add('show');
    
    // Define cor de acordo com o tipo
    if (type === 'success') {
        feedbackMessage.style.background = 'linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%)';
    } else {
        feedbackMessage.style.background = 'linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%)';
    }
    
    // Remove mensagem após 2 segundos
    setTimeout(() => {
        feedbackMessage.classList.remove('show');
    }, 2000);
    
    // Desbloqueia botões após o timeout apenas se for sucesso
    if (type === 'success') {
        setTimeout(() => {
            unblockButtons();
        }, TIMEOUT_DURATION);
    }
}

// Suporte para teclado (acessibilidade)
document.addEventListener('keydown', (e) => {
    if (isBlocked) return;
    
    // Tecla 1: Muito Satisfeito
    if (e.key === '1') {
        buttons[0].click();
    }
    // Tecla 2: Satisfeito
    else if (e.key === '2') {
        buttons[1].click();
    }
    // Tecla 3: Insatisfeito
    else if (e.key === '3') {
        buttons[2].click();
    }
});
