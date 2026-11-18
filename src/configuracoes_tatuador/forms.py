import time

from configuracoes_tatuador.db import trocar_senha

MIN_SENHA = 8

# Limite simples de tentativas por tatuador (em memória)
MAX_TENTATIVAS = 5
JANELA_SEGUNDOS = 10 * 60
_tentativas = {}


def validar_troca_senha(atual, nova, confirmar):
    errors = {}

    if not atual:
        errors["atual"] = "Informe sua senha atual."

    if len(nova) < MIN_SENHA:
        errors["nova"] = f"A nova senha precisa ter no mínimo {MIN_SENHA} caracteres."
    elif nova == atual:
        errors["nova"] = "A nova senha precisa ser diferente da atual."

    if nova != confirmar:
        errors["confirmar"] = "As senhas não coincidem."

    return errors


def _recentes(tatuador_id):
    agora = time.time()
    lista = [t for t in _tentativas.get(tatuador_id, []) if agora - t < JANELA_SEGUNDOS]
    _tentativas[tatuador_id] = lista
    return lista


def alterar_senha_do_tatuador(tatuador_id, email, data):
    """Retorna (ok, errors, status)."""
    atual = data.get("atual") or ""
    nova = data.get("nova") or ""
    confirmar = data.get("confirmar") or ""

    errors = validar_troca_senha(atual, nova, confirmar)
    if errors:
        return False, errors, 400

    if len(_recentes(tatuador_id)) >= MAX_TENTATIVAS:
        return False, {"geral": "Muitas tentativas. Aguarde alguns minutos e tente de novo."}, 429

    ok, motivo = trocar_senha(email, atual, nova)
    if not ok:
        _tentativas[tatuador_id].append(time.time())
        return False, {"atual": "Senha atual incorreta."}, 400

    _tentativas.pop(tatuador_id, None)
    return True, {}, 200


# Perguntas da tela de Ajuda voltada para o Tatuador.
FAQ = [
    {
        "pergunta": "Como gero ou atualizo meu portfólio?",
        "resposta": "Acesse a seção de Portfólio no painel para adicionar novas fotos de trabalhos realizados, removendo ou destacando suas melhores artes.",
    },
    {
        "pergunta": "Como funcionam os agendamentos dos clientes?",
        "resposta": "Você pode visualizar e gerenciar as solicitações de agendamento enviadas pelos clientes diretamente na sua aba de Agendamentos.",
    },
    {
        "pergunta": "O que é a ficha de anamnese do cliente?",
        "resposta": "É o questionário de saúde respondido pelo cliente antes da sessão. Fique atento às restrições informadas para garantir a segurança do procedimento.",
    },
    {
        "pergunta": "Como altero minha senha de acesso?",
        "resposta": "Vá em Configurações, selecione 'Alterar senha', digite sua senha atual e escolha uma nova com no mínimo 8 caracteres.",
    },
    {
        "pergunta": "Esqueci minha senha, o que fazer?",
        "resposta": "Se estiver logado, utilize a opção de alteração de senha nas configurações. Caso contrário, entre em contato com o suporte técnico do estúdio.",
    },
    {
        "pergunta": "Como encerro minha sessão no painel?",
        "resposta": "No menu de Configurações, clique em 'Sair da conta'. Lembre-se de sempre encerrar a sessão em computadores compartilhados.",
    },
]