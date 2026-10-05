document.addEventListener("DOMContentLoaded", () => {
  const btnEntrar = document.getElementById("btn-entrar");
  const btnCriar = document.getElementById("btn-criar");
  const eyebrowEl = document.getElementById("eyebrow-text");
  const subtitleEl = document.getElementById("subtitle-text");
  const cards = document.querySelectorAll(".perfil-card");

  // Textos que mudam de acordo com a intenção (entrar x criar conta)
  const TEXTOS = {
    login: {
      eyebrow: "Bem-vindo de volta",
      subtitle: "Escolha seu perfil para continuar"
    },
    cadastro: {
      eyebrow: "Bem-vindo",
      subtitle: "Vamos criar sua conta"
    }
  };

  // Para onde cada combinação (modo + tipo de perfil) deve navegar
  const ROTAS = {
    login: {
      cliente: "/login/cliente",
      tatuador: "/login/tatuador"
    },
    cadastro: {
      cliente: "/cadastro/cliente",
      tatuador: "/cadastro/tatuador"
    }
  };

  let modoAtual = "login";

  function setModo(modo) {
    modoAtual = modo;

    btnEntrar.classList.toggle("active", modo === "login");
    btnEntrar.setAttribute("aria-selected", modo === "login");

    btnCriar.classList.toggle("active", modo === "cadastro");
    btnCriar.setAttribute("aria-selected", modo === "cadastro");

    eyebrowEl.textContent = TEXTOS[modo].eyebrow;
    subtitleEl.textContent = TEXTOS[modo].subtitle;
  }

  btnEntrar.addEventListener("click", () => setModo("login"));
  btnCriar.addEventListener("click", () => setModo("cadastro"));

  cards.forEach((card) => {
    card.addEventListener("click", () => {
      const tipo = card.dataset.tipo;
      const destino = ROTAS[modoAtual][tipo];
      if (destino) {
        window.location.href = destino;
      }
    });
  });
});
