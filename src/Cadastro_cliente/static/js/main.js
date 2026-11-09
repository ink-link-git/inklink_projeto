document.addEventListener("DOMContentLoaded", () => {
    const nomeInput = document.getElementById("nome");
    const cpfInput = document.getElementById("cpf");
    const emailInput = document.getElementById("email");
    const telefoneInput = document.getElementById("telefone");
    const senhaInput = document.getElementById("senha");
    const confirmarInput = document.getElementById("confirmar");
    
    const submitBtn = document.getElementById("submit-btn");
    const form = document.getElementById("signup-form");
    const strengthBars = document.querySelectorAll("#strength span");
    const serverErrorEl = document.getElementById("server-error");
  
    const fieldMap = {
      nome: { input: nomeInput, err: document.getElementById("err-nome") },
      cpf: { input: cpfInput, err: document.getElementById("err-cpf") },
      email: { input: emailInput, err: document.getElementById("err-email") },
      telefone: { input: telefoneInput, err: document.getElementById("err-telefone") },
      senha: { input: senhaInput, err: document.getElementById("err-senha") },
      confirmar: { input: confirmarInput, err: document.getElementById("err-confirmar") }
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
    function validateNome() {
      const parts = nomeInput.value.trim().split(" ").filter(p => p.length > 0);
      const ok = parts.length >= 2;
      setError("nome", !ok);
      return ok;
    }
  
    function validateCpf() {
      const digits = cpfInput.value.replace(/\D/g, "");
      const ok = digits.length === 11;
      setError("cpf", !ok);
      return ok;
    }
  
    function validateEmail() {
      const ok = /^[^^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim());
      setError("email", !ok);
      return ok;
    }
  
    function validateTelefone() {
      const digits = telefoneInput.value.replace(/\D/g, "");
      const ok = digits.length >= 10;
      setError("telefone", !ok);
      return ok;
    }
  
    function calculatePasswordScore(val) {
      let score = 0;
      if (val.length >= 8) score++;
      if (/[A-Z]/.test(val) && /[a-z]/.test(val)) score++;
      if (/\d/.test(val)) score++;
      if (/[^A-Za-z0-9]/.test(val)) score++;
      return score;
    }
  
    function updateStrength() {
      const score = calculatePasswordScore(senhaInput.value);
      strengthBars.forEach((bar, index) => {
        bar.style.background = index < score ? "var(--primary)" : "var(--border)";
      });
    }
  
    function validateSenha() {
      const ok = senhaInput.value.length >= 8;
      setError("senha", senhaInput.value.length > 0 && !ok);
      updateStrength();
      return ok;
    }
  
    function validateConfirmar() {
      const ok = confirmarInput.value.length > 0 && confirmarInput.value === senhaInput.value;
      setError("confirmar", confirmarInput.value.length > 0 && !ok);
      return ok;
    }
  
    // --- Máscaras de entrada ---
    cpfInput.addEventListener("input", (e) => {
      let value = e.target.value.replace(/\D/g, "").slice(0, 11);
      value = value.replace(/(\d{3})(\d)/, "$1.$2");
      value = value.replace(/(\d{3})(\d)/, "$1.$2");
      value = value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
      e.target.value = value;
    });
  
    telefoneInput.addEventListener("input", (e) => {
      let digits = e.target.value.replace(/\D/g, "").slice(0, 11);
      if (digits.length > 6) {
        e.target.value = `(${digits.slice(0, 2)}) ${digits.slice(2, 7)}-${digits.slice(7)}`;
      } else if (digits.length > 2) {
        e.target.value = `(${digits.slice(0, 2)}) ${digits.slice(2)}`;
      } else {
        e.target.value = digits;
      }
    });
  
    // --- Eventos de perda de foco (Blur) ---
    nomeInput.addEventListener("blur", validateNome);
    cpfInput.addEventListener("blur", validateCpf);
    emailInput.addEventListener("blur", validateEmail);
    telefoneInput.addEventListener("blur", validateTelefone);
    senhaInput.addEventListener("blur", validateSenha);
    senhaInput.addEventListener("input", updateStrength);
    confirmarInput.addEventListener("blur", validateConfirmar);
  
    // --- Envio do formulário via Fetch API ---
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearServerError();
  
      const isNomeValid = validateNome();
      const isCpfValid = validateCpf();
      const isEmailValid = validateEmail();
      const isTelefoneValid = validateTelefone();
      const isSenhaValid = validateSenha();
      const isConfirmarValid = validateConfirmar();
  
      if (!isNomeValid || !isCpfValid || !isEmailValid || !isTelefoneValid || !isSenhaValid || !isConfirmarValid) {
        return;
      }
  
      submitBtn.disabled = true;
      submitBtn.innerText = "Criando conta...";
  
      const payload = {
        nome: nomeInput.value.trim(),
        cpf: cpfInput.value.trim(),
        email: emailInput.value.trim(),
        telefone: telefoneInput.value.trim(),
        senha: senhaInput.value,
        confirmar: confirmarInput.value
      };
  
      try {
        const response = await fetch("/api/index", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
  
        const data = await response.json();
  
        if (response.ok && data.success) {
          submitBtn.innerText = "Conta criada ✓";
          form.reset();
          strengthBars.forEach(b => b.style.background = "var(--border)");
          return;
        }
  
        submitBtn.disabled = false;
        submitBtn.innerText = "Criar conta";
  
        // Exibe erros de validação retornados pelo servidor
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
          serverErrorEl.innerText = "Não foi possível criar a conta. Tente novamente.";
          serverErrorEl.classList.add("show");
        }
  
      } catch (error) {
        submitBtn.disabled = false;
        submitBtn.innerText = "Criar conta";
        serverErrorEl.innerText = "Erro ao conectar com o servidor.";
        serverErrorEl.classList.add("show");
      }
    });
  });