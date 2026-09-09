# Corpus de legislação previdenciária

Fonte da verdade local para consulta por `grep`/`rg`. Cada norma é baixada da
origem oficial e convertida para markdown por `baixar.py`.

Os arquivos `.md` NÃO são versionados como texto de referência jurídica
autêntica — para citação em documento oficial, confira sempre o texto no
endereço oficial da coluna URL.

## Núcleo previdenciário

| Arquivo | Norma | Ementa | URL oficial |
|---|---|---|---|
| `lei-8212-1991.md` | Lei nº 8.212/1991 | Custeio da Seguridade Social (Lei Orgânica) | https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm |
| `lei-8213-1991.md` | Lei nº 8.213/1991 | Planos de Benefícios da Previdência Social | https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm |
| `decreto-3048-1999.md` | Decreto nº 3.048/1999 | Regulamento da Previdência Social (RPS) | https://www.planalto.gov.br/ccivil_03/decreto/d3048.htm |
| `lei-9876-1999.md` | Lei nº 9.876/1999 | Contribuição do contribuinte individual, fator previdenciário | https://www.planalto.gov.br/ccivil_03/leis/l9876.htm |
| `lei-10666-2003.md` | Lei nº 10.666/2003 | Aposentadoria especial, retenção, RAT/FAP | https://www.planalto.gov.br/ccivil_03/leis/2003/l10.666.htm |
| `lei-12546-2011.md` | Lei nº 12.546/2011 | CPRB — desoneração da folha | https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12546.htm |
| `ec-103-2019.md` | EC nº 103/2019 | Reforma da Previdência | https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc103.htm |

## Normas infralegais (RFB)

O sijut2consulta também está bloqueado neste ambiente — entregue pelo Drive:

| Arquivo | Norma | Ementa |
|---|---|---|
| ✅ `in-rfb-2110-2022.md` | IN RFB nº 2.110/2022 | Normas gerais de tributação previdenciária e de arrecadação — 130 p., 282 artigos |
| ✅ `in-rfb-2058-2021.md` | IN RFB nº 2.058/2021 | Processo de consulta — 10 p., 52 artigos |

## Como entregar uma norma pelo Google Drive

O conector do Drive **não** passa pelo proxy de egresso que bloqueia o
Planalto e o sijut2consulta neste ambiente — então o Drive é a via que funciona.

Fluxo: você joga a norma numa pasta do Drive e me diz o nome dela. Eu leio pelo
conector, converto e comito em `legislacao/`.

### PDF funciona — depende do PDF

Existem dois tipos de PDF, e a diferença é invisível a olho nu:

| Tipo | Extração | Exemplo testado |
|---|---|---|
| **PDF de texto** (gerado por editor) | ✅ fiel | IN RFB 2.110/2022 — 130 páginas, 282 artigos, 99,9% limpo |
| **PDF com fonte sem mapa de caracteres** | ❌ ilegível | Decreto-lei 200/67 — 32 páginas, **zero** artigos, saída `/0 /1 /2 /3` |

Normas recentes da RFB, do Planalto e do DOU são do primeiro tipo. Documentos
antigos digitalizados ou com fonte incorporada mal-formada são do segundo — e
nem extrator profissional recupera, porque a informação de qual glifo é qual
letra não está no arquivo.

`de_pdf.py` mede isso e **recusa** o arquivo quando a extração falha (nenhum
`Art. N`, ou menos de 90% de caracteres plausíveis). Um PDF corrompido nunca
entra no corpus em silêncio.

Quando um PDF reprovar, as saídas são: salvar a página do Planalto direto em
`.htm` (`Ctrl+S`), colar num Documento Google, ou pedir o `.docx` na origem.

### Formatos aceitos

| Formato | Situação |
|---|---|
| **PDF de texto** | ✅ via `de_pdf.py`, com diagnóstico automático |
| **Documentos Google** | ✅ exporta markdown fiel |
| **`.md` / `.txt` / `.htm`** | ✅ bytes exatos, via `do_drive.py` |
| **`.docx`** | ✅ funciona, com perda de formatação |
| **PDF digitalizado** | ❌ precisa de OCR, não disponível neste ambiente |

## Como consultar

```bash
# texto literal de um dispositivo
rg -n "^\s*Art\. 22" legislacao/lei-8212-1991.md -A 40

# onde uma expressão aparece em todo o corpus
rg -n -i "salário de contribuição" legislacao/

# só as ementas/títulos
rg -n "^#{1,3} " legislacao/lei-8212-1991.md
```
