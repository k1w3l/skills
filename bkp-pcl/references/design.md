# bkp-pcl — Design e racional (contexto da sessão de brainstorm)

Este documento registra *por que* o sistema é do jeito que é, para que ajustes
futuros não revertam decisões sem entender o motivo.

## Problema
Reconstituir o setup rapidamente após reinstalar o sistema e proteger os dados
pessoais. O pedido original era "sincronizar tudo com o NAS", mas isso conflava
três problemas com requisitos opostos — daí a separação em camadas.

## A premissa central: 3+1 problemas, não 1
| Categoria | Quer | Ferramenta natural |
|---|---|---|
| Config versionável | histórico, seletivo, reproduzível | git (yadm) |
| Segredos | cifrado, nunca em git plano | gpg |
| Dados brutos | mirror/backup, sem versão por arquivo | rsync (+ ZFS) |

Tratar tudo com uma ferramenta só (ex.: Syncthing/rsync do home inteiro) foi
rejeitado: incha tudo com estado de app, vaza segredos em texto plano e não dá
restauração reproduzível.

## Decisões e justificativas
| Decisão | Escolha | Por quê |
|---|---|---|
| Arquitetura | 4 camadas separadas | requisitos opostos por categoria |
| Ferramenta de config | **yadm** | git sobre `$HOME` + cripto gpg nativa; o usuário só tem gpg e pensa em "arquivos do home". chezmoi seria abstração a mais; stow não tem cripto |
| Host do repo | **bare git no NAS** (`/mnt/NAS/PCL/Backup/dotfiles.git`) | segredos nunca saem de casa; o usuário não quis offsite em terceiros |
| Segredos | gpg **assimétrico**, só `.ssh` e `.kube` | público cifra sem passphrase (job automático); privado só no restore. Decisão do usuário de limitar o escopo |
| Bootstrap da chave gpg | export no **Bitwarden** | resolve o ovo-e-galinha: na máquina nova você ainda não tem a chave, e ela é o único segredo que não pode morar (em claro) no NAS |
| Dados | rsync `--backup`, retenção 1 dia | espelho com rede de segurança curta; o histórico profundo é o snapshot ZFS do TrueNAS, então `--backup` longo seria redundante |
| Gatilho | híbrido | config muda raramente (timer diário, commit "limpo"); dados mudam direto (inotify+debounce 5min); estado pesado churny (timer diário) |
| NFS | converter `mnt-NAS.mount` → **automount** | a `.mount` no boot era intermitente ("nem sempre monta no login"); automount monta sob demanda e some com a corrida de rede |
| Dep. de rede do automount | **só no `.mount`, nunca no `.automount`** | a 1ª versão do `.automount` tinha `After/Wants=network-online.target` → ciclo de ordenação (`local-fs → automount → network-online → NetworkManager → … → local-fs`) → systemd quebrou apagando o job do NetworkManager → boot **sem rede** (jun/2026). O `.automount` sobe cedo (local-fs) e não pode esperar a rede; quem espera é o `.mount`, acionado sob demanda fora do boot |
| git_token | migrar p/ `gh auth setup-git` e `shred` | o `gh` já estava autenticado; o `git_token.txt` em texto plano no `~` era redundante e um vazamento |

## Allowlist — filosofia
Allowlist explícita (escolho o que entra), **não** "tudo menos exclusões". Muita
coisa em `~/.config` é estado de app, não config (`google-chrome`, `Bitwarden`,
`Electron`, `Code`, `Kuro`, browsers). Regras:
- Itens grandes entram **seletivos** (só os arquivos de config). Ex.: noctalia
  tinha 30M só em `plugins/` → entra `plugins.json` + config, reinstala o resto.
- `.claude`: config no yadm; estado churny na camada de dados.
- `webapps` (`WebApp-*.desktop` em `~/.local/share/applications`) entram no yadm;
  os perfis de browser (`~/.local/share/ice`, ~10G) entram na camada de estado
  para **não precisar relogar** em tudo na restauração (decisão do usuário).
- Mídia custom do LCD (`~/.local/share/thermalright-lcd-control`, ~935M) → estado.

## Fluxo de restauração (o teste real)
1. montar NAS (NFS) — `install-system.sh` deixa o automount permanente
2. `pacman -S yadm rsync inotify-tools gnupg github-cli`
3. importar a chave gpg privada do Bitwarden (`gpg --import`)
4. `yadm clone /mnt/NAS/PCL/Backup/dotfiles.git`
5. `yadm decrypt` (restaura `.ssh`/`.kube`)
6. `gh auth login` + re-login do Claude
7. dados ficam no NAS; restaura sob demanda com rsync reverso

## Estrutura no NAS
```
/mnt/NAS/PCL/Backup/
├── dotfiles.git/          # bare repo yadm (config + segredos cifrados)
├── data/home/             # espelho do home não-oculto
├── data/state/            # estado pesado (ice, trcc, .claude churny)
└── data-backup/<data>/    # versões substituídas (retenção 1 dia)
```
Nota: `/mnt/NAS/PCL/` já continha um espelho FreeFileSync antigo do home; o
`Backup/` foi criado como subpasta nova, sem tocar no resto. Limpeza desse
espelho antigo é uma tarefa futura opcional.

## Pendências/abertos na época da criação
- A ativação final dependia de passos com sudo/interativos do usuário:
  `pacman` install, `gpg --quick-generate-key`, export pro Bitwarden,
  `install-system.sh` (automount) e `setup.sh`.
- `loginctl enable-linger $USER` é opcional para os timers rodarem sem sessão
  gráfica ativa.
