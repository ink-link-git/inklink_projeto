document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-perfil');
    const btnEditar = document.getElementById('btn-editar');
    const btnSalvar = document.getElementById('btn-salvar');
    const btnCancelar = document.getElementById('btn-cancelar');
    
    const campoFoto = document.getElementById('campo-foto-container');
    const inputFoto = document.getElementById('foto_perfil');
    const msgPerfil = document.getElementById('msg-perfil');
    
    const inputsEditaveis = [
        document.getElementById('nome'),
        document.getElementById('telefone'),
        document.getElementById('endereco')
    ];

    if (!form || !btnEditar) return;

    // Garante que todos começam desabilitados e impossíveis de clicar
    inputsEditaveis.forEach(input => {
        if (input) input.disabled = true;
    });

    let valoresOriginais = {};

    // Pré-visualização da foto ao selecionar um arquivo novo
    if (inputFoto) {
        inputFoto.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const avatarContainer = document.getElementById('perfil-avatar');
                    let img = avatarContainer.querySelector('img');
                    if (!img) {
                        avatarContainer.innerHTML = '';
                        img = document.createElement('img');
                        img.className = 'perfil-img-avatar';
                        avatarContainer.appendChild(img);
                    }
                    img.src = event.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    }

    // Ao clicar em "Editar perfil", destrava tudo
    btnEditar.addEventListener('click', () => {
        form.classList.add('editando');
        if (msgPerfil) msgPerfil.textContent = '';
        
        inputsEditaveis.forEach(input => {
            if (input) {
                valoresOriginais[input.id] = input.value;
                input.disabled = false; // Libera o campo para edição
            }
        });

        if (campoFoto) campoFoto.style.display = 'flex';

        btnEditar.hidden = true;
        btnSalvar.hidden = false;
        btnCancelar.hidden = false;
        
        if (inputsEditaveis[0]) inputsEditaveis[0].focus();
    });

    // Ao clicar em "Cancelar", volta os valores e trava tudo de novo
    btnCancelar.addEventListener('click', () => {
        form.classList.remove('editando');
        if (msgPerfil) msgPerfil.textContent = '';

        inputsEditaveis.forEach(input => {
            if (input) {
                input.value = valoresOriginais[input.id] || '';
                input.disabled = true; // Bloqueia o campo novamente
            }
        });

        if (campoFoto) {
            campoFoto.style.display = 'none';
            if (inputFoto) inputFoto.value = ''; // Limpa o input file
        }

        btnEditar.hidden = false;
        btnSalvar.hidden = true;
        btnCancelar.hidden = true;
    });

    // Envio do formulário via AJAX para salvar no banco e Supabase
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (msgPerfil) {
            msgPerfil.textContent = 'Salvando alterações...';
            msgPerfil.style.color = '#fff';
        }

        // Habilita temporariamente os inputs para o FormData conseguir capturar os valores
        inputsEditaveis.forEach(input => { if (input) input.disabled = false; });
        const formData = new FormData(form);
        // Trava de novo enquanto envia
        inputsEditaveis.forEach(input => { if (input) input.disabled = true; });

        try {
            const response = await fetch('/api/tatuador/perfil', {
                method: 'PATCH',
                body: formData
            });

            const resultado = await response.json();

            if (response.ok && resultado.success) {
                if (msgPerfil) {
                    msgPerfil.textContent = resultado.message || 'Perfil atualizado com sucesso!';
                    msgPerfil.style.color = '#4BB543';
                }

                // Atualiza o nome exibido no título do perfil se houver
                const tituloNome = document.getElementById('perfil-nome-titulo');
                if (tituloNome && resultado.perfil.nome) {
                    tituloNome.textContent = resultado.perfil.nome;
                }

                // Esconde controles de edição e volta aos botões normais
                form.classList.remove('editando');
                if (campoFoto) campoFoto.style.display = 'none';
                btnEditar.hidden = false;
                btnSalvar.hidden = true;
                btnCancelar.hidden = true;

                // Recarrega a página após 1 segundo para atualizar a sessão e a foto do sidebar perfeitamente
                setTimeout(() => {
                    window.location.reload();
                }, 1000);

            } else {
                // Se houver erros de validação
                inputsEditaveis.forEach(input => { if (input) input.disabled = false; }); // destrava para corrigir
                if (msgPerfil) {
                    msgPerfil.textContent = resultado.errors?.geral || 'Verifique os campos e tente novamente.';
                    msgPerfil.style.color = '#D31235';
                }
            }
        } catch (error) {
            console.error('Erro na requisição:', error);
            inputsEditaveis.forEach(input => { if (input) input.disabled = false; });
            if (msgPerfil) {
                msgPerfil.textContent = 'Erro de conexão ao salvar alterações.';
                msgPerfil.style.color = '#D31235';
            }
        }
    });
});