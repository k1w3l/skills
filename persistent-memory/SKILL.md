---
name: persistent-memory
description: >-
  Memórias persistentes importadas do Claude Code (home lab, PCL, Horus,
  Kartrack, ZMK). Use em diagnóstico, homelab, Proxmox, backup, wiki,
  hardware PCL, Horus, Kartrack ou teclado ZMK.
---

# Persistent Memory (Claude Code → Cursor)

Memórias ficam em `~/.cursor/memory/` (symlinks para `~/.claude/projects/*/memory`).

## Onde olhar

| Escopo | Path |
|--------|------|
| Home / PCL / homelab | `~/.cursor/memory/home/MEMORY.md` |
| Projeto Horus | `~/.cursor/memory/horus/MEMORY.md` |
| Projeto Kartrack | `~/.cursor/memory/kartrack/MEMORY.md` |
| ZMK Sofle | `~/.cursor/memory/zmk-sofle/MEMORY.md` |

## Como usar

1. Leia o `MEMORY.md` do escopo relevante (índice com links).
2. Abra só os arquivos de memória citados que forem necessários.
3. **Não use** `mem-search` / `plugin-claude-mem-mcp-search` enquanto o worker estiver morto (Bun ausente no PCL desde 2026-09-12; decisão 2026-09-19: seguir sem). Histórico de sessão não está disponível — grave fato estável nestas notas ou na wiki.
4. Em brainstorm, diagnóstico, projeto ou implantação: consulte também a wiki unificada via skill `wiki` (`/mnt/NAS/Sync/Documentos/Pessoal/Wiki/wiki/`).

Se `~/.cursor/memory/<escopo>` for um arquivo (não symlink/diretório), restaurar o `ln -s` para `~/.claude/projects/*/memory` — não reescrever a memória do zero. Detalhe: `home/cursor-memory-fontes.md`.

## Escrita

Se aprender um fato estável que deva persistir, acrescente/atualize o arquivo correspondente em `~/.cursor/memory/<escopo>/` e o índice `MEMORY.md` — os symlinks atualizam o Claude Code também.
