// Estado da aplicação
const state = {
    selectedDate: null,
    selectedTime: null,
    skinTone: null,
    hasAnamnesis: false,
    currentMonth: new Date().getMonth(),
    currentYear: new Date().getFullYear()
};

// Datas disponíveis
const availableDates = [
    new Date(2026, 3, 22),
    new Date(2026, 3, 23),
    new Date(2026, 3, 25),
    new Date(2026, 3, 28),
    new Date(2026, 3, 29),
    new Date(2026, 3, 30),
    new Date(2026, 4, 2),
    new Date(2026, 4, 5),
    new Date(2026, 4, 6)
];

// Horários disponíveis
const availableTimes = ['10:00', '11:00', '14:00', '15:00', '16:00', '17:00'];

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    initCalendar();
    initSkinToneButtons();
    initAnamnesisModal();
    initFormValidation();
});

// Calendário
function initCalendar() {
    renderCalendar();
}

function renderCalendar() {
    const calendarEl = document.getElementById('calendar');
    const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                        'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const weekDays = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb'];

    const firstDay = new Date(state.currentYear, state.currentMonth, 1);
    const lastDay = new Date(state.currentYear, state.currentMonth + 1, 0);
    const prevLastDay = new Date(state.currentYear, state.currentMonth, 0);

    const firstDayIndex = firstDay.getDay();
    const lastDayDate = lastDay.getDate();
    const prevLastDayDate = prevLastDay.getDate();
    const nextDays = 7 - lastDay.getDay() - 1;

    let calendarHTML = `
        <div class="calendar-header">
            <button type="button" class="calendar-nav" onclick="changeMonth(-1)">‹</button>
            <span>${monthNames[state.currentMonth]} ${state.currentYear}</span>
            <button type="button" class="calendar-nav" onclick="changeMonth(1)">›</button>
        </div>
        <div class="calendar-weekdays">
            ${weekDays.map(day => `<div class="calendar-weekday">${day}</div>`).join('')}
        </div>
        <div class="calendar-days">
    `;

    // Dias do mês anterior
    for (let x = firstDayIndex; x > 0; x--) {
        calendarHTML += `<div class="calendar-day other-month">${prevLastDayDate - x + 1}</div>`;
    }

    // Dias do mês atual
    for (let day = 1; day <= lastDayDate; day++) {
        const currentDate = new Date(state.currentYear, state.currentMonth, day);
        const isAvailable = availableDates.some(d =>
            d.getDate() === day &&
            d.getMonth() === state.currentMonth &&
            d.getFullYear() === state.currentYear
        );

        const isSelected = state.selectedDate &&
            state.selectedDate.getDate() === day &&
            state.selectedDate.getMonth() === state.currentMonth &&
            state.selectedDate.getFullYear() === state.currentYear;

        let classes = 'calendar-day';
        if (isAvailable) classes += ' available';
        if (isSelected) classes += ' selected';

        const onclick = isAvailable ? `onclick="selectDate(${day}, ${state.currentMonth}, ${state.currentYear})"` : '';

        calendarHTML += `<div class="${classes}" ${onclick}>${day}</div>`;
    }

    // Dias do próximo mês
    for (let day = 1; day <= nextDays; day++) {
        calendarHTML += `<div class="calendar-day other-month">${day}</div>`;
    }

    calendarHTML += '</div>';
    calendarEl.innerHTML = calendarHTML;
}

function changeMonth(direction) {
    state.currentMonth += direction;

    if (state.currentMonth > 11) {
        state.currentMonth = 0;
        state.currentYear++;
    } else if (state.currentMonth < 0) {
        state.currentMonth = 11;
        state.currentYear--;
    }

    renderCalendar();
}

function selectDate(day, month, year) {
    state.selectedDate = new Date(year, month, day);
    state.selectedTime = null;
    renderCalendar();
    showTimeSlots();
    updateSubmitButton();
}

