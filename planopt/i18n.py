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

        # motivo.*: os sinais que o classificador aponta em "explica"/"--json".
        # Ficam aqui, não em classificador.py, porque texto pronto embutido no
        # código é o mesmo jeito de nunca ter saído em inglês.
        "motivo.causa_oculta": "defeito sem causa conhecida — achar custa mais que consertar",
        "motivo.escopo_aberto": "escopo aberto — é varredura, não ponto",
        "motivo.escopo_aberto_marcas": "escopo aberto — é varredura, não ponto (%d marcas)",
        "motivo.varredura": "pede revisão ou auditoria",
        "motivo.decisao": "exige decisão de arquitetura ou escolha entre caminhos",
        "motivo.decisao_marcas": "exige decisão de arquitetura ou escolha entre caminhos (%d marcas)",
        "motivo.risco": "mexe com segredo, permissão, dinheiro ou produção",
        "motivo.desempenho": "desempenho: medir antes de mexer",
        "motivo.dominios_tres": "toca %d frentes diferentes (%s)",
        "motivo.dominios_duas": "toca duas frentes (%s)",
        "motivo.emendas": "vários pedidos emendados na mesma mensagem",
        "motivo.lista": "lista com %d itens",
        "motivo.briefing_muito_longo": "briefing muito longo",
        "motivo.briefing_longo": "briefing longo",
        "motivo.pede_obra": "pede obra, não conversa",
        "motivo.precisao": "já diz o arquivo, a linha ou o símbolo — não há o que procurar",
        "motivo.mecanico": "edição mecânica: a resposta está no próprio pedido",
        "motivo.pergunta": "é pergunta, não trabalho",
        "motivo.curto_demais": "pedido curto demais para conter tarefa",
        "motivo.sobe_por_seguranca": "em cima do corte — sobe de faixa por segurança",
        "motivo.saudacao": "saudação, sem tarefa",
        "motivo.manda_seguir": "manda seguir — o custo é o da tarefa em curso",

        # dominio.*: os rótulos que motivo.dominios_* junta numa lista. As
        # frentes técnicas (frontend, backend, docs, infra, mobile, i18n) são o
        # mesmo termo nas duas línguas; só "dados"/"teste" mudam para inglês.
        "dominio.frontend": "frontend",
        "dominio.backend": "backend",
        "dominio.data": "dados",
        "dominio.test": "teste",
        "dominio.docs": "docs",
        "dominio.infra": "infra",
        "dominio.mobile": "mobile",
        "dominio.i18n": "i18n",

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
        "hook.gratis": "  · sem gastar a conta medida: %s.",
        "hook.pressao_media": (
            "[planopt] A janela de uso está apertada e este pedido é média. "
            "Sonnet ainda vale se só o Claude resolve — mas dá pra tentar de "
            "graça primeiro. Motivo: %s."
        ),

        "res.sem_pressao": (
            "Sem telemetria ainda — a linha de status precisa rodar pelo "
            "menos um quadro nesta sessão."
        ),
        "res.pressao_normal": "Janela em %s%% (5h) / %s%% (7 dias) — folga.",
        "res.pressao_alerta": (
            "Janela em %s%% (5h) / %s%% (7 dias) — já compensa mandar as "
            "faixas baratas pro grátis."
        ),
        "res.pressao_critica": (
            "Janela em %s%% (5h) / %s%% (7 dias) — crítico: só o que só o "
            "Claude resolve fica na conta medida."
        ),
        "res.candidato_gratis": "  %-8s -> %-10s %s",

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

        "motivo.causa_oculta": "defect with no known cause — finding it costs more than fixing it",
        "motivo.escopo_aberto": "open scope — this is a sweep, not a point fix",
        "motivo.escopo_aberto_marcas": "open scope — this is a sweep, not a point fix (%d marks)",
        "motivo.varredura": "asks for a review or an audit",
        "motivo.decisao": "calls for an architecture decision or a choice between paths",
        "motivo.decisao_marcas": "calls for an architecture decision or a choice between paths (%d marks)",
        "motivo.risco": "touches a secret, a permission, money, or production",
        "motivo.desempenho": "performance: measure before touching anything",
        "motivo.dominios_tres": "touches %d different areas (%s)",
        "motivo.dominios_duas": "touches two areas (%s)",
        "motivo.emendas": "several requests stitched into one message",
        "motivo.lista": "a list with %d items",
        "motivo.briefing_muito_longo": "very long brief",
        "motivo.briefing_longo": "long brief",
        "motivo.pede_obra": "asks for work, not conversation",
        "motivo.precisao": "already names the file, the line, or the symbol — nothing to search for",
        "motivo.mecanico": "mechanical edit: the answer is inside the request itself",
        "motivo.pergunta": "it's a question, not work",
        "motivo.curto_demais": "too short to contain a task",
        "motivo.sobe_por_seguranca": "right on the boundary — bumps up a tier for safety",
        "motivo.saudacao": "greeting, no task",
        "motivo.manda_seguir": "keep going — the cost is the running task's",

        "dominio.frontend": "frontend",
        "dominio.backend": "backend",
        "dominio.data": "data",
        "dominio.test": "test",
        "dominio.docs": "docs",
        "dominio.infra": "infra",
        "dominio.mobile": "mobile",
        "dominio.i18n": "i18n",

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
        "hook.gratis": "  · without touching the metered account: %s.",
        "hook.pressao_media": (
            "[planopt] The usage window is tight and this request is medium. "
            "Sonnet still earns its place if only Claude can do it — but it's "
            "worth trying free first. Reason: %s."
        ),

        "res.sem_pressao": (
            "No telemetry yet — the status line needs to run at least one "
            "frame in this session."
        ),
        "res.pressao_normal": "Window at %s%% (5h) / %s%% (7 day) — plenty of room.",
        "res.pressao_alerta": (
            "Window at %s%% (5h) / %s%% (7 day) — already worth moving the "
            "cheap tiers to the free targets."
        ),
        "res.pressao_critica": (
            "Window at %s%% (5h) / %s%% (7 day) — critical: keep the metered "
            "account only for what only Claude can do."
        ),
        "res.candidato_gratis": "  %-8s -> %-10s %s",

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
