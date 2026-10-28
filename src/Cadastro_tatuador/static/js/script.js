document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    const senhaInput = document.getElementById('password');
    const confirmarSenhaInput = document.getElementById('confirm');
    const erroConfirmar = document.getElementById('erro-confirm');

    if (!form) return;

    // Limpa a mensagem quando a pessoa volta a digitar
    confirmarSenhaInput.addEventListener('input', () => {
        erroConfirmar.textContent = '';
    });

    form.addEventListener('submit', (e) => {
        // Validação de correspondência das senhas
        if (senhaInput.value !== confirmarSenhaInput.value) {
            e.preventDefault(); // Impede o envio do formulário no Flask
            erroConfirmar.textContent = 'As senhas digitadas não correspondem. Por favor, verifique.';
            confirmarSenhaInput.focus();
            return;
        }

        // Caso as senhas sejam iguais, o formulário segue para o backend (routes.py)
    });
});