function showTimeSlots() {
    const timeSlotsEl = document.getElementById('timeSlots');
    const timeGridEl = document.getElementById('timeGrid');

    timeSlotsEl.classList.remove('hidden');

    timeGridEl.innerHTML = availableTimes.map(time => `
        <button type="button" class="time-btn" onclick="selectTime('${time}')">
            ${time}
        </button>
    `).join('');
}

function selectTime(time) {
    state.selectedTime = time;

    // Atualizar visual dos botões
    document.querySelectorAll('.time-btn').forEach(btn => {
        if (btn.textContent.trim() === time) {
            btn.classList.add('selected');
        } else {
            btn.classList.remove('selected');
        }
    });

    updateSubmitButton();
}

// Seleção de tom de pele
function initSkinToneButtons() {
    const buttons = document.querySelectorAll('.skin-tone-btn');

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const value = btn.getAttribute('data-value');
            state.skinTone = value;
            document.getElementById('skinTone').value = value;

            buttons.forEach(b => b.classList.remove('selected'));
            btn.classList.add('selected');

            updateSubmitButton();
        });
    });
}

// Modal de Anamnese
function initAnamnesisModal() {
    const modal = document.getElementById('anamnesisModal');
    const fillBtn = document.getElementById('fillAnamnesisBtn');
    const closeBtn = document.getElementById('closeModal');
    const cancelBtn = document.getElementById('cancelAnamnesis');
    const form = document.getElementById('anamnesisForm');
    const checkbox = document.getElementById('hasAnamnesis');

    // Mostrar/esconder botão de preencher
    checkbox.addEventListener('change', (e) => {
        state.hasAnamnesis = e.target.checked;
        fillBtn.style.display = e.target.checked ? 'none' : 'block';
        updateSubmitButton();
    });

    fillBtn.addEventListener('click', () => {
        modal.classList.remove('hidden');
    });

    closeBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    cancelBtn.addEventListener('click', () => {
        modal.classList.add('hidden');
    });

    form.addEventListener('submit', (e) => {
        e.preventDefault();
        state.hasAnamnesis = true;
        document.getElementById('hasAnamnesis').checked = true;
        fillBtn.style.display = 'none';
        modal.classList.add('hidden');
        alert('Ficha de anamnese preenchida com sucesso!');
        updateSubmitButton();
    });

    // Fechar modal ao clicar fora
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.add('hidden');
        }
    });

    // Lógica para checkbox "Nenhuma" nas condições de saúde
    const healthCheckboxes = document.querySelectorAll('input[name="health"]');
    healthCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', (e) => {
            if (e.target.value === 'Nenhuma' && e.target.checked) {
                healthCheckboxes.forEach(cb => {
                    if (cb.value !== 'Nenhuma') cb.checked = false;
                });
            } else if (e.target.checked && e.target.value !== 'Nenhuma') {
                healthCheckboxes.forEach(cb => {
                    if (cb.value === 'Nenhuma') cb.checked = false;
                });
            }
        });
    });
}

// Validação do formulário
function initFormValidation() {
    const form = document.getElementById('appointmentForm');

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const phone = document.getElementById('phone').value;
        const description = document.getElementById('description').value;

        if (state.selectedDate && state.selectedTime && state.skinTone && state.hasAnamnesis) {
            const dateStr = formatDate(state.selectedDate);
            alert(`Agendamento solicitado para ${dateStr} às ${state.selectedTime}\n\nNome: ${name}\nEmail: ${email}`);

            // Aqui você pode enviar os dados para um servidor
            console.log({
                date: state.selectedDate,
                time: state.selectedTime,
                name,
                email,
                phone,
                skinTone: state.skinTone,
                description,
                hasAnamnesis: state.hasAnamnesis
            });
        }
    });
}

function updateSubmitButton() {
    const submitBtn = document.getElementById('submitBtn');
    const isValid = state.selectedDate &&
                   state.selectedTime &&
                   state.skinTone &&
                   state.hasAnamnesis;

    submitBtn.disabled = !isValid;
}

function formatDate(date) {
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
}
