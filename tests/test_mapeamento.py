"""Testes do mapeamento: faixa -> modelo e esforço, por alvo."""

import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from planopt.mapeamento import Mapeamento, _NUNCA_AUTOMATICO  # noqa: E402
from planopt.classificador import TIERS                        # noqa: E402


class Estrutura(unittest.TestCase):
    def setUp(self):
        self.m = Mapeamento()

    def test_json_e_valido_e_completo(self):
        for nome, conf in self.m.alvos.items():
            with self.subTest(alvo=nome):
                self.assertIn(conf.get("aplicacao"), ("obrigatorio", "conselho"))
                self.assertTrue(conf.get("carteira"), "sem carteira")
                for tier in (conf.get("tiers") or {}):
                    self.assertIn(tier, TIERS, "faixa desconhecida em %s" % nome)

    def test_esforco_so_onde_e_suportado(self):
        """Prometer esforço onde a CLI não aceita é mentir no relatório."""
        for nome in self.m.nomes():
            for tier in TIERS:
                escolha = self.m.escolha(nome, tier)
                if escolha and escolha["esforco"]:
                    with self.subTest(alvo=nome, tier=tier):
                        self.assertTrue(self.m.alvos[nome].get("esforco_suportado"))

    def test_esforco_extremo_nunca_e_automatico(self):
        """xhigh e max multiplicam token de raciocínio: não entram por palpite."""
        for nome in self.m.nomes():
            for tier in TIERS:
                escolha = self.m.escolha(nome, tier)
                if escolha:
                    with self.subTest(alvo=nome, tier=tier):
                        self.assertNotIn(escolha["esforco"], ("xhigh", "max"))


class Carteira(unittest.TestCase):
    def setUp(self):
        self.m = Mapeamento()

    def test_gratis_vem_antes_de_medida(self):
        ordem = [e["carteira"] for e in self.m.candidatos("media", incluir_medida=True)]
        if "gratis" in ordem and "medida" in ordem:
            self.assertLess(ordem.index("gratis"), ordem.index("medida"))

    def test_emprestada_e_paga_ficam_de_fora(self):
        """Conta de outra pessoa e dinheiro de verdade só entram quando nomeados."""
        for tier in TIERS:
            for escolha in self.m.candidatos(tier, incluir_medida=True):
                with self.subTest(tier=tier, alvo=escolha["alvo"]):
                    self.assertNotIn(escolha["carteira"], _NUNCA_AUTOMATICO)

    def test_cursor_nunca_pega_trabalho_trivial_sozinho(self):
        alvos = {e["alvo"] for e in self.m.candidatos("trivial", incluir_medida=True)}
        self.assertNotIn("cursor", alvos)

    def test_trivial_tem_opcao_gratis(self):
        """A faixa barata só serve se houver quem a faça sem custo."""
        for tier in ("trivial", "barata"):
            with self.subTest(tier=tier):
                carteiras = {e["carteira"] for e in self.m.candidatos(tier)}
                self.assertTrue(carteiras & {"local", "gratis"})


class MelhorGratis(unittest.TestCase):
    """O atalho que o gancho usa para sugerir sair da conta medida."""

    def setUp(self):
        self.m = Mapeamento()

    def test_devolve_a_cabeca_de_candidatos(self):
        for tier in TIERS:
            with self.subTest(tier=tier):
                self.assertEqual(self.m.melhor_gratis(tier), self.m.candidatos(tier)[0]
                                  if self.m.candidatos(tier) else None)

    def test_nunca_devolve_conta_medida(self):
        for tier in TIERS:
            candidato = self.m.melhor_gratis(tier)
            if candidato:
                with self.subTest(tier=tier):
                    self.assertNotIn(candidato["alvo"], ("claude", "subagente"))

    def test_trivial_cai_no_local(self):
        candidato = self.m.melhor_gratis("trivial")
        self.assertIsNotNone(candidato)
        self.assertEqual(candidato["carteira"], "local")


class Fila(unittest.TestCase):
    def setUp(self):
        self.m = Mapeamento()

    def test_gratis_tem_reserva(self):
        """Plano gratuito responde 429 sem avisar: um id só não sustenta a faixa."""
        escolha = self.m.escolha("openrouter", "trivial")
        self.assertTrue(escolha["alternativas"], "openrouter trivial sem reserva")

    def test_raciocinio_fora_da_faixa_trivial(self):
        evitar = set(self.m.dados["evitar_em_trivial"]["modelos"])
        for tier in ("trivial", "barata"):
            for escolha in self.m.candidatos(tier):
                with self.subTest(tier=tier, alvo=escolha["alvo"]):
                    self.assertNotIn(escolha["modelo"], evitar)

    def test_faixa_ausente_devolve_none(self):
        """Ausência é informação: 'este não é o agente para este trabalho'."""
        self.assertIsNone(self.m.escolha("ollama", "cara"))
        self.assertIsNone(self.m.escolha("nao-existe", "media"))


if __name__ == "__main__":
    unittest.main()
