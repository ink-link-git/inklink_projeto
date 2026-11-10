(function () {
    var busca = document.getElementById("tat-busca");
    if (!busca) return;

    var fichas = document.querySelectorAll(".tat-ficha");
    var semResultado = document.getElementById("tat-sem-resultado");
    var chips = document.querySelectorAll(".tat-chip");
    var filtroAtivo = "";

    function aplicar() {
        var termo = busca.value.trim().toLowerCase();
        var visiveis = 0;
        fichas.forEach(function (f) {
            var bateBusca = !termo || f.dataset.busca.indexOf(termo) !== -1;
            var bateTipo = !filtroAtivo || (" " + f.dataset.tags + " ").indexOf(" " + filtroAtivo + " ") !== -1;
            var mostrar = bateBusca && bateTipo;
            f.hidden = !mostrar;
            if (mostrar) visiveis++;
        });
        semResultado.hidden = visiveis > 0;
    }

    busca.addEventListener("input", aplicar);

    chips.forEach(function (chip) {
        chip.addEventListener("click", function () {
            // Clicar no chip já ativo volta para "Todos".
            filtroAtivo = (chip.dataset.filtro === filtroAtivo) ? "" : chip.dataset.filtro;
            chips.forEach(function (c) {
                var ativo = c.dataset.filtro === filtroAtivo;
                c.classList.toggle("ativo", ativo);
                c.setAttribute("aria-pressed", ativo ? "true" : "false");
            });
            aplicar();
        });
    });
})();
