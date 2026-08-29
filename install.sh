#!/usr/bin/env bash
# Instala o planopt: CLI no PATH, skill do Claude Code, e os dois ganchos.
#
# Idempotente de propósito — reinstalar é a forma normal de atualizar, e um
# instalador que só funciona em máquina limpa não é usado duas vezes.
set -euo pipefail

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN="${PLANOPT_BIN_DIR:-$HOME/.local/bin}"
CLAUDE="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
CASA="${PLANOPT_HOME:-$HOME/.claude-plan-optimizer}"

info() { printf '  %s\n' "$*"; }

mkdir -p "$BIN" "$CASA" "$CLAUDE/skills/plan-optimizer"

ln -sfn "$RAIZ/bin/planopt" "$BIN/planopt"
info "CLI: $BIN/planopt"

cp "$RAIZ/skill/SKILL.md" "$CLAUDE/skills/plan-optimizer/SKILL.md"
info "skill: $CLAUDE/skills/plan-optimizer/"

case ":$PATH:" in
  *":$BIN:"*) ;;
  *) info "aviso: $BIN não está no PATH — acrescente com: export PATH=\"$BIN:\$PATH\"" ;;
esac

python3 - "$CLAUDE/settings.json" "$BIN/planopt" <<'PY'
"""Liga o gancho e a linha de status sem estragar o que já está lá.

O settings.json é do dono da máquina e costuma ter hook de outros projetos: a
regra é acrescentar o que falta e não tocar em mais nada. Reescrever o arquivo
inteiro seria a forma mais rápida de este instalador apagar trabalho alheio.
"""
import json, os, sys

caminho, planopt = sys.argv[1], sys.argv[2]
try:
    with open(caminho, encoding="utf-8") as f:
        cfg = json.load(f)
except (OSError, ValueError):
    cfg = {}

ganchos = cfg.setdefault("hooks", {}).setdefault("UserPromptSubmit", [])
comando = "%s gancho" % planopt
ja = any(comando in json.dumps(g) for g in ganchos)
if not ja:
    ganchos.append({"hooks": [{"type": "command", "command": comando, "timeout": 10}]})
    print("  gancho UserPromptSubmit: ligado")
else:
    print("  gancho UserPromptSubmit: já estava ligado")

# A linha de status é o sensor: é o único lugar que recebe o modelo em uso e a
# porcentagem da janela de cinco horas. Sem ela o gancho fica cego. Mas ela é
# também o que a pessoa vê o dia inteiro, então uma que já exista não é trocada.
if not cfg.get("statusLine"):
    cfg["statusLine"] = {"type": "command", "command": "%s statusline" % planopt}
    print("  linha de status: ligada (ela é o sensor do modelo em uso)")
else:
    print("  linha de status: já havia uma — mantida")
    print("    sem ela o gancho não enxerga o modelo da sessão; para usar a do")
    print("    planopt: %s statusline" % planopt)

os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
tmp = caminho + ".planopt.tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2, ensure_ascii=False)
os.replace(tmp, caminho)
PY

info ""
info "pronto. experimente:"
info "  planopt explica \"muda a cor do botao pra azul\""
info "  planopt candidatos \"testa tudo e revisa o app inteiro\""
info "  planopt modo guarda    # interrompe modelo caro em tarefa barata"
