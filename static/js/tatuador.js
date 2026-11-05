document.addEventListener("DOMContentLoaded", () => {
    const nomeInput = document.getElementById("nome");
    const emailInput = document.getElementById("email");
    const cpfInput = document.getElementById("cpf");
    const telefoneInput = document.getElementById("telefone");
    const especialidadeInput = document.getElementById("especialidade");
    const senhaInput = document.getElementById("senha");
    const confirmarInput = document.getElementById("confirmar");
    
    const submitBtn = document.getElementById("submit-btn");
    const form = document.getElementById("registerForm");
    const strengthBars = document.querySelectorAll("#strength span");
    const serverErrorEl = document.getElementById("server-error");
  
    const fieldMap = {
      nome: { input: nomeInput, err: document.getElementById("err-nome") },
      email: { input: emailInput, err: document.getElementById("err-email") },
      cpf: { input: cpfInput, err: document.getElementById("err-cpf") },
      telefone: { input: telefoneInput, err: document.getElementById("err-telefone") },
      especialidade: { input: especialidadeInput, err: document.getElementById("err-especialidade") },
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
  
    // Validações individuais
    function validateNome() {
      const ok = nomeInput.value.trim().length >= 2;
      setError("nome", !ok);
      return ok;
    }
  
    function validateEmail() {
      const ok = /^[^^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailInput.value.trim());
      setError("email", !ok);
      return ok;
    }

    function validateCpf() {
      const digits = cpfInput.value.replace(/\D/g, "");
      const ok = digits.length === 11;
      setError("cpf", !ok);
      return ok;
    }
  
    function validateTelefone() {
      const digits = telefoneInput.value.replace(/\D/g, "");
      const ok = digits.length >= 10;
      setError("telefone", !ok);
      return ok;
    }

    function validateEspecialidade() {
      const ok = especialidadeInput.value.trim().length > 0;
      setError("especialidade", !ok);
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
        bar.style.background = index < score ? "#cc2936" : "#333";
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
  
    // Máscaras de CPF e Telefone
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

    // Botões de mostrar/ocultar senha
    function setupToggle(btnId, inputEl) {
        const btn = document.getElementById(btnId);
        if(btn && inputEl) {
            btn.addEventListener("click", () => {
                const type = inputEl.type === "password" ? "text" : "password";
                inputEl.type = type;
            });
        }
    }
    setupToggle("toggle-senha", senhaInput);
    setupToggle("toggle-confirmar", confirmarInput);
  
    // Eventos de Blur
    nomeInput.addEventListener("blur", validateNome);
    emailInput.addEventListener("blur", validateEmail);
    cpfInput.addEventListener("blur", validateCpf);
    telefoneInput.addEventListener("blur", validateTelefone);
    especialidadeInput.addEventListener("blur", validateEspecialidade);
    senhaInput.addEventListener("blur", validateSenha);
    senhaInput.addEventListener("input", updateStrength);
    confirmarInput.addEventListener("blur", validateConfirmar);
  
    // Envio do formulário via Fetch
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      clearServerError();
  
      const isValid = validateNome() & validateEmail() & validateCpf() & validateTelefone() & validateEspecialidade() & validateSenha() & validateConfirmar();
      if (!isValid) return;
  
      submitBtn.disabled = true;
      submitBtn.innerText = "Criando conta...";
  
      const payload = {
        nome: nomeInput.value.trim(),
        email: emailInput.value.trim(),
        cpf: cpfInput.value.replace(/\D/g, ""), // Envia apenas dígitos se preferir
        tel: telefoneInput.value.replace(/\D/g, ""), // Mapeado para o nome da coluna no DB ('tel')
        especialidade: especialidadeInput.value.trim(),
        senha: senhaInput.value,
        confirmar: confirmarInput.value
      };
  
      try {
        const response = await fetch("/api/tatuador", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
  
        const data = await response.json();
  
        if (response.ok && data.success) {
          submitBtn.innerText = "Conta criada ✓";
          setTimeout(() => {
            window.location.href = "/login/tatuador";
          }, 1000);
          return;
        }
  
        submitBtn.disabled = false;
        submitBtn.innerText = "Criar Conta";
  
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
        submitBtn.innerText = "Criar Conta";
        serverErrorEl.innerText = "Erro ao conectar com o servidor.";
        serverErrorEl.classList.add("show");
      }
    });
});