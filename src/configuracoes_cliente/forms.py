import time

from configuracoes_cliente.db import trocar_senha

MIN_SENHA = 8

# Limite simples de tentativas por cliente (em memória): evita ficar
# testando senhas atuais em sequência.
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


def _recentes(cliente_id):
    agora = time.time()
    lista = [t for t in _tentativas.get(cliente_id, []) if agora - t < JANELA_SEGUNDOS]
    _tentativas[cliente_id] = lista
    return lista


def alterar_senha_do_cliente(cliente_id, email, data):
    """Retorna (ok, errors, status)."""
    atual = data.get("atual") or ""
    nova = data.get("nova") or ""
    confirmar = data.get("confirmar") or ""

    errors = validar_troca_senha(atual, nova, confirmar)
    if errors:
        return False, errors, 400

    if len(_recentes(cliente_id)) >= MAX_TENTATIVAS:
        return False, {"geral": "Muitas tentativas. Aguarde alguns minutos e tente de novo."}, 429

    ok, motivo = trocar_senha(email, atual, nova)
    if not ok:
        _tentativas[cliente_id].append(time.time())
        return False, {"atual": "Senha atual incorreta."}, 400

    _tentativas.pop(cliente_id, None)
    return True, {}, 200


# Perguntas da tela de Ajuda (regras reais do sistema).
FAQ = [
    {
        "pergunta": "Como agendo uma sessão?",
        "resposta": "Abra Agendamentos, escolha o tatuador, o dia e o horário, descreva a tatuagem "
                    "e envie. Você pode anexar até 4 imagens de referência (JPG, PNG, WEBP ou GIF, "
                    "até 5 MB cada).",
    },
    {
        "pergunta": "Posso cancelar um agendamento?",
        "resposta": "Sim. Em Agendamentos, use a opção de cancelar na sessão desejada. Sessões que "
                    "já foram concluídas ou canceladas não podem mais ser alteradas.",
    },
    {
        "pergunta": "O que é a ficha de anamnese?",
        "resposta": "É um questionário de saúde que o tatuador usa para sua segurança. Ela é preenchida "
                    "uma vez por agendamento — depois de enviada, não pode ser preenchida de novo.",
    },
    {
        "pergunta": "Como altero minha senha?",
        "resposta": "Em Configurações, toque em Alterar senha, informe a senha atual e escolha uma nova "
                    "com no mínimo 8 caracteres.",
    },
    {
        "pergunta": "Esqueci minha senha. E agora?",
        "resposta": "Se você ainda está logado, use Alterar senha. Se não conseguir entrar, fale com "
                    "o suporte pelo e-mail indicado nesta página.",
    },
    {
        "pergunta": "Como saio da minha conta?",
        "resposta": "Em Configurações, toque em Sair da conta. Em computadores compartilhados, "
                    "sempre encerre a sessão ao terminar.",
    },
]
