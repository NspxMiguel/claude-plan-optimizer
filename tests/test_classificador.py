"""Testes do classificador.

Os exemplos aqui são escritos à mão, no mesmo dialeto do corpus real — português
informal, sem acento, abreviado — mas **nenhum é um pedido real de ninguém**. O
corpus que calibrou os cortes tem nome de projeto, domínio e caminho de máquina
dentro, e não entra em repositório público. O que entra é a forma dele.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from planopt.classificador import classificar, TIERS, _ORDEM  # noqa: E402


def tier(texto):
    return classificar(texto)["tier"]


def e_continuacao(texto):
    return classificar(texto)["continuacao"]


class Continuacao(unittest.TestCase):
    """22% dos pedidos reais mandam seguir em vez de descrever trabalho."""

    def test_palavra_de_seguimento(self):
        for texto in ("continua", "dale", "vai", "pode ir", "isso mesmo",
                      "beleza", "go ahead", "keep going"):
            with self.subTest(texto=texto):
                self.assertTrue(e_continuacao(texto), texto)

    def test_reconhecimento_nu(self):
        """"." e "b" não têm vocabulário — o que os identifica é a ausência."""
        for texto in (".", "b", "nada", "pronyo", "foi ja?", "msm versao"):
            with self.subTest(texto=texto):
                self.assertTrue(e_continuacao(texto), texto)

    def test_continuacao_nao_tem_faixa(self):
        """Sem faixa de propósito: o custo é o da tarefa em curso."""
        self.assertIsNone(tier("dale"))

    def test_ok_seguido_de_trabalho_nao_e_continuacao(self):
        """A confusão que arruinaria tudo: "ok" abrindo o pedido mais caro do dia."""
        self.assertFalse(e_continuacao("ok, agora refaz o backend inteiro"))
        self.assertEqual(tier("ok, agora refaz o backend inteiro"), "cara")

    def test_verbo_de_obra_derruba_a_hipotese(self):
        self.assertFalse(e_continuacao("pode colocar o botao de sair"))

    def test_risco_nunca_e_continuacao(self):
        """Curto, soa conversa, e é a pergunta mais cara da semana."""
        self.assertFalse(e_continuacao("ok, a chave vaza?"))

    def test_defeito_curto_nao_e_continuacao(self):
        self.assertFalse(e_continuacao("vai que ta bugado"))


class FaixaBarata(unittest.TestCase):
    """O pedido que abriu o projeto: Opus para mudar a cor de uma coisa."""

    def test_mudanca_de_cor(self):
        self.assertIn(tier("muda a cor do botao pra azul"), ("trivial", "barata"))

    def test_arquivo_e_linha_barateiam(self):
        """Quem já disse onde é tirou a busca do meio, que era o trabalho caro."""
        com = classificar("renomeia a funcao no src/app.py:42")["pontos"]
        sem = classificar("renomeia aquela funcao la")["pontos"]
        self.assertLess(com, sem)

    def test_saudacao(self):
        self.assertEqual(tier("oi"), "trivial")
        self.assertEqual(tier("bom dia"), "trivial")


class FaixaCara(unittest.TestCase):
    def test_escopo_aberto(self):
        self.assertEqual(tier("testa tudo, revisa o app inteiro"), "cara")

    def test_decisao_de_arquitetura(self):
        self.assertEqual(
            tier("vale a pena migrar pra outra arquitetura? compara os caminhos"), "cara")

    def test_defeito_com_escopo_aberto_tem_chao(self):
        """Causa desconhecida somada a escopo aberto não desce de 'cara'."""
        self.assertEqual(tier("ta tudo bugado, nao funciona nada"), "cara")


class Assimetria(unittest.TestCase):
    """Errar para baixo custa resposta errada; errar para cima custa dinheiro."""

    def test_risco_tem_chao_mesmo_curto(self):
        """Quatro palavras, e não é trabalho barato."""
        for texto in ("a chave vazou", "a senha ta no codigo", "token exposto"):
            with self.subTest(texto=texto):
                self.assertGreaterEqual(_ORDEM[tier(texto)], _ORDEM["media"], texto)

    def test_defeito_curto_nao_leva_desconto_de_tamanho(self):
        """"bug" são três letras e uma caçada inteira."""
        self.assertGreaterEqual(_ORDEM[tier("bug")], _ORDEM["barata"])
        self.assertGreaterEqual(_ORDEM[tier("chiaki sumiu")], _ORDEM["barata"])

    def test_nao_sobe_para_cara_por_um_ponto(self):
        """A assimetria não vale na entrada de 'cara'.

        Subir para o modelo mais caro na dúvida é exatamente o desperdício que
        este projeto existe para acabar — ali o desempate fica onde está.
        """
        veredito = classificar("otimiza o app pra nao pesar tanto")
        if veredito["pontos"] == 4:
            self.assertEqual(veredito["tier"], "media")


class Robustez(unittest.TestCase):
    def test_vazio(self):
        for texto in ("", "   ", None):
            with self.subTest(texto=texto):
                self.assertTrue(classificar(texto)["vazio"])

    def test_determinismo(self):
        texto = "arruma o css da pagina de login e escreve teste"
        self.assertEqual(classificar(texto), classificar(texto))

    def test_faixa_sempre_conhecida(self):
        for texto in ("x", "faz o app", "a" * 5000, "🙂🙂🙂", "SELECT * FROM t;"):
            with self.subTest(texto=texto[:20]):
                v = classificar(texto)
                self.assertTrue(v["continuacao"] or v["tier"] in TIERS)

    def test_acento_nao_muda_nada(self):
        self.assertEqual(tier("nao funciona a pagina"), tier("não funciona a página"))

    def test_ingles_tambem(self):
        self.assertIn(tier("change the button colour"), ("trivial", "barata"))
        self.assertEqual(tier("review the entire app and audit everything"), "cara")

    def test_nao_toca_a_rede(self):
        """Um classificador que chama modelo para escolher modelo é absurdo.

        A regra vale como teste porque é a que mais tenta ser quebrada quando
        alguém quiser "melhorar a precisão".
        """
        import socket
        original = socket.socket

        def recusa(*a, **k):
            raise AssertionError("o classificador tentou abrir soquete")

        socket.socket = recusa
        try:
            classificar("faz um refactor grande no backend inteiro")
        finally:
            socket.socket = original


if __name__ == "__main__":
    unittest.main()
