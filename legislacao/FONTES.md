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
| `in-rfb-2110-2022.md` | IN RFB nº 2.110/2022 | Normas gerais de tributação previdenciária e de arrecadação |
| `in-rfb-2058-2021.md` | IN RFB nº 2.058/2021 | Processo de consulta (já usada no projeto do agente) |

## Como entregar uma norma pelo Google Drive

O conector do Drive **não** passa pelo proxy de egresso que bloqueia o
Planalto neste ambiente — então o Drive é hoje a via que funciona.

**O formato importa mais que o conteúdo.** Testado nesta sessão:

| Formato no Drive | Resultado |
|---|---|
| **Documentos Google** | ✅ exporta markdown fiel |
| **`.md` / `.txt` / `.htm`** | ✅ bytes exatos |
| **`.docx`** | ✅ funciona, com perda de formatação |
| **`.pdf`** | ❌ **não use** |

O PDF falhou de forma grave: a extração de `Decreto-lei 200-67.pdf` devolveu
256 mil caracteres de mojibake, com **zero** ocorrências de "Art." — as fontes
embutidas usam encoding próprio e o texto sai ilegível. Um PDF assim passaria
despercebido num corpus grande e devolveria dispositivo errado numa citação.

Fluxo:

1. Você joga a norma numa pasta do Drive, em Documentos Google ou `.md`/`.htm`
   (o `.htm` salvo direto do Planalto serve).
2. Me diz o nome da pasta.
3. Eu leio pelo conector, converto com `do_drive.py` e comito em `legislacao/`.

O `do_drive.py` conta as ocorrências de `Art. N` e **falha** se não achar
nenhuma — é a rede de segurança contra extração corrompida como a do PDF acima.

## Como consultar

```bash
# texto literal de um dispositivo
rg -n "^\s*Art\. 22" legislacao/lei-8212-1991.md -A 40

# onde uma expressão aparece em todo o corpus
rg -n -i "salário de contribuição" legislacao/

# só as ementas/títulos
rg -n "^#{1,3} " legislacao/lei-8212-1991.md
```
