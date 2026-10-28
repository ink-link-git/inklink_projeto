document.addEventListener("DOMContentLoaded", () => {
  const MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
  ];

  const form = document.getElementById("agendamento-form");
  const tatuadorSelect = document.getElementById("tatuador");
  const portfolioLink = document.getElementById("portfolio-link");
  const monthLabel = document.getElementById("calendar-month");
  const daysGrid = document.getElementById("calendar-days");
  const prevBtn = document.getElementById("prev-month");
  const nextBtn = document.getElementById("next-month");
  const timesLabel = document.getElementById("times-label");
  const periodoGrid = document.getElementById("periodo-grid");
  const submitBtn = document.getElementById("submit-btn");
  const serverMessage = document.getElementById("server-message");

  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);

  let viewDate = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
  let selectedDate = null;
  let periodo = "qualquer";

  function formatarData(date) {
    const m = String(date.getMonth() + 1).padStart(2, "0");
    const d = String(date.getDate()).padStart(2, "0");
    return `${date.getFullYear()}-${m}-${d}`;
  }

  // --- Calendário ---

  function renderCalendar() {
    const year = viewDate.getFullYear();
    const month = viewDate.getMonth();

    monthLabel.textContent = `${MESES[month]} ${year}`;
    daysGrid.innerHTML = "";

    const totalDias = new Date(year, month + 1, 0).getDate();
    const primeiroDiaSemana = new Date(year, month, 1).getDay();

    for (let i = 0; i < primeiroDiaSemana; i++) {
      const vazio = document.createElement("div");
      vazio.className = "day-cell empty";
      daysGrid.appendChild(vazio);
    }

    const semTatuador = !tatuadorSelect.value;

    for (let d = 1; d <= totalDias; d++) {
      const cellDate = new Date(year, month, d);
      const cell = document.createElement("div");
      cell.textContent = String(d);

      // Dia só fica clicável com tatuador escolhido e data de hoje em diante.
      // O horário exato é o tatuador quem define ao aceitar o pedido.
      const disponivel = !semTatuador && cellDate >= hoje;
      cell.className = disponivel ? "day-cell available" : "day-cell unavailable";

      if (disponivel) {
        cell.addEventListener("click", () => selecionarDia(cellDate, cell));
      }

      if (selectedDate && cellDate.toDateString() === selectedDate.toDateString()) {
        cell.classList.add("selected");
      }

      daysGrid.appendChild(cell);
    }

    prevBtn.disabled = (year === hoje.getFullYear() && month <= hoje.getMonth());
  }

  function selecionarDia(date, cellEl) {
    selectedDate = date;

    document.querySelectorAll(".day-cell.selected").forEach(el => el.classList.remove("selected"));
    cellEl.classList.add("selected");
    setError("data", false);
    atualizarResumo();
  }

  function atualizarResumo() {
    if (!tatuadorSelect.value) {
      timesLabel.textContent = "Escolha um tatuador e o dia que você gostaria de tatuar.";
    } else if (!selectedDate) {
      timesLabel.textContent = "Agora escolha o dia desejado no calendário.";
    } else {
      const dia = selectedDate.toLocaleDateString("pt-BR", { weekday: "long", day: "2-digit", month: "long" });
      timesLabel.textContent = `Dia escolhido: ${dia}.`;
    }
  }

  periodoGrid.querySelectorAll(".time-pill").forEach(pill => {
    pill.addEventListener("click", () => {
      periodo = pill.dataset.periodo;
      periodoGrid.querySelectorAll(".time-pill").forEach(el => el.classList.remove("selected"));
      pill.classList.add("selected");
    });
  });

  function limparSelecao() {
    selectedDate = null;
    renderCalendar();
    atualizarResumo();
  }

  prevBtn.addEventListener("click", () => {
    viewDate.setMonth(viewDate.getMonth() - 1);
    limparSelecao();
  });

  nextBtn.addEventListener("click", () => {
    viewDate.setMonth(viewDate.getMonth() + 1);
    limparSelecao();
  });

  // --- Tatuador ---

  tatuadorSelect.addEventListener("change", () => {
    setError("tatuador", false);

    if (tatuadorSelect.value && form.dataset.portfolioUrl) {
      portfolioLink.href = form.dataset.portfolioUrl.replace("__ID__", encodeURIComponent(tatuadorSelect.value));
      portfolioLink.hidden = false;
    } else {
      portfolioLink.hidden = true;
    }

    limparSelecao();
  });

  // --- Cor da pele ---

  document.querySelectorAll('input[name="pele"]').forEach(input => {
    input.addEventListener("change", () => {
      document.querySelectorAll(".skin-option").forEach(opt => opt.classList.remove("selected"));
      input.closest(".skin-option").classList.add("selected");
      setError("pele", false);
    });
  });

  // --- Upload de imagens de referência ---

  const imagensInput = document.getElementById("imagens");
  const previewsEl = document.getElementById("upload-previews");
  const MAX_IMAGENS = 4;
  const MAX_BYTES = 5 * 1024 * 1024;
  let arquivosSelecionados = [];

  imagensInput.addEventListener("change", (e) => {
    const novos = Array.from(e.target.files);
    const grandes = novos.filter(f => f.size > MAX_BYTES);
    const validos = novos.filter(f => f.size <= MAX_BYTES);

    arquivosSelecionados = arquivosSelecionados.concat(validos).slice(0, MAX_IMAGENS);
    setError("imagens", grandes.length > 0, "Cada imagem deve ter no máximo 5 MB.");
    renderPreviews();
    imagensInput.value = ""; // permite selecionar o mesmo arquivo de novo após remover
  });

  function renderPreviews() {
    previewsEl.innerHTML = "";

    arquivosSelecionados.forEach((file, index) => {
      const thumb = document.createElement("div");
      thumb.className = "preview-thumb";

      const img = document.createElement("img");
      img.src = URL.createObjectURL(file);
      img.alt = file.name;
      thumb.appendChild(img);

      const removeBtn = document.createElement("button");
      removeBtn.type = "button";
      removeBtn.className = "preview-remove";
      removeBtn.textContent = "×";
      removeBtn.setAttribute("aria-label", "Remover imagem");
      removeBtn.addEventListener("click", () => {
        arquivosSelecionados.splice(index, 1);
        renderPreviews();
      });
      thumb.appendChild(removeBtn);

      previewsEl.appendChild(thumb);
    });
  }

  // --- Validação de campos ---

  function setError(key, show, texto) {
    const el = document.getElementById(`err-${key}`);
    if (!el) return;
    if (texto) el.textContent = texto;
    el.classList.toggle("show", show);
  }

  document.getElementById("anamnese").addEventListener("change", () => setError("anamnese", false));

  // --- Envio ---

  function mostrarMensagem(texto, erro) {
    serverMessage.textContent = texto;
    serverMessage.classList.toggle("erro", !!erro);
    serverMessage.classList.add("show");
  }

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    serverMessage.classList.remove("show");
    setError("geral", false);

    let valido = true;

    if (!tatuadorSelect.value) {
      setError("tatuador", true);
      valido = false;
    }

    if (!selectedDate) {
      setError("data", true);
      valido = false;
    }

    const peleSelecionada = document.querySelector('input[name="pele"]:checked');
    if (!peleSelecionada) {
      setError("pele", true);
      valido = false;
    }

    if (!document.getElementById("anamnese").checked) {
      setError("anamnese", true);
      valido = false;
    }

    if (!valido) return;

    const dados = new FormData();
    dados.append("tatuador", tatuadorSelect.value);
    dados.append("data", formatarData(selectedDate));
    dados.append("periodo", periodo);
    dados.append("pele", peleSelecionada.value);
    dados.append("descricao", document.getElementById("descricao").value.trim());
    dados.append("anamnese", "on");
    arquivosSelecionados.forEach(f => dados.append("imagens", f));

    submitBtn.disabled = true;
    submitBtn.textContent = "Enviando...";

    try {
      const response = await fetch("/api/agendamentos", { method: "POST", body: dados });
      const data = await response.json();

      if (response.ok && data.success) {
        mostrarMensagem(data.mensagem + (data.aviso ? " " + data.aviso : ""), false);
        setTimeout(() => { window.location.href = data.anamnese_url; }, 1800);
        return;
      }

      const erros = data.errors || {};
      Object.keys(erros).forEach(chave => setError(chave, true, erros[chave]));
      if (!Object.keys(erros).length) mostrarMensagem("Erro ao enviar. Tente novamente.", true);
    } catch (err) {
      mostrarMensagem("Não foi possível conectar ao servidor. Tente novamente.", true);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Solicitar Agendamento";
    }
  });

  // --- Inicialização ---
  renderCalendar();
  atualizarResumo();
});
