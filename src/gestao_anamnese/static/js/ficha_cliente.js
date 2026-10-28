document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("ficha-form");
  if (!form) return;

  const submitBtn = document.getElementById("submit-btn");
  const serverErrorEl = document.getElementById("server-error");

  function setError(key, show, texto) {
    const el = document.getElementById(`err-${key}`);
    if (!el) return;
    if (texto) el.textContent = texto;
    el.classList.toggle("show", show);
  }

  function showServerError(message) {
    serverErrorEl.innerText = message;
    serverErrorEl.classList.add("show");
  }

  // Mostra o campo de detalhe só quando a resposta é "Sim"
  form.querySelectorAll('input[type="radio"][data-detalhe]').forEach((radio) => {
    radio.addEventListener("change", () => {
      const campo = radio.name;
      const sim = form.querySelector(`input[name="${campo}"][value="sim"]`).checked;
      const caixa = document.getElementById(`detalhe-${campo}`);
      caixa.hidden = !sim;
      if (!sim) {
        document.getElementById(radio.dataset.detalhe).value = "";
        setError(radio.dataset.detalhe, false);
      }
    });
  });

  // Limpa os erros ao mexer nos campos
  form.addEventListener("input", (e) => {
    const alvo = e.target;
    setError(alvo.id || alvo.name, false);
  });
  form.addEventListener("change", (e) => {
    const alvo = e.target;
    setError(alvo.id || alvo.name, false);
  });

  function montarPayload() {
    const payload = { agendamento: document.getElementById("agendamento").value };

    form.querySelectorAll('input[type="radio"][value="sim"]').forEach((radio) => {
      payload[radio.name] = radio.checked;
      if (radio.dataset.detalhe) {
        payload[radio.dataset.detalhe] = document.getElementById(radio.dataset.detalhe).value.trim();
      }
    });

    payload.ciente_riscos = document.getElementById("ciente_riscos").checked;
    payload.termo_aceito = document.getElementById("termo_aceito").checked;
    return payload;
  }

  function validar(payload) {
    let valido = true;

    if (!payload.agendamento) {
      setError("agendamento", true);
      valido = false;
    }

    form.querySelectorAll('input[type="radio"][value="sim"][data-detalhe]').forEach((radio) => {
      const campoDetalhe = radio.dataset.detalhe;
      if (radio.checked && !payload[campoDetalhe]) {
        setError(campoDetalhe, true);
        valido = false;
      }
    });

    if (!payload.ciente_riscos) {
      setError("ciente_riscos", true);
      valido = false;
    }
    if (!payload.termo_aceito) {
      setError("termo_aceito", true);
      valido = false;
    }
    return valido;
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    serverErrorEl.classList.remove("show");

    const payload = montarPayload();
    if (!validar(payload)) return;

    submitBtn.disabled = true;
    submitBtn.textContent = "Enviando...";

    try {
      const response = await fetch("/api/anamnese", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      if (response.ok && data.success) {
        submitBtn.textContent = "Ficha enviada!";
        setTimeout(() => { window.location.href = data.redirect || form.dataset.redirect; }, 1200);
        return;
      }

      const erros = data.errors || {};
      Object.keys(erros).forEach((chave) => {
        if (chave === "geral") showServerError(erros[chave]);
        else setError(chave, true, erros[chave]);
      });
      if (!Object.keys(erros).length) showServerError("Erro ao enviar. Tente novamente.");
    } catch (err) {
      showServerError("Não foi possível conectar ao servidor. Tente novamente.");
    }

    submitBtn.disabled = false;
    submitBtn.textContent = "Enviar ficha";
  });
});
