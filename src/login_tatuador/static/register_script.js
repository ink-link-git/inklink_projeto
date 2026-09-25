document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('registerForm');
    const senhaInput = document.getElementById('senha');
    const confirmarSenhaInput = document.getElementById('confirmar-senha');

    form.addEventListener('submit', (e) => {
        // Validação de correspondência das senhas
        if (senhaInput.value !== confirmarSenhaInput.value) {
            e.preventDefault(); // Impede o envio do formulário no Flask
            alert('As senhas digitadas não correspondem. Por favor, verifique.');
            confirmarSenhaInput.focus();
            return;
        }

        // Caso as senhas sejam iguais, o formulário segue para o backend (routes.py)
    });
});