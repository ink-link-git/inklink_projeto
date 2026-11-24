document.addEventListener("DOMContentLoaded", () => {
  const lista = document.getElementById("lista-agendamentos-cliente");
  if (!lista) return;

  const statusLabels = {
    PENDENTE: "Pendente",
    CONFIRMADO: "Confirmado",
    CANCELADO: "Cancelado",
    REALIZADO: "Realizado",
  };

  function elemento(tag, classe, texto) {
    const node = document.createElement(tag);
    if (classe) node.className = classe;
    if (texto !== undefined && texto !== null && texto !== "") node.textContent = texto;
    return node;
  }

  function detalhe(rotulo, valor, classe = "") {
    const wrapper = elemento("div", `agendamento-detalhe ${classe}`.trim());
    wrapper.append(elemento("small", "", rotulo), elemento("span", "", valor || "Não informado"));
    return wrapper;
  }

  function mostrarMensagem(texto) {
    lista.replaceChildren(elemento("p", "agendamentos-mensagem", texto));
  }

  function criarCard(item) {
    const card = elemento("article", "agendamento-item");
    const topo = elemento("div", "agendamento-item-topo");
    const info = elemento("div");
    info.append(
      elemento("p", "agendamento-data", item.quando || "Data a definir"),
      elemento("p", "agendamento-tatuador", `Com ${item.nome_tatuador || item.profissional || "Tatuador"}`)
    );

    const status = String(item.status || "PENDENTE").toUpperCase();
    const classeStatus = ["PENDENTE", "CONFIRMADO", "CANCELADO", "REALIZADO"].includes(status) ? status.toLowerCase() : "default";
    const selo = elemento("span", `agendamento-status status-${classeStatus}`, statusLabels[status] || status);
    topo.append(info, selo);
    card.append(topo);

    const periodoLabels = { manha: "Manhã", tarde: "Tarde", noite: "Noite", qualquer: "Sem preferência" };
    const detalhes = elemento("div", "agendamento-detalhes");
    detalhes.append(
      detalhe("Serviço", item.servico || "Tatuagem"),
      detalhe("Período solicitado", periodoLabels[item.periodo] || item.periodo || "Não informado"),
      detalhe("Data solicitada", item.data_desejada ? new Date(`${item.data_desejada}T00:00:00`).toLocaleDateString("pt-BR") : "Não informada"),
      detalhe("Ficha de anamnese", item.tem_ficha ? "Enviada" : "Pendente")
    );
    if (item.descricao) detalhes.append(detalhe("Descrição", item.descricao, "agendamento-descricao"));
    card.append(detalhes);

    if (status === "PENDENTE" || status === "CONFIRMADO") {
      const acoes = elemento("div", "agendamento-acoes-tela");
      if (item.tem_ficha) {
        acoes.append(elemento("span", "agendamento-ficha-ok", "Ficha enviada ✓"));
      } else {
        const ficha = elemento("a", "", "Preencher ficha de anamnese");
        ficha.href = `${lista.dataset.fichaUrl}?agendamento=${encodeURIComponent(item.id)}`;
        acoes.append(ficha);
      }

      if (status === "PENDENTE") {
        if (item.whatsapp_enviado_em) {
          acoes.append(elemento("span", "agendamento-ficha-ok", "Contato por WhatsApp enviado ✓"));
        } else {
          const whats = elemento("button", "agendamento-whatsapp", "Contatar tatuador no Whatsapp");
          whats.type = "button";
          whats.addEventListener("click", () => contatarWhatsapp(item.id, whats));
          acoes.append(whats);
        }
      }

      const cancelar = elemento("button", "", "Cancelar agendamento");
      cancelar.type = "button";
      cancelar.addEventListener("click", () => cancelarAgendamento(item.id, cancelar));
      acoes.append(cancelar);
      card.append(acoes);
    }
    return card;
  }

  async function carregar() {
    mostrarMensagem("Carregando seus agendamentos...");
    try {
      const response = await fetch(lista.dataset.apiUrl, { headers: { Accept: "application/json" } });
      const data = await response.json();
      if (!response.ok || !data.success) throw new Error("Falha ao consultar agendamentos");

      if (!Array.isArray(data.agendamentos) || data.agendamentos.length === 0) {
        mostrarMensagem("Você ainda não tem agendamentos. Quando fizer um pedido, ele aparecerá aqui.");
        return;
      }
      lista.replaceChildren(...data.agendamentos.map(criarCard));
    } catch (error) {
      mostrarMensagem("Não foi possível carregar seus agendamentos. Atualize a página e tente novamente.");
    }
  }

  async function contatarWhatsapp(id, botao) {
    botao.disabled = true;
    // A janela é aberta já no clique (antes do fetch), senão o navegador bloqueia como pop-up.
    const janela = window.open("", "_blank");
    try {
      const url = lista.dataset.whatsappUrl.replace("__ID__", encodeURIComponent(id));
      const response = await fetch(url, { method: "POST", headers: { Accept: "application/json" } });
      const data = await response.json();
      if (!response.ok || !data.success) {
        if (janela) janela.close();
        window.alert(data.errors?.geral || "Não foi possível abrir o WhatsApp.");
        await carregar(); // atualiza o estado do botão (pode já ter sido usado)
        return;
      }
      if (janela) janela.location.href = data.url;
      else window.location.href = data.url;
      await carregar(); // o botão vira "Contato por WhatsApp enviado ✓"
    } catch (error) {
      if (janela) janela.close();
      window.alert("Não foi possível conectar ao servidor.");
      botao.disabled = false;
    }
  }

  async function cancelarAgendamento(id, botao) {
    if (!window.confirm("Deseja realmente cancelar este agendamento?")) return;
    botao.disabled = true;
    try {
      const url = lista.dataset.cancelarUrl.replace("__ID__", encodeURIComponent(id));
      const response = await fetch(url, { method: "PATCH", headers: { Accept: "application/json" } });
      const data = await response.json();
      if (!response.ok || !data.success) {
        window.alert(data.errors?.geral || "Não foi possível cancelar o agendamento.");
        botao.disabled = false;
        return;
      }
      await carregar();
    } catch (error) {
      window.alert("Não foi possível conectar ao servidor.");
      botao.disabled = false;
    }
  }

  carregar();
});
