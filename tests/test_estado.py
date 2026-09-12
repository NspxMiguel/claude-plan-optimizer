"""Testes do estado: a ponte entre a linha de status e o gancho.

``pressao`` é o pedaço novo — lê a mesma telemetria que a linha de status já
grava a cada quadro, e que até existir isto ninguém consultava.
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from planopt import estado  # noqa: E402


class Pressao(unittest.TestCase):
    def test_sem_sessao_e_none(self):
        self.assertIsNone(estado.pressao(None))
        self.assertIsNone(estado.pressao({}))

    def test_sem_telemetria_e_none(self):
        """Plano Free nunca manda rate_limits — ausência não é folga."""
        self.assertIsNone(estado.pressao({"modelo_id": "claude-sonnet-5"}))

    def test_normal_abaixo_dos_dois_limiares(self):
        self.assertEqual(estado.pressao({"cinco_horas": 10, "sete_dias": 20}), "normal")

    def test_alerta_por_cinco_horas(self):
        self.assertEqual(estado.pressao({"cinco_horas": 75, "sete_dias": 5}), "alerta")

    def test_alerta_por_sete_dias(self):
        self.assertEqual(estado.pressao({"cinco_horas": 5, "sete_dias": 85}), "alerta")

    def test_critica_por_cinco_horas(self):
        self.assertEqual(estado.pressao({"cinco_horas": 95, "sete_dias": 5}), "critica")

    def test_critica_por_sete_dias(self):
        """É o caso medido de verdade: 5h com folga, 7 dias no talo."""
        self.assertEqual(estado.pressao({"cinco_horas": 35, "sete_dias": 97}), "critica")

    def test_critica_vence_alerta(self):
        self.assertEqual(estado.pressao({"cinco_horas": 95, "sete_dias": 85}), "critica")

    def test_um_campo_ausente_nao_quebra(self):
        self.assertEqual(estado.pressao({"cinco_horas": 96}), "critica")
        self.assertEqual(estado.pressao({"sete_dias": 96}), "critica")


class SessaoMaisRecente(unittest.TestCase):
    """Atalho de quem chama `planopt pressao` na mão, sem o session_id."""

    def setUp(self):
        self._casa_original = estado.CASA
        self._sessoes_original = estado.SESSOES
        self._tmp = tempfile.TemporaryDirectory()
        estado.CASA = self._tmp.name
        estado.SESSOES = os.path.join(self._tmp.name, "sessoes")

    def tearDown(self):
        estado.CASA = self._casa_original
        estado.SESSOES = self._sessoes_original
        self._tmp.cleanup()

    def test_sem_sessao_nenhuma_e_none(self):
        self.assertIsNone(estado.sessao_mais_recente())

    def test_pega_a_mais_nova(self):
        """mtime decide, não a ordem de escrita — por isso o -60s explícito."""
        estado.anotar_sessao("velha", modelo_id="claude-sonnet-5")
        caminho_velha = estado._caminho_sessao("velha")
        antigo = os.path.getmtime(caminho_velha) - 60
        os.utime(caminho_velha, (antigo, antigo))
        estado.anotar_sessao("nova", modelo_id="claude-opus-5")
        self.assertEqual(estado.sessao_mais_recente()["sessao"], "nova")


if __name__ == "__main__":
    unittest.main()
