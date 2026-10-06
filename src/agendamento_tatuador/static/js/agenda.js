// Função para abrir o modal de reagendamento
function abrirModal(idAgendamento) {
    const form = document.getElementById('formReagendar');
    if (form) {
        form.action = '/reagendar/' + idAgendamento;
        const modal = document.getElementById('modalReagendar');
        if (modal) {
            modal.style.display = 'flex';
        }
    }
}

// Função para fechar o modal
function fecharModal() {
    const modal = document.getElementById('modalReagendar');
    if (modal) {
        modal.style.display = 'none';
    }
}

// Escuta os cliques na página de forma limpa
document.addEventListener('DOMContentLoaded', function () {
    // Botões para abrir o modal
    const botoesReagendar = document.querySelectorAll('.btn-reagendar');
    botoesReagendar.forEach(function (botao) {
        botao.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            abrirModal(id);
        });
    });

    // Botão para fechar o modal
    const botaoFechar = document.getElementById('btnFecharModal');
    if (botaoFechar) {
        botaoFechar.addEventListener('click', fecharModal);
    }
});