(function () {
    const form = document.getElementById("form-perfil");
    const nomeInput = document.getElementById("nome");
    const telefoneInput = document.getElementById("telefone");
    const btnEditar = document.getElementById("btn-editar");
    const btnSalvar = document.getElementById("btn-salvar");
    const btnCancelar = document.getElementById("btn-cancelar");
    const msg = document.getElementById("msg-perfil");

    // Valores que estão salvos: é para eles que o "Cancelar" volta.
    let original = { nome: nomeInput.value, telefone: telefoneInput.value };

    function limpar() {
        msg.textContent = "";
        msg.className = "perfil-msg";
        form.querySelectorAll("[data-erro]").forEach((el) => { el.textContent = ""; });
        form.querySelectorAll("input").forEach((el) => el.classList.remove("invalido"));
    }

    function mostrarErros(errors) {
        Object.keys(errors).forEach((campo) => {
            const el = form.querySelector(`[data-erro="${campo}"]`);
            if (el) {
                el.textContent = errors[campo];
                const input = form.elements[campo];
                if (input) input.classList.add("invalido");
            } else {
                msg.textContent = errors[campo];
                msg.className = "perfil-msg erro";
            }
        });
    }

    // Alterna entre "só leitura" e "editando" (nome e telefone; o e-mail nunca libera).
    function modoEdicao(ativo) {
        nomeInput.readOnly = !ativo;
        telefoneInput.readOnly = !ativo;
        form.classList.toggle("editando", ativo);
        btnEditar.hidden = ativo;
        btnSalvar.hidden = !ativo;
        btnCancelar.hidden = !ativo;
    }

    function formatarTelefone(valor) {
        const digitos = valor.replace(/\D/g, "").slice(0, 11);
        if (digitos.length > 10) return `(${digitos.slice(0, 2)}) ${digitos.slice(2, 7)}-${digitos.slice(7)}`;
        if (digitos.length > 6) return `(${digitos.slice(0, 2)}) ${digitos.slice(2, 6)}-${digitos.slice(6)}`;
        if (digitos.length > 2) return `(${digitos.slice(0, 2)}) ${digitos.slice(2)}`;
        return digitos;
    }

    // Mesmas regras do servidor (forms.py); o servidor sempre valida de novo.
    function validar() {
        const errors = {};
        if (nomeInput.value.trim().split(/\s+/).filter(Boolean).length < 2) {
            errors.nome = "Informe seu nome completo.";
        }
        if (telefoneInput.value.replace(/\D/g, "").length < 10) {
            errors.telefone = "Informe um telefone válido (com DDD).";
        }
        return errors;
    }

    // Depois de salvar, o resto da tela acompanha o novo nome (sem recarregar).
    function atualizarTela(perfil) {
        document.getElementById("perfil-nome-titulo").textContent = perfil.nome;
        document.getElementById("perfil-avatar").textContent = perfil.iniciais;

        const nomeBarra = document.querySelector(".cli-usuario strong");
        if (nomeBarra) nomeBarra.textContent = perfil.nome;
        const avatarBarra = document.querySelector(".cli-avatar");
        if (avatarBarra) avatarBarra.textContent = perfil.iniciais;
    }

    telefoneInput.addEventListener("input", () => {
        telefoneInput.value = formatarTelefone(telefoneInput.value);
    });

    btnEditar.addEventListener("click", () => {
        limpar();
        modoEdicao(true);
        nomeInput.focus();
    });

    btnCancelar.addEventListener("click", () => {
        limpar();
        nomeInput.value = original.nome;
        telefoneInput.value = original.telefone;
        modoEdicao(false);
    });

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        limpar();

        const errors = validar();
        if (Object.keys(errors).length) {
            mostrarErros(errors);
            return;
        }

        btnSalvar.disabled = true;
        btnSalvar.textContent = "Salvando...";

        fetch("/api/cliente/perfil", {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                nome: nomeInput.value.trim(),
                telefone: telefoneInput.value
            })
        })
            .then((r) => r.json().catch(() => ({})))
            .then((res) => {
                if (res.success) {
                    original = { nome: res.perfil.nome, telefone: res.perfil.telefone };
                    nomeInput.value = original.nome;
                    telefoneInput.value = original.telefone;
                    atualizarTela(res.perfil);
                    modoEdicao(false);
                    msg.textContent = res.message;
                    msg.className = "perfil-msg ok";
                } else {
                    mostrarErros(res.errors || { geral: "Não foi possível salvar as alterações." });
                }
            })
            .catch(() => {
                msg.textContent = "Erro de conexão. Tente novamente.";
                msg.className = "perfil-msg erro";
            })
            .then(() => {
                btnSalvar.disabled = false;
                btnSalvar.textContent = "Salvar alterações";
            });
    });
})();
