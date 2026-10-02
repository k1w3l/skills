# Obsidian-to-Vikunja Project Mapping

Use this as a current starting map, not as a substitute for discovering live projects. Project names/IDs can change; prefer live project titles and exact existing-task evidence on every run.

## Current project intent

- `Lab`: homelab, self-hosting, monitoring, and infrastructure notes.
- `To Study`: study-course parent tasks and their course workflow subtasks.
- `Games`: ROM/game maintenance notes.
- `Um dia...`: someday/general backlog; existing matching tasks are reused instead of duplicated.
- `Dev`: software/automation work, including finance-document automation when no more specific project exists.
- `Inbox`: fallback for an item with no defensible project, such as a section with no corresponding project.
- `Home` and `Setup`: inspect live task context before assigning; do not infer solely from the names.

## Folder and section defaults learned from the Obsidian TODO vault

- `Study/*.md` → parent task named after the file stem in `To Study`; unchecked checklist items become children.
- `Lab/Self_Hosting.md` → parent `Self Hosting` in `Lab`; each service bullet is a child, with long explanatory text kept in the description.
- `Lab/CashyOS.md` → parent `CashyOS` in `Lab` unless live project evidence clearly indicates a dedicated setup project.
- `Games/Atualizar_Roms.md` → parent `Atualizar Roms` in `Games`; clearly actionable ROM bullets become children, while unmarked wishlist prose is not imported.
- Root `ToDo.md` cards under `Lab` → `Lab`.
- Root `ToDo.md` cards under `Diversos` → normally `Um dia...`; reuse exact existing matching tasks there.
- Root `ToDo.md` cards under `Automação` → `Dev` when they are implementation/automation work.
- Root `ToDo.md` cards under `GCN` → `Inbox` unless a live GCN/contact project exists.

## Index deduplication

The root index often links to detailed notes (`Self Hosting`, `CashyOS`, study subjects, and `Doing`). Treat those links as navigation/parent references and do not create a second flat task for them. A parent task should come from the detailed note, with its child relation set through the Vikunja relations API.
