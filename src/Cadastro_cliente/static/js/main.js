document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    const senhaInput = document.getElementById('senha');
    const confirmarSenhaInput = document.getElementById('confirmar-senha');
    
    // Elemento das barrinhas de força (certifique-se de ter elementos correspondentes no HTML)
    const strengthBars = document.querySelectorAll("#strength span");

    // --- Função de cálculo de força da senha (igual ao do cliente) ---
    function calculatePasswordScore(val) {
        let score = 0;
        if (val.length >= 8) score++;
        if (/[A-Z]/.test(val) && /[a-z]/.test(val)) score++;
        if (/\d/.test(val)) score++;
        if (/[^A-Za-z0-9]/.test(val)) score++;
        return score;
    }

    // --- Atualiza as barrinhas visualmente ---
    function updateStrength() {
        if (!strengthBars.length) return;
        const score = calculatePasswordScore(senhaInput.value);
        strengthBars.forEach((bar, index) => {
            bar.style.background = index < score ? "var(--primary)" : "var(--border)";
        });
    }

    // Ouve as digitações no campo de senha para atualizar a força em tempo real
    if (senhaInput) {
        senhaInput.addEventListener("input", updateStrength);
    }

    // --- Funcionalidade para alternar a visualização da senha (Olho) ---
    // Dica: adicione botões com os IDs 'toggle-senha' e 'toggle-confirmar' no seu HTML se quiser esse recurso
    function setupTogglePassword(toggleId, inputElement) {
        const toggleBtn = document.getElementById(toggleId);
        if (toggleBtn && inputElement) {
            toggleBtn.addEventListener('click', () => {
                const type = inputElement.getAttribute('type') === 'password' ? 'text' : 'password';
                inputElement.setAttribute('type', type);
                // Opcional: mudar o ícone/texto do botão aqui se desejar
            });
        }
    }

    setupTogglePassword('toggle-senha', senhaInput);
    setupTogglePassword('toggle-confirmar', confirmarSenhaInput);

    // --- Validação no Envio do Formulário ---
    if (form) {
        form.addEventListener('submit', (e) => {
            // Validação de correspondência das senhas
            if (senhaInput.value !== confirmarSenhaInput.value) {
                e.preventDefault(); // Impede o envio do formulário no Flask
                alert('As senhas digitadas não correspondem. Por favor, verifique.');
                confirmarSenhaInput.focus();
                return;
            }

            // Opcional: Exigir senha com pontuação mínima (ex: score mínimo 2 ou 3)
            const score = calculatePasswordScore(senhaInput.value);
            if (score < 2) {
                e.preventDefault();
                alert('A senha é muito fraca. Por favor, inclua letras maiúsculas, números ou caracteres especiais.');
                senhaInput.focus();
                return;
            }

            // Caso tudo esteja correto, o formulário segue para o backend
        });
    }
});