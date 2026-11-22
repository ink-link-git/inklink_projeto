// Registrar compra: abre o painel, mostra os campos de "novo material" e envia a data em aaaa-mm-dd.
const form = document.getElementById("formCompra");
const abrir = document.getElementById("btnCompra");
const selectItem = document.getElementById("compra_item");
const novo = document.getElementById("novoMaterial");
const dataBr = document.getElementById("compra_data_br");

function hojeBr() {
    const d = new Date();
    return String(d.getDate()).padStart(2, "0") + "/" + String(d.getMonth() + 1).padStart(2, "0") + "/" + d.getFullYear();
}

function brParaIso(br) {
    const m = /^(\d{2})\/(\d{2})\/(\d{4})$/.exec(br);
    if (!m) return "";
    const d = new Date(+m[3], +m[2] - 1, +m[1]);
    const real = d.getFullYear() === +m[3] && d.getMonth() === +m[2] - 1 && d.getDate() === +m[1];
    return real ? m[3] + "-" + m[2] + "-" + m[1] : "";
}

abrir.addEventListener("click", () => {
    form.hidden = !form.hidden;
    if (!form.hidden && !dataBr.value) dataBr.value = hojeBr();
});
document.getElementById("btnCancelarCompra").addEventListener("click", () => { form.hidden = true; });

selectItem.addEventListener("change", () => {
    const ehNovo = selectItem.value === "__novo__";
    novo.hidden = !ehNovo;
    novo.querySelectorAll("input").forEach((i) => { i.required = ehNovo; });
});

dataBr.addEventListener("input", () => {
    const n = dataBr.value.replace(/\D/g, "").slice(0, 8);
    dataBr.value = n.length > 4 ? n.slice(0, 2) + "/" + n.slice(2, 4) + "/" + n.slice(4)
                 : n.length > 2 ? n.slice(0, 2) + "/" + n.slice(2) : n;
    dataBr.setCustomValidity("");
});
document.getElementById("compra_qtd").addEventListener("input", (e) => {
    e.target.value = e.target.value.replace(/\D/g, "");
});

form.addEventListener("submit", (e) => {
    const iso = brParaIso(dataBr.value);
    dataBr.setCustomValidity(iso ? "" : "Digite uma data válida no formato dd/mm/aaaa.");
    if (!form.reportValidity()) { e.preventDefault(); return; }
    document.getElementById("compra_data").value = iso;
});
