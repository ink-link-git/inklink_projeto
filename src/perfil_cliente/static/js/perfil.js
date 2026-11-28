(function () {
    const form = document.getElementById("form-perfil");
    const nomeInput = document.getElementById("nome");
    const telefoneInput = document.getElementById("telefone");
    const btnEditar = document.getElementById("btn-editar");
    const btnSalvar = document.getElementById("btn-salvar");
    const btnCancelar = document.getElementById("btn-cancelar");
    const msg = document.getElementById("msg-perfil");

    // Foto de perfil: o campo só aparece no modo edição.
    const campoFoto = document.getElementById("campo-foto-container");
    const inputFoto = document.getElementById("foto_perfil");
    const avatarPerfil = document.getElementById("perfil-avatar");

    // Valores que estão salvos: é para eles que o "Cancelar" volta.
    let original = { nome: nomeInput.value, telefone: telefoneInput.value, avatarHtml: avatarPerfil.innerHTML };

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
        campoFoto.style.display = ativo ? "flex" : "none";
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
        const foto = inputFoto.files[0];
        if (foto && !/\.(jpe?g|png)$/i.test(foto.name)) {
            errors.foto_perfil = "Apenas imagens nos formatos JPG, JPEG ou PNG são permitidas.";
        }
        return errors;
    }

    // Coloca a foto (ou, sem foto, as iniciais) dentro de um círculo de avatar.
    function pintarAvatar(el, perfil, classeImg) {
        el.textContent = "";
        if (perfil.avatar_url) {
            const img = document.createElement("img");
            img.src = perfil.avatar_url;
            img.alt = "Foto de perfil";
            img.className = classeImg;
            el.appendChild(img);
        } else {
            el.textContent = perfil.iniciais;
        }
    }

    // Depois de salvar, o resto da tela acompanha o novo nome e a nova foto (sem recarregar).
    function atualizarTela(perfil) {
        document.getElementById("perfil-nome-titulo").textContent = perfil.nome;
        pintarAvatar(avatarPerfil, perfil, "perfil-img-avatar");

        const nomeBarra = document.querySelector(".cli-usuario strong");
        if (nomeBarra) nomeBarra.textContent = perfil.nome;
        const avatarBarra = document.querySelector(".cli-avatar");
        if (avatarBarra) pintarAvatar(avatarBarra, perfil, "cli-avatar-img");
    }

    // Pré-visualização da foto ao selecionar um arquivo novo
    inputFoto.addEventListener("change", (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            let img = avatarPerfil.querySelector("img");
            if (!img) {
                avatarPerfil.innerHTML = "";
                img = document.createElement("img");
                img.className = "perfil-img-avatar";
                avatarPerfil.appendChild(img);
            }
            img.src = event.target.result;
        };
        reader.readAsDataURL(file);
    });

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
        inputFoto.value = "";                          // Limpa o input file
        avatarPerfil.innerHTML = original.avatarHtml;  // Desfaz a pré-visualização
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

        // FormData (e não JSON) porque agora o formulário pode levar a foto de perfil.
        // Sem Content-Type: o navegador monta o multipart sozinho.
        const formData = new FormData();
        formData.append("nome", nomeInput.value.trim());
        formData.append("telefone", telefoneInput.value);
        if (inputFoto.files[0]) formData.append("foto_perfil", inputFoto.files[0]);

        fetch("/api/cliente/perfil", {
            method: "PATCH",
            body: formData
        })
            .then((r) => r.json().catch(() => ({})))
            .then((res) => {
                if (res.success) {
                    nomeInput.value = res.perfil.nome;
                    telefoneInput.value = res.perfil.telefone;
                    inputFoto.value = "";
                    atualizarTela(res.perfil);
                    original = { nome: res.perfil.nome, telefone: res.perfil.telefone, avatarHtml: avatarPerfil.innerHTML };
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
