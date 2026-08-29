"""Configuração e o pouco de estado que o planopt guarda.

O estado existe por um motivo só: **o gancho não sabe em que modelo a sessão
está.** Nenhum campo de entrada de gancho do Claude Code carrega o modelo, e não
existe `$CLAUDE_MODEL`. Quem recebe isso é o script de linha de status, que roda
a cada quadro e ganha `model.id` — e, em plano Pro/Max, a porcentagem gasta da
janela de cinco horas.

Então a linha de status escreve, e o gancho lê. É a única ponte gratuita entre
os dois, e é por isso que ela existe.
"""

import json
import os
import tempfile
import time

CASA = os.environ.get("PLANOPT_HOME") or os.path.expanduser("~/.claude-plan-optimizer")
CONFIG = os.path.join(CASA, "config.json")
SESSOES = os.path.join(CASA, "sessoes")
DIARIO = os.path.join(CASA, "diario.jsonl")

MODOS = ("aviso", "guarda", "mudo")
MODO_PADRAO = "aviso"

# Sessão parada há mais de meia hora não diz nada sobre o agora.
VALIDADE_SESSAO = 30 * 60


def _garante(caminho):
    try:
        os.makedirs(caminho, exist_ok=True)
    except OSError:
        pass


def _grava_atomico(caminho, dados):
    """Escreve inteiro ou não escreve.

    A linha de status roda a cada quadro e o gancho lê a qualquer momento: sem
    troca atômica, o gancho leria JSON pela metade e cairia calado — que é o
    pior modo de falhar, porque some sem deixar rastro.
    """
    _garante(os.path.dirname(caminho))
    try:
        fd, temporario = tempfile.mkstemp(dir=os.path.dirname(caminho), prefix=".planopt.")
        with os.fdopen(fd, "w", encoding="utf-8") as arquivo:
            json.dump(dados, arquivo, ensure_ascii=False, indent=1)
        os.replace(temporario, caminho)
        return True
    except OSError:
        return False


def ler_config():
    try:
        with open(CONFIG, encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
        return dados if isinstance(dados, dict) else {}
    except (OSError, ValueError):
        return {}


def gravar_config(**campos):
    dados = ler_config()
    dados.update(campos)
    _grava_atomico(CONFIG, dados)
    return dados


def modo():
    valor = os.environ.get("PLANOPT_MODO") or ler_config().get("modo") or MODO_PADRAO
    return valor if valor in MODOS else MODO_PADRAO


# ----------------------------------------------------------------- sessões ---
def _caminho_sessao(sessao):
    seguro = "".join(c for c in (sessao or "sem-id") if c.isalnum() or c in "-_")[:80]
    return os.path.join(SESSOES, (seguro or "sem-id") + ".json")


def anotar_sessao(sessao, modelo_id=None, modelo_nome=None,
                  cinco_horas=None, sete_dias=None, reseta_em=None):
    """Chamado pela linha de status, a cada quadro."""
    dados = {
        "sessao": sessao,
        "modelo_id": modelo_id or "",
        "modelo_nome": modelo_nome or "",
        "cinco_horas": cinco_horas,
        "sete_dias": sete_dias,
        "reseta_em": reseta_em,
        "em": int(time.time()),
    }
    _grava_atomico(_caminho_sessao(sessao), dados)
    return dados


def ler_sessao(sessao):
    """O que a linha de status viu por último. ``None`` quando está velho.

    Devolver dado velho seria pior que devolver nada: o gancho decidiria com
    base num modelo que já foi trocado, e interromperia sem razão.
    """
    try:
        with open(_caminho_sessao(sessao), encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, ValueError):
        return None
    if not isinstance(dados, dict):
        return None
    if time.time() - (dados.get("em") or 0) > VALIDADE_SESSAO:
        return None
    return dados


def limpar_sessoes(idade=7 * 24 * 3600):
    """Sessão velha não serve para nada e nunca é apagada sozinha pelo sistema."""
    _garante(SESSOES)
    agora = time.time()
    removidas = 0
    try:
        for nome in os.listdir(SESSOES):
            caminho = os.path.join(SESSOES, nome)
            try:
                if agora - os.path.getmtime(caminho) > idade:
                    os.remove(caminho)
                    removidas += 1
            except OSError:
                continue
    except OSError:
        pass
    return removidas


# ------------------------------------------------------------------ diário ---
def anotar(evento):
    """Uma linha por decisão, para dar para medir depois se valeu a pena.

    Fica na máquina e só guarda o que serve para medir: faixa, pontos, modelo.
    O texto do pedido nunca entra — é o que a pessoa digitou, e um roteador não
    tem por que guardar isso em lugar nenhum.
    """
    if not ler_config().get("diario", True):
        return False
    _garante(CASA)
    evento = dict(evento)
    evento["em"] = int(time.time())
    evento.pop("texto", None)
    evento.pop("pedido", None)
    try:
        with open(DIARIO, "a", encoding="utf-8") as arquivo:
            arquivo.write(json.dumps(evento, ensure_ascii=False) + "\n")
        return True
    except OSError:
        return False
