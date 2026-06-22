function agendar() {
    const nome = document.getElementById('nome').value;
    const data = document.getElementById('data').value;
    const hora = document.getElementById('hora').value;

    if (!nome || !data || !hora) {
        alert("Preencha todos os campos");
        return;
    }

    const lista = document.getElementById('lista');
    const item = document.createElement('p');
    
    // USANDO CRASES AQUI:
    item.textContent = `${nome} agendou para ${data} às ${hora}`;
    
    lista.appendChild(item);

    // Limpar campos
    document.getElementById('nome').value = '';
    document.getElementById('data').value = '';
    document.getElementById('hora').value = '';
}