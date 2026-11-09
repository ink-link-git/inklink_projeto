document.addEventListener("DOMContentLoaded", () => {
  const lista = document.getElementById("lista-agendamentos");
  if (!lista) return; // módulo de agendamento ainda não instalado
  const DIAS = ["dom", "seg", "ter", "qua", "qui", "sex", "sáb"];

  function formatarDataHora(texto) {
    const dt = new Date(texto);
    if (isNaN(dt)) return texto || "";
    const dia = String(dt.getDate()).padStart(2, "0");
    const mes = String(dt.getMonth() + 1).padStart(2, "0");
    const hora = String(dt.getHours()).padStart(2, "0");
    const min = String(dt.getMinutes()).padStart(2, "0");
    return `${DIAS[dt.getDay()]}, ${dia}/${mes}/${dt.getFullYear()} às ${hora}:${min}`;
  }

  function mensagem(texto) {
    lista.innerHTML = "";
    const p = document.createElement("p");
    p.className = "home-vazio";
    p.textContent = texto;
    lista.appendChild(p);
  }

  function criarCard(item) {
    const card = document.createElement("div");
    card.className = "agendamento-card";

    const topo = document.createElement("div");
    topo.className = "agendamento-topo";
    const quando = document.createElement("strong");
    quando.textContent = item.quando;
    const selo = document.createElement("span");
    selo.className = `selo selo-${item.status.toLowerCase()}`;
    selo.textContent = item.status.charAt(0) + item.status.slice(1).toLowerCase();
    topo.append(quando, selo);

    const quem = document.createElement("p");
    quem.className = "agendamento-info";
    quem.textContent = `Com ${item.nome_tatuador}`;
    card.append(topo, quem);

    const ativo = item.status === "PENDENTE" || item.status === "CONFIRMADO";
    if (ativo) {
      const acoes = document.createElement("div");
      acoes.className = "agendamento-acoes";

      if (!lista.dataset.fichaUrl || lista.dataset.fichaUrl === "#") {
        // sem módulo de anamnese: não mostra o atalho
      } else if (!item.tem_ficha) {
        const ficha = document.createElement("a");
        ficha.href = `${lista.dataset.fichaUrl}?agendamento=${item.id}`;
        ficha.textContent = "Preencher ficha";
        acoes.appendChild(ficha);
      } else {
        const ok = document.createElement("span");
        ok.className = "ficha-ok";
        ok.textContent = "Ficha enviada ✓";
        acoes.appendChild(ok);
      }

      const cancelar = document.createElement("button");
      cancelar.type = "button";
      cancelar.textContent = "Cancelar";
      cancelar.addEventListener("click", () => cancelarAgendamento(item.id, cancelar));
      acoes.appendChild(cancelar);

      card.appendChild(acoes);
    }
    return card;
  }

  async function cancelarAgendamento(id, botao) {
    if (!confirm("Deseja cancelar este agendamento?")) return;

    botao.disabled = true;
    try {
      const response = await fetch(lista.dataset.cancelarUrl.replace("__ID__", id), { method: "PATCH" });
      const data = await response.json();
      if (!response.ok || !data.success) {
        alert((data.errors && data.errors.geral) || "Não foi possível cancelar.");
        botao.disabled = false;
        return;
      }
      carregar();
    } catch (err) {
      alert("Não foi possível conectar ao servidor.");
      botao.disabled = false;
    }
  }

  async function carregar() {
    try {
      const response = await fetch("/api/cliente/agendamentos");
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error();

      if (data.agendamentos.length === 0) {
        mensagem("Você ainda não tem agendamentos.");
        return;
      }

      lista.innerHTML = "";
      data.agendamentos.forEach((item) => lista.appendChild(criarCard(item)));
    } catch (err) {
      mensagem("Não foi possível carregar seus agendamentos agora.");
    }
  }

  carregar();
});
