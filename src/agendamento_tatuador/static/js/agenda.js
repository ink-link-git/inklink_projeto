// Modal para aceitar um pedido ou reagendar: o tatuador escolhe dia, hora e duração.
let sessoesConfirmadas = [];

function hojeISO() {
    const d = new Date();
    d.setMinutes(d.getMinutes() - d.getTimezoneOffset());
    return d.toISOString().slice(0, 10);
}

// O navegador mostra <input type="date/time"> no formato do sistema (mm/dd/aaaa, AM/PM).
// Por isso o modal usa campos de texto com máscara (dd/mm/aaaa e 24h) e envia ao servidor
// os valores em ISO (aaaa-mm-dd e hh:mm) nos campos escondidos #dia e #hora.
function isoParaBr(iso) {
    const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(iso || '');
    return m ? m[3] + '/' + m[2] + '/' + m[1] : '';
}

function brParaIso(br) {
    const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(br);
    if (!m) return '';
    const d = new Date(+m[3], +m[2] - 1, +m[1]);
    const real = d.getFullYear() === +m[3] && d.getMonth() === +m[2] - 1 && d.getDate() === +m[1];
    return real ? m[3] + '-' + m[2] + '-' + m[1] : '';
}

function mascaraData(campo) {
    const n = campo.value.replace(/\D/g, '').slice(0, 8);
    campo.value = n.length > 4 ? n.slice(0, 2) + '/' + n.slice(2, 4) + '/' + n.slice(4)
                : n.length > 2 ? n.slice(0, 2) + '/' + n.slice(2) : n;
}

function mascaraHora(campo) {
    const n = campo.value.replace(/\D/g, '').slice(0, 4);
    campo.value = n.length > 2 ? n.slice(0, 2) + ':' + n.slice(2) : n;
}

function mostrarOcupados() {
    const dia = brParaIso(document.getElementById('dia_br').value);
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

    document.getElementById('dia_br').value = isoParaBr(botao.dataset.dia);
    document.getElementById('hora_br').value = botao.dataset.hora;
    document.getElementById('dia_br').setCustomValidity('');
    document.getElementById('hora_br').setCustomValidity('');
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

    const diaBr = document.getElementById('dia_br');
    const horaBr = document.getElementById('hora_br');
    diaBr.addEventListener('input', function () {
        mascaraData(diaBr);
        diaBr.setCustomValidity('');
        mostrarOcupados();
    });
    horaBr.addEventListener('input', function () {
        mascaraHora(horaBr);
        horaBr.setCustomValidity('');
    });

    // Valida o texto digitado e preenche os campos escondidos em formato ISO.
    document.getElementById('formHorario').addEventListener('submit', function (e) {
        const iso = brParaIso(diaBr.value);
        const hora = /^([01]\d|2[0-3]):[0-5]\d$/.test(horaBr.value) ? horaBr.value : '';
        diaBr.setCustomValidity(!iso ? 'Digite uma data válida no formato dd/mm/aaaa.'
            : iso < hojeISO() ? 'Escolha uma data a partir de hoje.' : '');
        horaBr.setCustomValidity(hora ? '' : 'Digite a hora no formato 24h, por exemplo 14:30.');
        if (!this.reportValidity()) { e.preventDefault(); return; }
        document.getElementById('dia').value = iso;
        document.getElementById('hora').value = hora;
    });

    const botaoFechar = document.getElementById('btnFecharModal');
    if (botaoFechar) botaoFechar.addEventListener('click', fecharModal);
});