"""Classifica um pedido em quanto modelo ele merece.

O princípio que manda em tudo aqui é a **assimetria**. Mandar tarefa fácil para
o modelo grande custa dinheiro; mandar tarefa difícil para o modelo pequeno
custa uma resposta errada que ninguém percebe na hora. Os dois erros não são
iguais, então o desempate nunca é para baixo.

O segundo princípio é que **continuação não se classifica**. "continua", "dale",
"testa ai" são 22% dos pedidos de um corpus real, e o texto deles não diz nada
sobre o custo: o trabalho é o que já estava rodando. Fingir que dá para ler o
custo em "dale" é a forma mais fácil de destruir uma sessão inteira — o pedido
mais barato de escrever pode ser a continuação da tarefa mais cara em curso.
"""

import re
import unicodedata

from . import lexico as lx

TIERS = ("trivial", "barata", "media", "cara")
_ORDEM = {t: i for i, t in enumerate(TIERS)}

# Onde cada faixa começa. Não é gosto: saiu de uma varredura sobre 120 pedidos
# reais rotulados, escolhendo os cortes onde o classificador pode se comprometer
# sem risco. Medido nesse corpus:
#
#   pontos <= 0  ->  23% dos pedidos, e NENHUM deles era caro de verdade
#   pontos >= 5  ->  25% dos pedidos, 83% mesmo caros ou médios
#   no meio      ->  52%, onde o texto não decide — e aí não se mexe em nada
#
# A faixa do meio existe de propósito. Um roteador que opina sobre tudo erra em
# tudo; este cala onde não sabe, e quem chama fica no que já estava valendo.
_CORTES = ((5, "cara"), (1, "media"), (-1, "barata"))

# Perto do corte, a classificação não é confiança — é sorte. Nessa faixa o
# desempate sobe de faixa, pela assimetria.
_MARGEM = 1


def _sem_acento(texto):
    normal = unicodedata.normalize("NFD", texto)
    return "".join(c for c in normal if unicodedata.category(c) != "Mn")


def _itens(texto):
    """Conta itens de lista: marcador, número no começo da linha, ou ponto e vírgula."""
    linhas = texto.splitlines()
    marcados = sum(1 for l in linhas if re.match(r"\s*(?:[-*•]|\d+[.)])\s+\S", l))
    return max(marcados, texto.count(";"))


def _dominios(texto):
    return [nome for nome, padrao in lx.DOMINIOS if padrao.search(texto)]


def _e_continuacao(texto, bruto):
    """Manda seguir em vez de descrever trabalho novo.

    Duas portas. A primeira é o reconhecimento nu — "." , "b", "nada", "pronyo",
    "foi ja?" — que não tem vocabulário para reconhecer, só tamanho e ausência:
    curto demais para caber tarefa, e sem nenhum verbo de obra. A segunda é a
    palavra de seguimento explícita.

    Em qualquer das duas, um verbo de obra derruba a hipótese. "ok, agora refaz
    o backend inteiro" começa com "ok" e é a coisa mais cara da lista, e essa é
    exatamente a confusão que não pode acontecer.
    """
    if len(bruto) > 120:
        return False
    # Risco nunca é seguimento: "a chave vaza se deixar no app?" é curto, soa
    # conversa, e é a pergunta mais cara da semana.
    if lx.RISCO.search(texto):
        return False
    if lx.AMPLITUDE.search(texto) or lx.CAUSA_OCULTA.search(texto) \
            or lx.NEGACAO_DEFEITO.search(texto):
        return False
    if lx.CONSTRUIR.search(texto):
        return False
    if len(_dominios(texto)) >= 1:
        return False
    # Porta 1: curto demais para conter tarefa.
    if len(bruto) <= 22:
        return True
    # Porta 2: palavra de seguimento, num pedido que não abriu nada.
    return bool(lx.CONTINUACAO.search(texto))


def _distintos(padrao, texto):
    """Quantas marcas diferentes daquela categoria aparecem.

    Distintas, não repetidas: quem escreve "tudo" três vezes na mesma frase está
    enfatizando, não pedindo três coisas.
    """
    return len(set(m.group(0).lower() for m in padrao.finditer(texto)))


