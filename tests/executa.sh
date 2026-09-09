#!/usr/bin/env bash
# Roda tudo. Um comando, porque suíte que precisa de instrução não é rodada.
set -uo pipefail
RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ"
falhas=0

python3 tests/test_classificador.py 2>&1 | tail -3 || falhas=$((falhas+1))
python3 tests/test_mapeamento.py    2>&1 | tail -3 || falhas=$((falhas+1))

echo "— CLI de ponta a ponta"
verifica() { # verifica <descrição> <comando> <padrão esperado>
  if eval "$2" 2>&1 | grep -qE "$3"; then printf '  ✓ %s\n' "$1"
  else printf '  ✗ %s\n     %s\n' "$1" "$2"; falhas=$((falhas+1)); fi
}
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
verifica "statusline lê e imprime"   "echo '{\"session_id\":\"t\",\"model\":{\"id\":\"claude-opus-5\",\"display_name\":\"Opus\"}}' | python3 bin/planopt statusline" 'Opus'
verifica "gancho cala em continuação" "echo '{\"prompt\":\"dale\"}' | python3 bin/planopt gancho | wc -c" '^ *0$'
verifica "gancho fala em tarefa cara" "echo '{\"prompt\":\"revisa o app inteiro e testa tudo\"}' | python3 bin/planopt gancho" 'planopt'
verifica "entrada quebrada não quebra" "echo 'nao e json' | python3 bin/planopt gancho; echo saiu=\$?" 'saiu=0'
verifica "ajuda sai limpa"           "python3 bin/planopt ajuda"                            'planopt'

echo
if [ "$falhas" -eq 0 ]; then echo "tudo passou"; else echo "$falhas falha(s)"; fi
exit "$falhas"
