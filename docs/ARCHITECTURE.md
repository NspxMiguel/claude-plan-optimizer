# Architecture — claude-plan-optimizer

## Overview

Picks the right model at the right reasoning effort for the task in front of it, so the strongest model stops being spent on changing a colour.

## Stack (extraído do repositório)

| Camada | Tecnologia | Versão / nota |
| --- | --- | --- |
| — | Não inferida automaticamente | Ver manifests |

## Alvos / targets

_Sem `project.yml` com targets, ou projeto não-Xcode._

## Diagrama de pastas (topo)

```mermaid
flowchart TD
  claude_plan_optimizer["claude-plan-optimizer"]
  claude_plan_optimizer --> n0["LICENSE"]
  claude_plan_optimizer --> n1["NOTAS-DESIGN.md"]
  claude_plan_optimizer --> n2["PEDIDOS.md"]
  claude_plan_optimizer --> n3["README.md"]
  claude_plan_optimizer --> n4["bin/"]
  claude_plan_optimizer --> n5["docs/"]
  claude_plan_optimizer --> n6["hooks/"]
  claude_plan_optimizer --> n7["install.sh"]
  claude_plan_optimizer --> n8["planopt/"]
  claude_plan_optimizer --> n9["skill/"]
  claude_plan_optimizer --> n10["tests/"]
```

## Fluxo de build (inferido)

```mermaid
flowchart LR
  start([código]) --> unknown[fluxo de build não inferido — ver SETUP.md]
```
