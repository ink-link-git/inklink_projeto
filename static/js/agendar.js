document.addEventListener("DOMContentLoaded", () => {
  const MESES = [
    "janeiro", "fevereiro", "março", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
  ];

  const monthLabel = document.getElementById("calendar-month");
  const daysGrid = document.getElementById("calendar-days");
  const prevBtn = document.getElementById("prev-month");
  const nextBtn = document.getElementById("next-month");
  const timesLabel = document.getElementById("times-label");
  const timesGrid = document.getElementById("times-grid");

  const hoje = new Date();
  hoje.setHours(0, 0, 0, 0);

  let viewDate = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
  let selectedDate = null;
  let selectedTime = null;

  // --- Simulação de disponibilidade ---
  // TODO: substituir por consulta real ao Supabase quando a tabela de
  // agendamentos/horários existir. Por enquanto, gera disponibilidade
  // aleatória só pra já termos o front-end funcional.

  function diaEstaDisponivel(date) {
    if (date < hoje) return false;
    return Math.random() < 0.55;
  }

  function gerarHorariosSimulados() {
    const base = ["09:00", "10:30", "12:00", "14:00", "15:30", "17:00"];
    return base.filter(() => Math.random() < 0.6);
  }

  // --- Renderização do calendário ---

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

    for (let d = 1; d <= totalDias; d++) {
      const cellDate = new Date(year, month, d);
      const cell = document.createElement("div");
      cell.textContent = String(d);

      const disponivel = diaEstaDisponivel(cellDate);
      cell.className = disponivel ? "day-cell available" : "day-cell unavailable";

      if (disponivel) {
        cell.addEventListener("click", () => selecionarDia(cellDate, cell));
      }

      if (selectedDate && cellDate.toDateString() === selectedDate.toDateString()) {
        cell.classList.add("selected");
      }

      daysGrid.appendChild(cell);
    }

    // Não deixa navegar para meses anteriores ao atual
    prevBtn.disabled = (year === hoje.getFullYear() && month <= hoje.getMonth());
  }

  function selecionarDia(date, cellEl) {
    selectedDate = date;
    selectedTime = null;

    document.querySelectorAll(".day-cell.selected").forEach(el => el.classList.remove("selected"));
    cellEl.classList.add("selected");

    renderHorarios();
    setError("horario", false);
  }

  function renderHorarios() {
    timesGrid.innerHTML = "";

    if (!selectedDate) {
      timesLabel.textContent = "Selecione um dia disponível para ver os horários.";
      return;
    }

    const horarios = gerarHorariosSimulados();

    if (horarios.length === 0) {
      timesLabel.textContent = "Nenhum horário disponível nesse dia — tente outra data.";
      return;
    }

    timesLabel.textContent = "Horários disponíveis:";

    horarios.forEach(hora => {
      const pill = document.createElement("button");
      pill.type = "button";
      pill.className = "time-pill";
      pill.textContent = hora;

      pill.addEventListener("click", () => {
        selectedTime = hora;
        document.querySelectorAll(".time-pill.selected").forEach(el => el.classList.remove("selected"));
        pill.classList.add("selected");
        setError("horario", false);
      });

      timesGrid.appendChild(pill);
    });
  }

  prevBtn.addEventListener("click", () => {
    viewDate.setMonth(viewDate.getMonth() - 1);
    selectedDate = null;
    selectedTime = null;
    renderCalendar();
    renderHorarios();
  });

  nextBtn.addEventListener("click", () => {
    viewDate.setMonth(viewDate.getMonth() + 1);
    selectedDate = null;
    selectedTime = null;
    renderCalendar();
    renderHorarios();
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
  let arquivosSelecionados = [];

  imagensInput.addEventListener("change", (e) => {
    const novos = Array.from(e.target.files);
    arquivosSelecionados = arquivosSelecionados.concat(novos).slice(0, MAX_IMAGENS);
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

  function setError(key, show) {
    const el = document.getElementById(`err-${key}`);
    if (el) el.classList.toggle("show", show);
  }

  // --- Envio (ainda sem backend — só simula) ---

  const form = document.getElementById("agendamento-form");
  const serverMessage = document.getElementById("server-message");

  form.addEventListener("submit", (e) => {
    e.preventDefault();

    let valido = true;

    if (!selectedDate || !selectedTime) {
      setError("horario", true);
      valido = false;
    } else {
      setError("horario", false);
    }

    const peleSelecionada = document.querySelector('input[name="pele"]:checked');
    if (!peleSelecionada) {
      setError("pele", true);
      valido = false;
    } else {
      setError("pele", false);
    }

    const anamneseConfirmada = document.getElementById("anamnese").checked;
    if (!anamneseConfirmada) {
      setError("anamnese", true);
      valido = false;
    } else {
      setError("anamnese", false);
    }

    if (!valido) return;

    // TODO: trocar por um fetch de verdade quando a rota de agendamento existir no backend.
    const payload = {
      data: selectedDate.toISOString().slice(0, 10),
      horario: selectedTime,
      corPele: peleSelecionada.value,
      descricao: document.getElementById("descricao").value,
      imagens: arquivosSelecionados.map(f => f.name)
    };
    console.log("Payload do agendamento (simulado):", payload);

    serverMessage.textContent = "Solicitação enviada! (simulação — integração com o backend vem depois)";
    serverMessage.classList.add("show");
  });

  // --- Inicialização ---
  renderCalendar();
  renderHorarios();
});
