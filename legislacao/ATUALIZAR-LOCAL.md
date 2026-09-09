# Atualizar o corpus numa sessão local (Claude in Chrome)

Este arquivo é o roteiro para rodar o Claude Code **na sua máquina**, onde o
navegador tem acesso ao Planalto e ao sijut2consulta. A sessão remota não
consegue: a política de egresso da organização devolve 403 no CONNECT para
todas as fontes legislativas, e o Chromium do contêiner sai pela mesma rede.

Numa sessão local o Claude in Chrome dirige o SEU Chrome — sua rede, sua
sessão. Foi assim que o tópico 03 do agente foi construído (CLAUDE.md §8).

## Antes de começar

```bash
cd ~/caminho/para/teste
git pull origin claude/google-notebook-lm-integration-mlh6rd

python3 -m venv .venv
.venv/bin/pip install pypdf
```

O venv é necessário porque `de_pdf.py` usa pypdf. (No ambiente remoto o
pacote `cryptography` do sistema está quebrado; no seu Mac o venv só mantém
a instalação limpa.)

Confirme que a extensão Claude in Chrome está conectada antes de pedir
qualquer navegação.

## O que colar no Claude

> Atualize o corpus de `legislacao/` a partir das fontes oficiais, usando o
> Chrome. Siga `legislacao/ATUALIZAR-LOCAL.md`: para cada norma da tabela,
> abra a URL, salve o texto consolidado, converta com `de_pdf.py` ou
> `do_drive.py` passando `--ate-artigo` e `--consolidado-em` de hoje, e
> confira o `git diff` de cada arquivo antes de commitar. Faça uma norma por
> vez e me mostre o diff quando o texto mudar. Comece pelo Decreto 3.048, que
> está faltando.

## As normas

Prioridade 1 — falta no corpus:

| Norma | URL | Verificação |
|---|---|---|
| Decreto 3.048/1999 (RPS) | https://www.planalto.gov.br/ccivil_03/decreto/d3048.htm | **o art. 216 tem que existir** — a versão truncada parava no art. 188 |

Prioridade 2 — desatualização confirmada:

| Norma | URL | `--ate-artigo` | Verificação |
|---|---|---|---|
| Lei 8.212/1991 | https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm | 105 | art. 25, I deve dizer **1,32%** (LC 224/2025), não 1,2% |
| IN RFB 2.110/2022 | http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=127178 | 277 | deve mencionar a **IN RFB 2.321/2026** |

Prioridade 3 — provavelmente sem mudança, mas com 491 dias:

| Norma | URL | `--ate-artigo` |
|---|---|---|
| CF/1988 | https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm | 250 |
| Lei 8.213/1991 | https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm | 156 |
| CTN (Lei 5.172/1966) | https://www.planalto.gov.br/ccivil_03/leis/l5172compilado.htm | 218 |
| Lei 10.522/2002 | https://www.planalto.gov.br/ccivil_03/leis/2002/l10522.htm | 84 |
| Lei 10.666/2003 | https://www.planalto.gov.br/ccivil_03/leis/2003/l10.666.htm | 15 |
| Lei 12.546/2011 | https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12546.htm | 52 |
| LC 150/2015 | https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp150.htm | 68 |

A IN RFB 2.058/2021 **não precisa**: foi reconvertida de um PDF de 10/06/2026
e conferida contra a anterior — texto idêntico.

Os números de `--ate-artigo` são o último artigo da versão que está no corpus
hoje. Servem de piso: se a norma cresceu, passa; se a extração truncou,
reprova. Nunca abaixe esses números para "fazer passar".

## Como salvar cada norma

A página do Planalto é HTML. Duas vias, ambas funcionam:

1. **`Ctrl+S` / `Cmd+S`** na página → salva `.htm` → converter com
   `do_drive.py` (que aceita texto direto, não só base64 do Drive).
2. **Imprimir para PDF** → converter com `de_pdf.py`.

Prefira a primeira: o HTML preserva a estrutura e não passa pela extração de
PDF, que é onde moram as duas patologias descritas em `FONTES.md`.

## Ao final de cada norma

```bash
.venv/bin/python legislacao/de_pdf.py <arquivo> <nome> \
    --fonte "<url>" --ate-artigo <N> --consolidado-em $(date +%F)

git diff legislacao/<nome>.md
```

Leia o diff antes de commitar. É ele que mostra qual artigo mudou — o motivo
de o corpus estar em git. Se vier vazio de conteúdo (só o carimbo de data),
a norma não mudou, e isso também é informação útil: registre no commit.

Ao terminar tudo:

```bash
python3 legislacao/status.py     # todas devem sair "ok"
git push origin claude/google-notebook-lm-integration-mlh6rd
```

## Se o Claude in Chrome não estiver disponível

Baixe as normas no navegador manualmente, ponha numa pasta do Google Drive e
peça a conversão na sessão remota — o conector do Drive funciona lá. É mais
lento, mas chega no mesmo lugar. Limite: PDF acima de ~7 MB não passa pelo
conector (foi o que barrou o Decreto 3.048).
