document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById('registerForm');
    const senhaInput = document.getElementById('password');
    const confirmarSenhaInput = document.getElementById('confirm');
    const erroConfirmar = document.getElementById('erro-confirm');

    // 1. MÁSCARA DE CPF (000.000.000-00)
    const cpfInput = document.querySelector("#cpf");
    if (cpfInput) {
        cpfInput.addEventListener("input", (e) => {
            let value = e.target.value.replace(/\D/g, ""); // Remove tudo que não for número
            if (value.length > 11) value = value.slice(0, 11);
            
            value = value.replace(/(\d{3})(\d)/, "$1.$2");
            value = value.replace(/(\d{3})(\d)/, "$1.$2");
            value = value.replace(/(\d{3})(\d{1,2})$/, "$1-$2");
            
            e.target.value = value;
        });
    }

    // 2. MÁSCARA DE TELEFONE ((00) 00000-0000)
    const telInput = document.querySelector("#tel");
    if (telInput) {
        telInput.addEventListener("input", (e) => {
            let value = e.target.value.replace(/\D/g, "");
            if (value.length > 11) value = value.slice(0, 11);
            
            value = value.replace(/^(\d{2})(\d)/g, "($1) $2");
            value = value.replace(/(\d{5})(\d{4})$/, "$1-$2");
            
            e.target.value = value;
        });
    }

    // 3. MEDIDOR DE FORÇA DE SENHA
    const bars = document.querySelectorAll(".strength-bars .bar");
    const strengthText = document.querySelector("#strength-text");

    if (senhaInput) {
        senhaInput.addEventListener("input", (e) => {
            const val = e.target.value;
            let score = 0;

            // Critérios de pontuação
            if (val.length >= 6) score++;
            if (/[A-Z]/.test(val)) score++;
            if (/[0-9]/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++; // Caractere especial aumenta a força

            const colors = ["#ff4d4d", "#ffa500", "#ffd700", "#2ecc71"];
            const texts = ["Muito fraca", "Fraca", "Média", "Forte"];

            bars.forEach((bar, index) => {
                if (index < score && val.length > 0) {
                    bar.style.background = colors[score - 1];
                } else {
                    bar.style.background = "#333"; // Cor apagada
                }
            });

            if (val.length > 0) {
                strengthText.textContent = texts[score - 1] || "Muito fraca";
                strengthText.style.color = colors[score - 1] || "#ff4d4d";
            } else {
                strengthText.textContent = "Digite uma senha segura";
                strengthText.style.color = "#aaa";
            }
        });
    }

    // Se o formulário não existir na página, encerra por aqui
    if (!form) return;

    // Limpa a mensagem de erro quando a pessoa volta a digitar na confirmação
    if (confirmarSenhaInput && erroConfirmar) {
        confirmarSenhaInput.addEventListener('input', () => {
            erroConfirmar.textContent = '';
        });
    }

    // 4. VALIDAÇÃO DE ENVIO DO FORMULÁRIO
    form.addEventListener('submit', (e) => {
        if (senhaInput && confirmarSenhaInput) {
            // Validação de correspondência das senhas
            if (senhaInput.value !== confirmarSenhaInput.value) {
                e.preventDefault(); // Impede o envio do formulário no Flask
                if (erroConfirmar) {
                    erroConfirmar.textContent = 'As senhas digitadas não correspondem. Por favor, verifique.';
                }
                confirmarSenhaInput.focus();
                return;
            }
        }
        // Caso as senhas sejam iguais, o formulário segue para o backend (routes.py)
    });
});