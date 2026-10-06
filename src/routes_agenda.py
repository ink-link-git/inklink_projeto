from flask import Blueprint, render_template, redirect, url_for, request
from db_agenda import supabase

agenda_bp = Blueprint('agenda', __name__)

@agenda_bp.route('/')
@agenda_bp.route('/agenda')
def minha_agenda():
    resposta = supabase.table('agenda_tatuador').select('*').order('data_hora_inicio', desc=False).execute()
    agendamentos = resposta.data
    return render_template('agenda.html', agendamentos=agendamentos)

@agenda_bp.route('/confirmar/<int:id_agendamento>', methods=['POST'])
def confirmar(id_agendamento):
    supabase.table('agenda_tatuador').update({'status': 'CONFIRMADO'}).eq('id_agendamento', id_agendamento).execute()
    return redirect(url_for('agenda.minha_agenda'))

@agenda_bp.route('/remover/<int:id_agendamento>', methods=['POST'])
def remover(id_agendamento):
    supabase.table('agenda_tatuador').update({'status': 'CANCELADO'}).eq('id_agendamento', id_agendamento).execute()
    return redirect(url_for('agenda.minha_agenda'))

# Nova Rota: Reagendar Agendamento
@agenda_bp.route('/reagendar/<int:id_agendamento>', methods=['POST'])
def reagendar(id_agendamento):
    nova_data_inicio = request.form.get('data_hora_inicio')
    nova_data_fim = request.form.get('data_hora_fim')

    if nova_data_inicio and nova_data_fim:
        supabase.table('agenda_tatuador').update({
            'data_hora_inicio': nova_data_inicio,
            'data_hora_fim': nova_data_fim,
            'status': 'PENDENTE'  # Volta para pendente para o tatuador reconfirmar, se desejar
        }).eq('id_agendamento', id_agendamento).execute()

    return redirect(url_for('agenda.minha_agenda'))