def _pontuar(texto, bruto):
    """Soma os sinais e devolve (pontos, motivos legíveis)."""
    pontos = 0
    motivos = []

    def marca(delta, motivo):
        nonlocal pontos
        pontos += delta
        motivos.append((delta, motivo))

    def marca_intensa(padrao, base, motivo, teto=2):
        """Categoria pesada pontua pela quantidade de marcas distintas.

        Uma marca é um sinal; quatro são outro. "vale a pena migrar de
        arquitetura? compara os caminhos" tem quatro marcadores de decisão e
        pesava igual a um "muda o design" — que é uma tarefa completamente
        diferente.
        """
        quantas = _distintos(padrao, texto)
        if not quantas:
            return
        extra = min(quantas - 1, teto)
        marca(base + extra,
              motivo + (" (%d marcas)" % quantas if extra else ""))

    doms = _dominios(texto)

    defeito = bool(lx.CAUSA_OCULTA.search(texto) or lx.NEGACAO_DEFEITO.search(texto))
    if defeito:
        marca(3, "defeito sem causa conhecida — achar custa mais que consertar")
    marca_intensa(lx.AMPLITUDE, 3, "escopo aberto — é varredura, não ponto")
    if lx.VARREDURA.search(texto):
        marca(2, "pede revisão ou auditoria")
    marca_intensa(lx.DECISAO, 3,
                  "exige decisão de arquitetura ou escolha entre caminhos")
    if lx.RISCO.search(texto):
        marca(3, "mexe com segredo, permissão, dinheiro ou produção")
    if lx.DESEMPENHO.search(texto):
        marca(2, "desempenho: medir antes de mexer")

    if len(doms) >= 3:
        marca(3, "toca %d frentes diferentes (%s)" % (len(doms), ", ".join(doms)))
    elif len(doms) == 2:
        marca(2, "toca duas frentes (%s)" % ", ".join(doms))

    emendas = len(set(m.group(0).lower() for m in lx.EMENDA.finditer(texto)))
    if emendas:
        marca(min(emendas, 2), "vários pedidos emendados na mesma mensagem")

    itens = _itens(bruto)
    if itens >= 3:
        marca(1, "lista com %d itens" % itens)

    if len(bruto) > 2500:
        marca(2, "briefing muito longo")
    elif len(bruto) > 1200:
        marca(1, "briefing longo")

    if lx.CONSTRUIR.search(texto):
        marca(1, "pede obra, não conversa")

    # ---- o que barateia ----
    if lx.PRECISAO.search(bruto):
        marca(-2, "já diz o arquivo, a linha ou o símbolo — não há o que procurar")
    if lx.MECANICO.search(texto) and len(bruto) < 400:
        marca(-2, "edição mecânica: a resposta está no próprio pedido")
    amplo = bool(lx.AMPLITUDE.search(texto) or lx.VARREDURA.search(texto))
    if (lx.CONSULTA.search(texto) and not lx.CONSTRUIR.search(texto)
            and len(bruto) < 200 and not defeito and not amplo):
        marca(-2, "é pergunta, não trabalho")
    # Pedido curto só é barato quando não relata defeito nem abre escopo. O
    # tamanho da mensagem não tem relação com o tamanho do trabalho: "bug" são
    # três letras e uma caçada inteira.
    if len(bruto) < 25 and not defeito and not amplo:
        marca(-2, "pedido curto demais para conter tarefa")

    return pontos, motivos


def _piso(texto, tier):
    """Chão de segurança: há coisa que nunca desce, por mais curto que venha.

    "a chave vazou" tem quatro palavras e não é trabalho barato. O tamanho do
    pedido não tem relação com o tamanho do estrago.
    """
    if lx.RISCO.search(texto):
        return "media" if _ORDEM[tier] < _ORDEM["media"] else tier
    if (lx.CAUSA_OCULTA.search(texto) or lx.NEGACAO_DEFEITO.search(texto)) \
            and lx.AMPLITUDE.search(texto):
        return "cara"
    return tier


def classificar(pedido):
    """Devolve o veredito sobre um pedido.

    ``tier`` é ``None`` quando o pedido é continuação: aí não há o que
    classificar, e quem chama deve manter o que já estava valendo.
    """
    bruto = (pedido or "").strip()
    texto = _sem_acento(bruto)

    if not bruto:
        return _veredito(None, 0, [], continuacao=False, vazio=True)

    if lx.SAUDACAO.search(texto) and len(bruto) < 30 and not lx.CONSTRUIR.search(texto):
        return _veredito("trivial", 1.0,
                         [(0, "saudação, sem tarefa")], continuacao=False)

    if _e_continuacao(texto, bruto):
        return _veredito(None, 1.0,
                         [(0, "manda seguir — o custo é o da tarefa em curso")],
                         continuacao=True)

    pontos, motivos = _pontuar(texto, bruto)

    tier = "trivial"
    for corte, nome in _CORTES:
        if pontos >= corte:
            tier = nome
            break

    # Assimetria, mas só onde ela paga. Em cima de um corte a classificação é
    # sorte, e o desempate sobe — exceto na entrada de "cara". Subir para "cara"
    # por um ponto de diferença é gastar o modelo mais caro em dúvida, que é o
    # desperdício que este projeto existe para acabar. Deixar de subir ali custa
    # uma tarefa média rodando com esforço alto; subir sem motivo custa Opus.
    proximo_corte = min((corte for corte, _ in _CORTES if corte > pontos), default=None)
    perto = proximo_corte is not None and proximo_corte - pontos <= _MARGEM
    if perto:
        subiu = next(nome for corte, nome in _CORTES if corte == proximo_corte)
        if _ORDEM[subiu] > _ORDEM[tier] and subiu != "cara":
            tier = subiu
            motivos.append((0, "em cima do corte — sobe de faixa por segurança"))

    tier = _piso(texto, tier)
    confianca = 0.55 if perto else 0.85
    return _veredito(tier, confianca, motivos, continuacao=False, pontos=pontos)


def _veredito(tier, confianca, motivos, continuacao, pontos=0, vazio=False):
    return {
        "tier": tier,
        "continuacao": continuacao,
        "vazio": vazio,
        "pontos": pontos,
        "confianca": confianca,
        "motivos": [m for _, m in motivos],
        "detalhe": [{"peso": p, "motivo": m} for p, m in motivos if p],
    }
