/* Botão de olho (mostrar/ocultar senha) para qualquer <input type="password">.
   Basta incluir este script na página; ele cria o botão sozinho e traz o próprio CSS. */
(function () {
    var ABERTO = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M1 12s4-7 11-7 11 7 11 7-4 7-11 7S1 12 1 12z"/><circle cx="12" cy="12" r="3"/></svg>';
    var FECHADO = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M17.94 17.94A10.9 10.9 0 0 1 12 19c-7 0-11-7-11-7a19.8 19.8 0 0 1 5.06-5.94M9.9 4.24A10.9 10.9 0 0 1 12 5c7 0 11 7 11 7a19.8 19.8 0 0 1-3.17 4.19M14.12 14.12a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>';

    var css = document.createElement("style");
    css.textContent =
        ".olho-wrap{position:relative;display:block}" +
        ".olho-wrap input{width:100%;box-sizing:border-box;padding-right:46px !important}" +
        ".olho-btn{position:absolute;top:0;right:0;width:46px;height:100%;display:flex;align-items:center;justify-content:center;" +
        "background:none;border:none;padding:0;color:#8a8a8a;cursor:pointer}" +
        ".olho-btn:hover,.olho-btn.ativo{color:#fff}" +
        ".olho-btn:focus-visible{outline:2px solid #D31235;outline-offset:-2px}";
    document.head.appendChild(css);

    document.querySelectorAll('input[type="password"]').forEach(function (input) {
        if (input.parentElement.classList.contains("olho-wrap") ||
            input.parentElement.classList.contains("config-senha-wrap")) return;

        var wrap = document.createElement("div");
        wrap.className = "olho-wrap";
        input.parentNode.insertBefore(wrap, input);
        wrap.appendChild(input);

        var btn = document.createElement("button");
        btn.type = "button";
        btn.className = "olho-btn";
        btn.tabIndex = -1;
        btn.setAttribute("aria-label", "Mostrar senha");
        btn.setAttribute("aria-pressed", "false");
        btn.innerHTML = ABERTO;
        wrap.appendChild(btn);

        btn.addEventListener("click", function () {
            var mostrar = input.type === "password";
            input.type = mostrar ? "text" : "password";
            btn.innerHTML = mostrar ? FECHADO : ABERTO;
            btn.classList.toggle("ativo", mostrar);
            btn.setAttribute("aria-pressed", mostrar ? "true" : "false");
            btn.setAttribute("aria-label", mostrar ? "Ocultar senha" : "Mostrar senha");
        });
    });
})();
