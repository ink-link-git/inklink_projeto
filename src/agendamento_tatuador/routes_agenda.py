from flask import Blueprint, render_template, redirect, url_for, request
from db_agenda import supabase

agenda_bp = Blueprint('agenda', __name__)

@agenda_bp.route('/')
@agenda_bp.route('/agenda')
def minha_agenda():
    # Consulta ordenada pela coluna correta 'data_hora'
    resposta = supabase.table('agendamento').select('*').order('data_hora', desc=False).execute()
    agendamentos = resposta.data
    return render_template('agenda.html', agendamentos=agendamentos)

@agenda_bp.route('/confirmar/<int:id_agendamento>', methods=['POST'])
def confirmar(id_agendamento):
    # Usa a coluna 'id' correta
    supabase.table('agendamento').update({'status': 'CONFIRMADO'}).eq('id', id_agendamento).execute()
    return redirect(url_for('agenda.minha_agenda'))

@agenda_bp.route('/remover/<int:id_agendamento>', methods=['POST'])
def remover(id_agendamento):
    # Usa a coluna 'id' correta
    supabase.table('agendamento').update({'status': 'CANCELADO'}).eq('id', id_agendamento).execute()
    return redirect(url_for('agenda.minha_agenda'))

# Rota de Reagendar
@agenda_bp.route('/reagendar/<int:id_agendamento>', methods=['POST'])
def reagendar(id_agendamento):
    nova_data_hora = request.form.get('data_hora')

    if nova_data_hora:
        supabase.table('agendamento').update({
            'data_hora': nova_data_hora,
            'status': 'PENDENTE'
        }).eq('id', id_agendamento).execute()

    return redirect(url_for('agenda.minha_agenda'))