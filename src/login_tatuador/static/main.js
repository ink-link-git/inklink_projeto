document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('.login-form');
    const email = document.querySelector('#email');
    const password = document.querySelector('#password');

    if (!form) return;

    // Função auxiliar para definir erro ou limpar
    const setCampoErro = (input, mensagem) => {
        const errorMsg = input.closest('.form-group').querySelector('.error-msg');
        if (errorMsg) errorMsg.textContent = mensagem;
        input.style.borderColor = mensagem ? '#FF4D4D' : '#2A2A2A';
    };

    // Limpa a mensagem ao digitar
    [email, password].forEach(input => {
        input.addEventListener('input', () => setCampoErro(input, ''));
    });

    // Validação no envio
    form.addEventListener('submit', (e) => {
        let valido = true;

        if (!email.value.trim()) {
            setCampoErro(email, 'Por favor, informe seu e-mail.');
            valido = false;
        } else if (!email.checkValidity()) { // Usa a validação nativa de e-mail do HTML
            setCampoErro(email, 'Informe um e-mail válido.');
            valido = false;
        }

        if (!password.value.trim()) {
            setCampoErro(password, 'Por favor, informe sua senha.');
            valido = false;
        }

        if (!valido) e.preventDefault();
    });
});