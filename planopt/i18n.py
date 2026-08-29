"""Português e inglês desde a primeira linha impressa.

O idioma do sistema decide o padrão, ``PLANOPT_LANG`` força, e a escolha
gravada em ``~/.claude-plan-optimizer/config.json`` ganha do sistema. A ordem é
essa porque um Mac configurado em inglês não quer dizer que a pessoa queira a
ferramenta em inglês.
"""

import json
import locale
import os

_IDIOMAS = ("pt", "en")
_PADRAO = "pt"

TEXTOS = {
    "pt": {
        "tier.trivial": "trivial",
        "tier.barata": "barata",
        "tier.media": "média",
        "tier.cara": "cara",
        "tier.continuacao": "continuação",

        "aplicacao.obrigatorio": "vale",
        "aplicacao.conselho": "conselho",

        "res.continuacao": "Continuação: mantém o que já estava valendo.",
        "res.vazio": "Nada para classificar.",
        "res.tier": "Faixa: %s",
        "res.escolha": "Escolha: %s",
        "res.confianca_baixa": "em cima do corte — confira antes de confiar",
        "res.por_que": "Por quê:",
        "res.sem_faixa": "Este alvo não atende essa faixa — procure outro agente.",

        "hook.trivial": (
            "[planopt] Este pedido é %s. Não gaste modelo grande nele: "
            "faça direto, e se for delegar, %s. "
            "Motivo: %s."
        ),
        "hook.cara": (
            "[planopt] Este pedido é %s. Vale o modelo forte e esforço alto — "
            "e vale dividir antes de começar. Motivo: %s."
        ),
        "hook.continuacao": (
            "[planopt] Continuação: o custo é o da tarefa em curso, "
            "não o desta mensagem. Não mude de modelo por causa dela."
        ),
        "hook.opus_em_trivial": (
            "[planopt] A sessão está em %s e este pedido é %s. "
            "Isso é o desperdício que o planopt existe para evitar: "
            "resolva sem gastar raciocínio caro, ou troque com /model %s."
        ),

        "cli.uso": "uso: planopt <comando> [argumentos]",
        "cli.desconhecido": "comando desconhecido: %s",
        "cli.sem_texto": "faltou o texto do pedido (ou passe pela entrada padrão)",
        "cli.alvo_desconhecido": "alvo desconhecido: %s",
        "cli.alvos": "alvos conhecidos: %s",
        "cli.modo_atual": "modo atual: %s",
        "cli.modo_mudou": "modo agora é: %s",
        "cli.idioma_atual": "idioma atual: %s",
        "cli.idioma_mudou": "idioma agora é: %s",

        "modo.aviso": "aviso — opina, nunca interrompe",
        "modo.guarda": "guarda — opina, e interrompe só quando modelo caro encontra tarefa barata",
        "modo.mudo": "mudo — classifica e anota, não fala nada",
    },
    "en": {
        "tier.trivial": "trivial",
        "tier.barata": "cheap",
        "tier.media": "medium",
        "tier.cara": "expensive",
        "tier.continuacao": "continuation",

        "aplicacao.obrigatorio": "enforced",
        "aplicacao.conselho": "advisory",

        "res.continuacao": "Continuation: keep whatever was already in force.",
        "res.vazio": "Nothing to classify.",
        "res.tier": "Tier: %s",
        "res.escolha": "Pick: %s",
        "res.confianca_baixa": "right on the boundary — check before trusting it",
        "res.por_que": "Why:",
        "res.sem_faixa": "This target does not serve that tier — pick another agent.",

        "hook.trivial": (
            "[planopt] This request is %s. Do not spend a big model on it: "
            "just do it, and if you delegate, %s. "
            "Reason: %s."
        ),
        "hook.cara": (
            "[planopt] This request is %s. It earns the strong model at high "
            "effort — and it earns being split before you start. Reason: %s."
        ),
        "hook.continuacao": (
            "[planopt] Continuation: the cost is the running task's, not this "
            "message's. Do not switch models because of it."
        ),
        "hook.opus_em_trivial": (
            "[planopt] The session is on %s and this request is %s. "
            "That is the waste planopt exists to prevent: "
            "handle it without expensive reasoning, or switch with /model %s."
        ),

        "cli.uso": "usage: planopt <command> [arguments]",
        "cli.desconhecido": "unknown command: %s",
        "cli.sem_texto": "missing the request text (or pipe it on stdin)",
        "cli.alvo_desconhecido": "unknown target: %s",
        "cli.alvos": "known targets: %s",
        "cli.modo_atual": "current mode: %s",
        "cli.modo_mudou": "mode is now: %s",
        "cli.idioma_atual": "current language: %s",
        "cli.idioma_mudou": "language is now: %s",

        "modo.aviso": "advise — speaks up, never interrupts",
        "modo.guarda": "guard — speaks up, and interrupts only when an expensive model meets a cheap task",
        "modo.mudo": "quiet — classifies and records, says nothing",
    },
}


def _do_sistema():
    for var in ("LC_ALL", "LC_MESSAGES", "LANG"):
        valor = os.environ.get(var) or ""
        if valor[:2].lower() in _IDIOMAS:
            return valor[:2].lower()
    try:
        codigo = (locale.getlocale()[0] or "")[:2].lower()
    except (ValueError, TypeError):
        codigo = ""
    return codigo if codigo in _IDIOMAS else _PADRAO


def idioma(config=None):
    """Ordem: variável de ambiente, escolha gravada, idioma do sistema."""
    forcado = (os.environ.get("PLANOPT_LANG") or "")[:2].lower()
    if forcado in _IDIOMAS:
        return forcado
    if config:
        gravado = (config.get("idioma") or "")[:2].lower()
        if gravado in _IDIOMAS:
            return gravado
    return _do_sistema()


def t(chave, *args, lang=None, config=None):
    lang = lang or idioma(config)
    texto = TEXTOS.get(lang, TEXTOS[_PADRAO]).get(chave)
    if texto is None:
        texto = TEXTOS[_PADRAO].get(chave, chave)
    return texto % args if args else texto


def idiomas():
    return _IDIOMAS
