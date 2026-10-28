// Modal para aceitar um pedido ou reagendar: o tatuador escolhe dia, hora e duração.
let sessoesConfirmadas = [];

function hojeISO() {
    const d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 10);
}

function mostrarOcupados() {
    const dia = document.getElementById('dia').value;
    const caixa = document.getElementById('diaOcupado');
    const lista = document.getElementById('listaOcupado');
    const doDia = sessoesConfirmadas.filter(function (s) { return s.dia === dia; });

    lista.innerHTML = '';
    doDia.forEach(function (s) {
        const li = document.createElement('li');
        li.textContent = s.inicio + ' às ' + s.fim + ' — ' + s.cliente;
        lista.appendChild(li);
    });
    caixa.hidden = doDia.length === 0;
}

function abrirModal(botao) {
    const form = document.getElementById('formHorario');
    const modal = document.getElementById('modalHorario');
    if (!form || !modal) return;

    // /tatuador/agenda  ->  /tatuador/agenda/<id>/definir-horario
    form.action = form.dataset.urlBase + '/' + botao.dataset.id + '/definir-horario';
    document.getElementById('modalTitulo').textContent =
        (botao.dataset.modo === 'aceitar' ? 'Aceitar pedido — ' : 'Reagendar — ') + botao.dataset.cliente;

    const dia = document.getElementById('dia');
    dia.min = hojeISO();
    dia.value = botao.dataset.dia;
    document.getElementById('hora').value = botao.dataset.hora;
    document.getElementById('duracao_min').value = botao.dataset.duracao;

    mostrarOcupados();
    modal.style.display = 'flex';
}

function fecharModal() {
    const modal = document.getElementById('modalHorario');
    if (modal) modal.style.display = 'none';
}

document.addEventListener('DOMContentLoaded', function () {
    const dados = document.getElementById('dadosConfirmadas');
    try {
        sessoesConfirmadas = dados ? JSON.parse(dados.textContent) : [];
    } catch (e) {
        sessoesConfirmadas = [];
    }

    document.querySelectorAll('.btn-horario').forEach(function (botao) {
        botao.addEventListener('click', function () { abrirModal(this); });
    });

    document.getElementById('dia').addEventListener('change', mostrarOcupados);

    const botaoFechar = document.getElementById('btnFecharModal');
    if (botaoFechar) botaoFechar.addEventListener('click', fecharModal);
});
