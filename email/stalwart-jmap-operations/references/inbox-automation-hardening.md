# Endurecimento de automações de Inbox

Use esta referência ao migrar, reativar, testar ou corrigir rotinas que importam mensagens por
Imapsync e depois as classificam via JMAP. Ela cobre interações entre importador, keywords,
wrappers de cron e regras de categorização.

## 1. Sintoma: backlog reaparece sem aumento equivalente do total

Padrão diagnóstico:

- antes da sincronização, `processed == total` e `pending == 0`;
- durante ou logo após o Imapsync, `total` fica estável, mas `processed` cai e `pending` sobe;
- o journal mostra que a passagem acabou de visitar a Inbox.

Isso indica ressincronização de flags, não necessariamente mensagens novas. O Imapsync habilita
`--resyncflags` por padrão e pode remover no destino keywords que não existem na origem, como
`agent-processed`.

Correção durável: usar `--noresyncflags` quando o destino possui flags/keywords mantidas por uma
automação local.

## 2. Sequência segura de correção e prova

1. Registre `total`, `processed` e `pending` da Inbox, sem imprimir assuntos ou remetentes.
2. Leia somente a configuração não secreta necessária; faça backup timestamped preservando
   dono, grupo e modo.
3. Adicione `--noresyncflags` ao comando durável do Imapsync e valide a configuração do Compose.
4. Organize o backlog até `pending == 0`; essa é a baseline.
5. Deixe uma passagem real do Imapsync atravessar a Inbox.
6. Compare as contagens imediatamente depois:
   - `processed` das mensagens preexistentes não pode diminuir;
   - qualquer aumento de `pending` deve ser no máximo o delta de mensagens realmente novas;
   - processe somente esse delta e confirme `pending == 0`.
7. Confirme que timer e jobs continuam ativos e execute o caminho real do scheduler, não apenas
   funções internas.

Não considere `health` ou um dry-run isolado como prova dessa interação; é necessária uma
sincronização real seguida de contagem JMAP.

## 3. Não interrompa `docker compose run --rm` apenas para acelerar o teste

Uma unidade systemd pode acompanhar o processo `docker compose`, enquanto o container é criado
pelo daemon Docker. Interromper a unidade no meio da execução pode matar o wrapper e deixar o
container `run` continuando sem o lock original.

Preferência operacional:

1. deixe a passagem atual terminar;
2. aplique a configuração para a passagem seguinte;
3. valide quando ela ultrapassar a Inbox.

Se uma interrupção for realmente necessária, obtenha autorização explícita e verifique
separadamente:

- estado da unidade e do timer;
- inventário de containers Imapsync e seus horários de criação;
- existência de mais de uma execução;
- limpeza apenas da execução identificada, nunca por nome presumido;
- timer ativo após a manutenção.

Se o controle de segurança negar a interrupção, não tente uma via alternativa; aguarde a
execução terminar.

### Proteção durável contra sobreposição

`flock` sozinho protege o processo que mantém o descritor, não um container criado pelo daemon
Docker. Se o wrapper morrer e o container continuar, o lock é liberado cedo demais. O padrão
endurecido deve combinar:

1. lock de arquivo não bloqueante;
2. consulta a containers ativos pelo label `com.docker.compose.service=imapsync` antes da
   partida;
3. nome fixo de container para fechar a janela de corrida entre a consulta e o `docker run`;
4. captura de `TERM`/`INT` no wrapper, com parada e remoção somente do container que ele gerencia;
5. `KillMode=mixed` e timeout de parada suficiente na unidade systemd;
6. timer baseado em `OnUnitInactiveSec`, para contar o intervalo depois do término e não
   enfileirar uma nova passagem imediatamente quando a anterior exceder o intervalo nominal.

Teste separadamente os dois guardas: uma chamada concorrente deve sair de forma esperada sem
mudar a contagem de containers; depois, use um container inofensivo para provar que um `TERM` no
wrapper não deixa órfão. Não interrompa a sincronização de produção apenas para fazer esse teste.

## 4. Polling de systemd sem falso erro

`systemctl is-active` pode imprimir estados úteis como `activating` ou `inactive` com código de
saída diferente de zero. Em verificadores remotos, não trate todo código não zero como falha de
transporte. Capture stdout e interprete o estado; diferencie isso de erro SSH, timeout ou ausência
de saída.

## 5. Wrappers de cron devem preservar argumentos de teste

Um wrapper que chama o motor compartilhado sem repassar `sys.argv[1:]` ignora `--dry-run`,
`--limit` ou `--prime`. Isso pode transformar um teste presumidamente não destrutivo em uma
execução real.

Padrão correto:

```python
raise SystemExit(
    subprocess.run([
        sys.executable,
        str(engine),
        "organize",
        *sys.argv[1:],
    ], text=True).returncode
)
```

Antes de confiar no teste, confirme que o relatório efetivamente indica `dry_run: true` e que as
contagens remotas não mudaram. Faça o mesmo para wrappers de alertas.

## 6. Reduza falsos positivos de classificação e alertas

Não classifique pela concatenação do corpo completo: rodapés de marketing contêm termos como
“X”, “conta”, “pedido”, links sociais e textos de suporte que geram várias categorias falsas.

Ordem recomendada:

1. remetentes/domínios conhecidos têm precedência e retornam suas categorias determinísticas;
2. para desconhecidos, use remetente, assunto e preview;
3. mantenha os predicados de alertas separados das regras de categoria;
4. preserve a pasta original e adicione somente associações `Categorias/*`;
5. direcione itens sem regra para revisão;
6. valide com casos representativos de cada regra e um caso de ruído presente apenas no corpo.

Para reativação após uma pausa, faça uma primeira execução controlada, grave o estado de
deduplicação e execute novamente: a segunda passagem deve produzir zero alertas duplicados.
