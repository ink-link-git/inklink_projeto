(function () {
    var form = document.getElementById("form-senha");
    var btn = document.getElementById("btn-senha");
    var msg = document.getElementById("msg-senha");

    function limpar() {
        msg.textContent = "";
        msg.className = "config-msg";
        form.querySelectorAll("[data-erro]").forEach(function (el) { el.textContent = ""; });
        form.querySelectorAll("input").forEach(function (el) { el.classList.remove("invalido"); });
    }

    function mostrarErros(errors) {
        Object.keys(errors).forEach(function (campo) {
            var el = form.querySelector('[data-erro="' + campo + '"]');
            if (el) {
                el.textContent = errors[campo];
                var input = form.elements[campo];
                if (input) input.classList.add("invalido");
            } else {
                msg.textContent = errors[campo];
                msg.className = "config-msg erro";
            }
        });
    }

    form.querySelectorAll(".config-olho").forEach(function (olho) {
        olho.addEventListener("click", function () {
            var input = olho.parentElement.querySelector("input");
            var mostrar = input.type === "password";
            input.type = mostrar ? "text" : "password";
            olho.setAttribute("aria-pressed", mostrar ? "true" : "false");
            olho.setAttribute("aria-label", mostrar ? "Ocultar senha" : "Mostrar senha");
            olho.classList.toggle("ativo", mostrar);
        });
    });

    form.addEventListener("submit", function (e) {
        e.preventDefault();
        limpar();
        btn.disabled = true;
        btn.textContent = "Salvando...";

        fetch("/api/cliente/senha", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                atual: form.elements.atual.value,
                nova: form.elements.nova.value,
                confirmar: form.elements.confirmar.value
            })
        })
            .then(function (r) { return r.json().catch(function () { return {}; }); })
            .then(function (res) {
                if (res.success) {
                    form.reset();
                    form.querySelectorAll(".config-olho.ativo").forEach(function (o) { o.click(); });
                    msg.textContent = res.message;
                    msg.className = "config-msg ok";
                } else {
                    mostrarErros(res.errors || { geral: "Não foi possível alterar a senha." });
                }
            })
            .catch(function () {
                msg.textContent = "Erro de conexão. Tente novamente.";
                msg.className = "config-msg erro";
            })
            .then(function () {
                btn.disabled = false;
                btn.textContent = "Salvar nova senha";
            });
    });
})();
