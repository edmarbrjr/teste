# Corpus de legislação previdenciária

Fonte da verdade local para consulta por `grep`/`rg`. Não substitui o texto
oficial: para citação em documento, confira sempre a URL da coluna Fonte.

## No corpus

| Arquivo | Norma | Extensão | Fonte |
|---|---|---|---|
| `constituicao-1988.md` | CF/1988 | 162 p., 250 artigos | [Planalto](https://www.planalto.gov.br/ccivil_03/constituicao/constituicaocompilado.htm) |
| `lei-8212-1991.md` | Lei 8.212/1991 — custeio | 37 p., 105 artigos | [Planalto](https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm) |
| `lei-8213-1991.md` | Lei 8.213/1991 — benefícios | 42 p., 154 artigos | [Planalto](https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm) |
| `lei-10666-2003.md` | Lei 10.666/2003 | 3 p., 15 artigos | [Planalto](https://www.planalto.gov.br/ccivil_03/leis/2003/l10.666.htm) |
| `lei-10522-2002.md` | Lei 10.522/2002 — art. 19, jurisprudência vinculante | 20 p., 70 artigos | [Planalto](https://www.planalto.gov.br/ccivil_03/leis/2002/l10522.htm) |
| `lei-12546-2011.md` | Lei 12.546/2011 — CPRB | 18 p., 68 artigos | [Planalto](https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12546.htm) |
| `lei-5172-1966-ctn.md` | CTN | 31 p., 204 artigos | [Planalto](https://www.planalto.gov.br/ccivil_03/leis/l5172compilado.htm) |
| `lcp-150-2015.md` | LC 150/2015 — doméstico | 12 p., 63 artigos | [Planalto](https://www.planalto.gov.br/ccivil_03/leis/lcp/lcp150.htm) |
| `in-rfb-2110-2022.md` | IN RFB 2.110/2022 — tributação previdenciária | 130 p., 277 artigos | [sijut2consulta](http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=127178) |
| `in-rfb-2058-2021.md` | IN RFB 2.058/2021 — processo de consulta | 10 p., 52 artigos | [sijut2consulta](http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=121555) |

Todos convertidos da pasta do Drive do usuário (consolidados em 06.05.2025) e
aprovados no diagnóstico de `_diagnostico.py`.

## Falta

**Decreto 3.048/1999 (RPS)** — o PDF do Drive tem 7 MB e o conector encerra a
sessão nesse tamanho (cinco tentativas). O caminho alternativo do conector
entrega o texto **truncado no art. 188** de 372, sem o art. 216 (arrecadação),
e por isso foi recusado. Saídas: salvar a página do Planalto em `.htm`
(`Ctrl+S`, alguns MB menor), dividir o PDF em duas metades, ou colar num
Documento Google.

## As duas patologias que o diagnóstico pega

Ambas silenciosas — o texto entregue parece perfeito:

1. **Extração corrompida.** PDF com fonte sem mapa de caracteres: sai `/0 /1 /2`
   e nenhum "Art." é encontrado. Caso real: `Decreto-lei 200-67.pdf`, 32
   páginas, zero artigos. Nem extrator profissional recupera — a informação de
   qual glifo é qual letra não está no arquivo.
2. **Extração truncada.** O leitor devolve só o começo. Pior que a primeira,
   porque o trecho entregue está impecável e nada denuncia a falta. Casos
   reais: o Decreto 3.048 parou no art. 188; a Constituição, lida pelo mesmo
   caminho, parou no art. 156 — sem os arts. 195 e 201.

`_diagnostico.py` mede a proporção de caracteres plausíveis (pega a primeira)
e procura buracos na numeração dos artigos (pega a segunda), distinguindo
truncamento de revogação: a Lei 8.213 não tem os arts. 145-146 e o CTN não tem
os arts. 52-61 porque foram revogados, e ambos passam.

Quando souber o último artigo da norma, passe `--ate-artigo N` — é a
verificação mais direta contra truncamento.

## Como alimentar o corpus

Ponha a norma numa pasta do Drive e me diga qual. Eu leio pelo conector e
converto. Formatos:

| Formato | Situação |
|---|---|
| PDF de texto (até ~5 MB) | ✅ `de_pdf.py`, extração local com pypdf |
| Documentos Google | ✅ exporta markdown fiel |
| `.md` / `.txt` / `.htm` | ✅ bytes exatos, via `do_drive.py` |
| `.docx` | ✅ com perda de formatação |
| PDF acima de ~7 MB | ❌ o conector encerra a sessão |
| PDF digitalizado | ❌ precisa de OCR, indisponível aqui |

`de_pdf.py` exige pypdf. O pacote `cryptography` do sistema está quebrado
neste ambiente, então use um venv:

```bash
python3 -m venv .venv && .venv/bin/pip install pypdf
.venv/bin/python legislacao/de_pdf.py arquivo.pdf lei-8212-1991 --ate-artigo 105
```

## Como atualizar uma norma

Legislação muda. Um corpus antigo é mais perigoso que corpus nenhum: o texto
parece autoritativo e ninguém desconfia.

### 1. Ver o que está velho

```bash
python3 legislacao/status.py
```

Mostra a data de consolidação e a idade de cada norma, e alerta acima de 180
dias (`--limite N` muda o limiar).

### 2. Baixar de novo e reconverter

Pegue o texto atualizado na fonte oficial, ponha na mesma pasta do Drive e me
avise. Eu reconverto **por cima do arquivo existente** — é isso que faz o
passo 3 funcionar.

### 3. Ler o que mudou

Como o corpus está em git, a atualização produz um diff que mostra
exatamente qual dispositivo mudou:

```bash
git diff legislacao/lei-8212-1991.md          # o que mudou agora
git log --oneline legislacao/lei-8212-1991.md  # histórico da norma
git diff HEAD~3 -- legislacao/                 # mudanças das últimas 3 atualizações
```

Isso é melhor do que qualquer ferramenta de RAG entrega: não é "o que a lei
diz hoje", é **o que mudou e quando**, no nível do artigo. Para quem redige
solução de consulta e precisa saber a redação vigente à época do fato
gerador, o `git log` do arquivo é uma linha do tempo da norma.

Sempre atualize o carimbo ao reconverter:

```
<!-- consolidado-em: 2026-09-09 -->
```

### Defasagem conhecida em 09/09/2026

O corpus foi montado com PDFs de 06/05/2025 — 491 dias. Duas mudanças já
identificadas e **ausentes** dos arquivos:

- **LC 224/2025** (26/12/2025): a alíquota do produtor rural pessoa física do
  art. 25, I da Lei 8.212 passou de 1,2% para **1,32%** a partir de
  01/04/2026. O corpus ainda diz 1,2%.
- **IN RFB 2.321/2026** (06/04/2026): alterou a IN RFB 2.110/2022. O corpus
  tem a redação anterior.

Enquanto não atualizar, trate esses dois pontos com cuidado — e o resto do
corpus como provável, não certo.

## Como consultar

```bash
# texto literal de um dispositivo
sed -n '/^Art\. 22\./,/^Art\. 23\./p' legislacao/lei-8212-1991.md

# onde uma expressão aparece em todo o corpus
rg -n -i "salário de contribuição" legislacao/

# um artigo e o que vem logo depois
rg -n "^Art\. 195\." legislacao/constituicao-1988.md -A 12
```
