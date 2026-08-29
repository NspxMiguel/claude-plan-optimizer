"""Traduz uma faixa de custo na escolha concreta de cada alvo.

Duas coisas diferentes moram aqui, e confundi-las é o erro que faz um roteador
gastar caro achando que está economizando:

* **a dificuldade escolhe a força** — quanto raciocínio o trabalho merece;
* **a carteira escolhe quem paga** — e a carteira medida (o plano do dono) é
  justamente a que este projeto existe para poupar.

Uma tarefa cara não quer dizer "gaste Opus". Quer dizer "gaste o mais forte que
não sai do plano medido" — e é por isso que a tabela é por alvo, não global.
"""

import json
import os

_AQUI = os.path.dirname(os.path.abspath(__file__))
_PADRAO = os.path.join(_AQUI, "mapeamento.json")

# Ordem de preferência quando é preciso escolher quem faz o trabalho: quem não
# custa nada primeiro, quem custa o plano do dono por último. "emprestada" fica
# fora da escolha automática de propósito — é conta de outra pessoa.
_ORDEM_CARTEIRA = ("local", "gratis", "secundaria", "depende_do_provedor", "medida")
# "emprestada" é conta de outra pessoa; "paga" gasta dinheiro de verdade. As
# duas só entram quando alguém as nomeia à mão.
_NUNCA_AUTOMATICO = ("emprestada", "paga")


class Mapeamento:
    def __init__(self, caminho=None):
        self.caminho = caminho or os.environ.get("PLANOPT_MAPEAMENTO") or _PADRAO
        with open(self.caminho, encoding="utf-8") as arquivo:
            self.dados = json.load(arquivo)
        self.alvos = self.dados.get("alvos", {})

    # ------------------------------------------------------------------ alvo ---
    def conhece(self, alvo):
        return alvo in self.alvos

    def nomes(self):
        return sorted(self.alvos)

    def escolha(self, alvo, tier):
        """O que rodar naquele alvo para aquela faixa.

        Devolve ``None`` quando o alvo não atende a faixa — o que é informação,
        não falha: significa "esse não é o agente para este trabalho".
        """
        conf = self.alvos.get(alvo)
        if not conf or not tier:
            return None
        linha = (conf.get("tiers") or {}).get(tier)
        if linha is None:
            return None
        esforco = linha.get("esforco") or ""
        if esforco and not conf.get("esforco_suportado"):
            esforco = ""

        # A entrada pode ser um modelo ou uma fila. Plano gratuito responde 429
        # com frequência e sem aviso — na medição de 28/08/2026, quatro dos
        # dezesseis modelos livres estavam indisponíveis, e não os mesmos quatro
        # de meia hora antes. Um modelo só, aqui, é um agente que não trabalha
        # metade do tempo; a fila é o que faz a faixa continuar de pé.
        bruto = linha.get("modelo") or ""
        fila = [m for m in (bruto if isinstance(bruto, list) else [bruto]) if m]
        if tier in ("trivial", "barata"):
            evitar = set(((self.dados.get("evitar_em_trivial") or {}).get("modelos")) or ())
            fila = [m for m in fila if m not in evitar] or fila

        return {
            "alvo": alvo,
            "rotulo": conf.get("rotulo", alvo),
            "tier": tier,
            "modelo": fila[0] if fila else "",
            "alternativas": fila[1:],
            "esforco": esforco,
            "esforco_flag": conf.get("esforco_flag") or "",
            "aplicacao": conf.get("aplicacao", "conselho"),
            "carteira": conf.get("carteira", ""),
            "nota": conf.get("_nota", ""),
        }

    # -------------------------------------------------------------- carteira ---
    def candidatos(self, tier, disponiveis=None, incluir_medida=False):
        """Quem pode fazer trabalho dessa faixa, do mais barato para o mais caro.

        ``disponiveis`` filtra por quem está de pé agora. A carteira medida só
        entra quando pedida: delegar existe para não gastá-la.
        """
        saida = []
        for nome, conf in self.alvos.items():
            if disponiveis is not None and nome not in disponiveis:
                continue
            carteira = conf.get("carteira", "")
            if carteira in _NUNCA_AUTOMATICO:
                continue
            if carteira == "medida" and not incluir_medida:
                continue
            if nome in ("claude", "subagente") and not incluir_medida:
                continue
            escolha = self.escolha(nome, tier)
            if escolha:
                saida.append(escolha)
        ordem = {c: i for i, c in enumerate(_ORDEM_CARTEIRA)}
        saida.sort(key=lambda e: (ordem.get(e["carteira"], len(_ORDEM_CARTEIRA)), e["alvo"]))
        return saida

    # -------------------------------------------------------------- esforços ---
    def esforcos_automaticos(self):
        return tuple((self.dados.get("esforcos") or {}).get("automaticos") or ())

    def esforcos_so_a_mao(self):
        return tuple((self.dados.get("esforcos") or {}).get("so_a_mao") or ())


_cache = None


def carregar(caminho=None):
    global _cache
    if caminho or _cache is None:
        mapa = Mapeamento(caminho)
        if caminho is None:
            _cache = mapa
        return mapa
    return _cache
