document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("login-form");
  const emailInput = document.getElementById("email");
  const senhaInput = document.getElementById("senha");
  const submitBtn = document.getElementById("submit-btn");
  const serverErrorEl = document.getElementById("server-error");

  const fieldMap = {
    email: { input: emailInput, err: document.getElementById("err-email") },
    senha: { input: senhaInput, err: document.getElementById("err-senha") }
  };

  function setError(fieldKey, isInvalid) {
    const item = fieldMap[fieldKey];
    item.input.classList.toggle("error", isInvalid);
    item.err.classList.toggle("show", isInvalid);
  }

  function showServerError(message) {
    serverErrorEl.innerText = message;
    serverErrorEl.classList.add("show");
  }

  function clearServerError() {
    serverErrorEl.classList.remove("show");
    serverErrorEl.innerText = "";
  }

  function validateEmail() {
    const ok = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim());
    setError("email", !ok);
    return ok;
  }

  function validateSenha() {
    const ok = senhaInput.value.length > 0;
    setError("senha", !ok);
    return ok;
  }

  emailInput.addEventListener("blur", validateEmail);
  senhaInput.addEventListener("blur", validateSenha);

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearServerError();

    const isEmailValid = validateEmail();
    const isSenhaValid = validateSenha();
    if (!isEmailValid || !isSenhaValid) return;

    submitBtn.disabled = true;
    submitBtn.innerText = "Entrando...";

    try {
      const response = await fetch("/api/login/cliente", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: emailInput.value.trim(),
          senha: senhaInput.value
        })
      });

      const data = await response.json();

      if (response.ok && data.success) {
        window.location.href = data.redirect;
        return;
      }

      submitBtn.disabled = false;
      submitBtn.innerText = "Entrar";
      showServerError((data.errors && data.errors.geral) || "Não foi possível entrar. Tente novamente.");
    } catch (error) {
      submitBtn.disabled = false;
      submitBtn.innerText = "Entrar";
      showServerError("Erro ao conectar com o servidor.");
    }
  });
});
