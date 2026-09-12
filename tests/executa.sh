#!/usr/bin/env bash
# Roda tudo. Um comando, porque suíte que precisa de instrução não é rodada.
set -uo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"
falhas=0

python3 tests/test_classificador.py 2>&1 | tail -3 || falhas=$((falhas+1))
python3 tests/test_mapeamento.py    2>&1 | tail -3 || falhas=$((falhas+1))
python3 tests/test_estado.py        2>&1 | tail -3 || falhas=$((falhas+1))

echo "— CLI de ponta a ponta"
verifica() { # verifica <descrição> <comando> <padrão esperado>
  if eval "$2" 2>&1 | grep -qE "$3"; then printf '  ✓ %s\n' "$1"
  else printf '  ✗ %s\n     %s\n' "$1" "$2"; falhas=$((falhas+1)); fi
}

# Casa isolada para todo o resto do arquivo: o gancho grava diário e sessão a
# cada chamada, e isso não pode acabar misturado com o ~/.claude-plan-optimizer
# de verdade — testar não pode ser a razão de uma métrica real ficar errada.
TMPCASA="$(mktemp -d)"
export PLANOPT_HOME="$TMPCASA"
trap 'rm -rf "$TMPCASA"' EXIT

verifica "classifica responde"      "python3 bin/planopt classifica 'muda a cor do botao'" 'barata|trivial'
verifica "continuação é reconhecida" "python3 bin/planopt classifica 'dale'"                'ontinua'
# These two assert the Portuguese wording, so they have to pin the language the
# same way the English case below does. Without the pin they follow the system
# locale: green on a pt-BR machine, red on CI, where the locale is C.
verifica "escopo aberto é caro"      "PLANOPT_LANG=pt python3 bin/planopt classifica 'testa tudo, revisa o app inteiro'" 'cara'
verifica "explica mostra os sinais"  "PLANOPT_LANG=pt python3 bin/planopt explica 'pq o app trava'"         'Por qu'
verifica "escolhe dá modelo"         "python3 bin/planopt escolhe subagente 'muda a cor'"   'haiku'
verifica "candidatos vêm do grátis"  "python3 bin/planopt candidatos 'muda a cor do botao'" 'gratis'
verifica "json é json"               "python3 bin/planopt classifica --json 'faz um app'"   '\"tier\"'
verifica "inglês responde em inglês" "PLANOPT_LANG=en python3 bin/planopt classifica 'change the colour'" 'Tier'
verifica "motivo também sai em inglês, não só o rótulo da faixa" \
  "PLANOPT_LANG=en python3 bin/planopt explica 'revisa tudo: ui, banco de dados e testes'" \
  'touches [0-9]+ different areas \(frontend, data, test\)'
verifica "statusline lê e imprime"   "echo '{\"session_id\":\"t\",\"model\":{\"id\":\"claude-opus-5\",\"display_name\":\"Opus\"}}' | python3 bin/planopt statusline" 'Opus'
verifica "gancho cala em continuação" "echo '{\"prompt\":\"dale\"}' | python3 bin/planopt gancho | wc -c" '^ *0$'
verifica "gancho fala em tarefa cara" "echo '{\"prompt\":\"revisa o app inteiro e testa tudo\"}' | python3 bin/planopt gancho" 'planopt'
verifica "entrada quebrada não quebra" "echo 'nao e json' | python3 bin/planopt gancho; echo saiu=\$?" 'saiu=0'
verifica "gancho barato sugere sair da conta medida" "echo '{\"prompt\":\"muda a cor do botao pra azul\"}' | python3 bin/planopt gancho" 'sem gastar|without touching'
verifica "ajuda sai limpa"           "python3 bin/planopt ajuda"                            'planopt'

echo "— pressão de uso (telemetria que a linha de status já grava)"
echo '{"session_id":"e2e","model":{"id":"claude-sonnet-5","display_name":"Sonnet 5"},"rate_limits":{"five_hour":{"used_percentage":40},"seven_day":{"used_percentage":97}}}' \
  | python3 bin/planopt statusline > /dev/null
verifica "sem telemetria avisa, não inventa folga" "python3 bin/planopt pressao nao-existe" 'ainda|yet'
verifica "pressão crítica aparece"   "PLANOPT_LANG=pt python3 bin/planopt pressao e2e" 'ítico'
verifica "pressão critica em ingles" "PLANOPT_LANG=en python3 bin/planopt pressao e2e" 'critical'
verifica "pressão aponta quem é de graça" "python3 bin/planopt pressao e2e" 'ollama|gemini|antigravity|groq|openrouter|omniroute'
verifica "gancho sob pressão puxa a faixa média também" \
  "PLANOPT_LANG=pt bash -c \"echo '{\\\"session_id\\\":\\\"e2e\\\",\\\"prompt\\\":\\\"otimiza o app pra nao pesar tanto\\\"}' | python3 bin/planopt gancho\"" \
  'apertada'

echo
if [ "$falhas" -eq 0 ]; then echo "tudo passou"; else echo "$falhas falha(s)"; fi
exit "$falhas"
