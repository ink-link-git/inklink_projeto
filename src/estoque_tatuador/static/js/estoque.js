// Clicar no insumo seleciona/remove; o campo de quantidade só é enviado quando selecionado.
document.querySelectorAll(".chip").forEach((chip) => {
    const botao = chip.querySelector(".chip-btn");
    const passo = chip.querySelector(".chip-step");
    const qtd = chip.querySelector(".chip-qtd");
    const max = +chip.dataset.max;

    botao.addEventListener("click", () => {
        const ligado = chip.classList.toggle("on");
        passo.hidden = !ligado;
        qtd.name = ligado ? "qtd_" + chip.dataset.id : "";
        if (!ligado) qtd.value = 1;
        botao.textContent = (ligado ? "✓ " : "+ ") + botao.textContent.slice(2);
    });

    // Botões − e + no lugar das setinhas nativas do navegador.
    passo.querySelectorAll(".step-btn").forEach((b) => b.addEventListener("click", () => {
        qtd.value = Math.min(max, Math.max(1, (+qtd.value || 1) + +b.dataset.passo));
    }));
    qtd.addEventListener("change", () => {
        qtd.value = Math.min(max, Math.max(1, +qtd.value || 1));
    });
});

// Data em dd/mm/aaaa (o campo nativo segue o idioma do navegador); o servidor recebe aaaa-mm-dd.
const dataBr = document.getElementById("data_br");
function brParaIso(br) {
    const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(br);
    if (!m) return "";
    const d = new Date(+m[3], +m[2] - 1, +m[1]);
    const real = d.getFullYear() === +m[3] && d.getMonth() === +m[2] - 1 && d.getDate() === +m[1];
    return real ? m[3] + "-" + m[2] + "-" + m[1] : "";
}
dataBr.addEventListener("input", () => {
    const n = dataBr.value.replace(/\D/g, "").slice(0, 8);
    dataBr.value = n.length > 4 ? n.slice(0, 2) + "/" + n.slice(2, 4) + "/" + n.slice(4)
                 : n.length > 2 ? n.slice(0, 2) + "/" + n.slice(2) : n;
    dataBr.setCustomValidity("");
});

document.querySelector(".estoque-form").addEventListener("submit", (e) => {
    const iso = brParaIso(dataBr.value);
    dataBr.setCustomValidity(iso ? "" : "Digite uma data válida no formato dd/mm/aaaa.");
    if (!e.target.reportValidity()) { e.preventDefault(); return; }
    if (!document.querySelector(".chip.on")) {
        e.preventDefault();
        alert("Selecione ao menos um insumo.");
        return;
    }
    document.getElementById("data_sessao").value = iso;
});

// "Outro cliente" mostra o campo de texto.
const selectCliente = document.getElementById("cliente");
const campoOutro = document.getElementById("cliente_outro");
selectCliente.addEventListener("change", () => {
    const outro = selectCliente.value === "__outro__";
    campoOutro.hidden = !outro;
    campoOutro.required = outro;
    if (outro) campoOutro.focus();
});
