document.addEventListener("DOMContentLoaded", () => {
  const emailInput = document.getElementById("email");
  const senhaInput = document.getElementById("senha");

  const submitBtn = document.getElementById("submit-btn");
  const form = document.getElementById("login-form");
  const serverErrorEl = document.getElementById("server-error");

  const fieldMap = {
    email: { input: emailInput, err: document.getElementById("err-email") },
    senha: { input: senhaInput, err: document.getElementById("err-senha") }
  };

  function setError(fieldKey, isInvalid, customMessage = null) {
    const item = fieldMap[fieldKey];
    if (!item) return;

    item.input.classList.toggle("error", isInvalid);
    item.err.classList.toggle("show", isInvalid);
    if (customMessage) {
      item.err.innerText = customMessage;
    }
  }

  function clearServerError() {
    serverErrorEl.classList.remove("show");
    serverErrorEl.innerText = "";
  }

  // --- Validações individuais ---
  function validateEmail() {
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim());
    setError("email", !ok);
    return ok;
  }

  function validateSenha() {
    // Login só checa se preencheu — a regra de força/tamanho já foi
    // aplicada lá no cadastro, não faz sentido repetir aqui.
    const ok = senhaInput.value.length > 0;
    setError("senha", !ok);
    return ok;
  }

  // --- Eventos de perda de foco (Blur) ---
  emailInput.addEventListener("blur", validateEmail);
  senhaInput.addEventListener("blur", validateSenha);

  // --- Envio do formulário via Fetch API ---
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearServerError();

    const isEmailValid = validateEmail();
    const isSenhaValid = validateSenha();

    if (!isEmailValid || !isSenhaValid) {
      return;
    }

    submitBtn.disabled = true;
    submitBtn.innerText = "Entrando...";

    const payload = {
      email: emailInput.value.trim(),
      senha: senhaInput.value
    };

    try {
      const response = await fetch("/api/login/cliente", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (response.ok && data.success) {
        submitBtn.innerText = "Login efetuado ✓";
        return;
      }

      submitBtn.disabled = false;
      submitBtn.innerText = "Entrar";

      if (data.errors) {
        Object.keys(data.errors).forEach(key => {
          if (fieldMap[key]) {
            setError(key, true, data.errors[key]);
          } else {
            serverErrorEl.innerText = data.errors[key];
            serverErrorEl.classList.add("show");
          }
        });
      } else {
        serverErrorEl.innerText = "Não foi possível entrar. Tente novamente.";
        serverErrorEl.classList.add("show");
      }

    } catch (error) {
      submitBtn.disabled = false;
      submitBtn.innerText = "Entrar";
      serverErrorEl.innerText = "Erro ao conectar com o servidor.";
      serverErrorEl.classList.add("show");
    }
  });
});
