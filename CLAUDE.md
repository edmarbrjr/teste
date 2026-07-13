# CLAUDE.md — Agente de Admissibilidade de Soluções de Consulta (Cosit/RFB)

> Contexto persistente do projeto para sessões do Claude Code.
> Última atualização: 11/06/2026.

## 1. O que é este projeto

Agente de triagem de admissibilidade de Soluções de Consulta da Receita Federal
do Brasil, construído no **Microsoft Copilot Studio**. Objetivo: reduzir
despachos decisórios de ineficácia causados por erros evitáveis dos
contribuintes antes e durante o protocolo da consulta no e-CAC.

O agente conduz o contribuinte por uma árvore de decisão (10 níveis de triagem)
que verifica os requisitos de admissibilidade da **IN RFB 2.058/2021**,
distinguindo erros **INSANÁVEIS** (ineficácia direta, sem correção) de
**SANÁVEIS** (intimação com 30 dias para retificar — art. 28, parágrafo único,
aplicável aos incisos I, II e XI a XIV do art. 27).

O agente **não responde mérito tributário** — apenas procedimento.
Orquestração 100% determinística (IA generativa desligada).

## 2. Documentos de referência (manter na pasta do projeto)

| Arquivo | Conteúdo |
|---|---|
| `Blueprint_Copilot_Studio_SC_RFB.md` | Especificação completa: 21+ tópicos, variáveis, mensagens prontas, analytics, cronograma |
| `IN_RFB_nº_20582021.pdf` | Norma de base (multivigente, com alterações até IN 2.183/2024) |
| `Anexo_I.docx` | Modelo de consulta — Pessoa Física |
| `Anexo_II.docx` | Modelo de consulta — Pessoa Jurídica |
| `Anexo_III.docx` | Modelo de consulta — Classificação NBS |
| `solucao/` (zip exportado, descompactado) | Fonte da verdade do agente atual; tópicos em YAML |

## 3. Ambiente e configuração do agente

- **Ambiente Power Platform:** `DEV-BOT-COSIT` (tipo Developer — pessoal; ambiente compartilhado é pendência)
- **Agente:** `Assistente de Admissibilidade de Consulta`
- **Idioma principal:** Português (Brasil) — definido na criação, imutável
- **Orquestração:** Clássica (generativa DESLIGADA)
- **Conhecimento geral da IA / Web search / upload de arquivos / code interpreter:** desativados
- **Reações 👍👎:** ativadas (alimentam métricas)
- **Solução:** `Cosit - Admissibilidade SC` (fornecedor/publisher `cosit`, prefixo `cosit`) — backup via exportação **não gerenciada** (.zip)
- **Autenticação:** nenhuma (público) — publicação futura via iframe no portal RFB

## 4. Arquitetura — variáveis globais (12)

Inicializadas a cada sessão pelo tópico `ZZ - Inicializador de Variáveis`
(chamado pelo Início da Conversa).

| Variável | Tipo | Inicial | Valores possíveis |
|---|---|---|---|
| `Global.TipoConsulta` | string | `""` | `interpretacao` \| `nbs` |
| `Global.TipoPessoa` | string | `""` | `pf` \| `pj` \| `orgao` \| `entidade` |
| `Global.SujeitoPassivo` | boolean | `false` | |
| `Global.QuemAssina` | string | `""` | `proprio` \| `procurador_rfb` \| `terceiro` |
| `Global.DTEAtivo` | boolean | `false` | |
| `Global.EMatriz` | boolean | `true` | |
| `Global.CompetenciaFederal` | boolean | `false` | |
| `Global.FatoDeterminado` | boolean | `false` | |
| `Global.SemFiscalizacao` | boolean | `false` | |
| `Global.SemDecisaoAnterior` | boolean | `false` | |
| `Global.StatusFluxo` | string | `"iniciado"` | `iniciado` \| `bloqueado_insanavel` \| `bloqueado_sanavel` \| `apto` |
| `Global.MotivoBloqueio` | string | `""` | código do motivo (ex.: `pf_nbs`, `nao_sujeito_passivo`, `fiscalizacao_em_curso`) |

**Códigos são sempre minúsculos, sem acento, sem espaço.**

## 5. Estado atual da construção

**Backup de referência:** `BackupAgentedeAdmissibilidade_1_0_0_3.zip` (não gerenciado).
**Fonte local dos YAMLs:** `topicos-gerados/` — 22 arquivos limpos (sem [DEBUG]), prontos para colar no editor de código do Studio.

### Fluxo completo construído e testado ✅

**Triagem (10 níveis):**

1. **`Início da Conversa`** → `ZZ` automaticamente (abertura sem gatilho).
2. **`ZZ - Inicializador de Variáveis`**: inicializa 12 variáveis → redireciona a `00`.
   YAML: `ZZ-InicializadordeVariveis.yaml`.
3. **`00 - Tipo de Consulta`**: pergunta (2 opções) → grava `TipoConsulta` → `01`.
   YAML: `00-TipodeConsulta.yaml`. Tópico é `OnRedirect` (alcançado só por redirect).
4. **`01 - Tipo de Pessoa`**: NBS→confirma PJ; Interpretação→4 opções. Grava
   `TipoPessoa`. YAML: `01-TipodePessoa.yaml`. Nome interno: `01-TipodePessoa`.
5. **`02 - Legitimidade Material`**: ramifica por `TipoPessoa` (pf/pj, orgao,
   entidade). Grava `SujeitoPassivo`. YAML: `02-LegitimidadeMaterial.yaml`.
6. **`03 - Quem Protocola`**: versão PF / PJ (inclui orgao/entidade). 4 opções
   por versão. Grava `QuemAssina`. YAML: `03-QuemProtocola.yaml`.
   Nome interno: `03-Quemprotocola`.
7. **`04 - DTE`**: PF recebe pergunta (sim/não/não sei+recheck); PJ/orgao/entidade
   recebem `DTEAtivo=true` automático. YAML: `04-DTE.yaml`.
   **Nome interno imutável: `teste4A`** — todas as refs usam `...topic.teste4A...`.
8. **`05 - Matriz ou Filial`**: PF pula (grava `EMatriz=true`); PJ/orgao/entidade
   recebem pergunta Sim/Não. YAML: `05-MatrizouFilial.yaml`.
9. **`06 - Competência Federal`**: 4 opções: federal, ICMS, ISS, IBS, não sei.
   CBS prossegue; IBS vai ao Comitê Gestor; ambos CBS+IBS pode prosseguir só CBS.
   YAML: `06-CompetenciaFederal.yaml`. Nome interno: `06-CompetnciaFederal`.
10. **`07 - Fato Determinado`**: concreto/determinado vs. hipótese genérica.
    YAML: `07-FatoDeterminado.yaml`. Correção aplicada: removido `BeginDialog` nu
    (código morto) fora do grupo de condições.
11. **`08 - Procedimento Fiscal`**: 3 opções (nenhum/em curso/espontaneidade
    readquirida). YAML: `08-ProcedimentoFiscal.yaml`.
12. **`09 - Decisão Anterior`**: 4 opções (nenhuma/decisão anterior/matéria
    normatizada/constitucionalidade). YAML: `09-DecisoAnterior.yaml`.
    Nome interno: `09-DecisoAnterior`.
13. **`10 - Checklist Formal`**: exibe checklist por Anexo (I/II/III); pergunta
    se todos os itens estão completos. YAML: `10-ChecklistFormal.yaml`.

**Destinos de bloqueio — insanáveis (5 BLOQs):**

- **`BLOQ - Legitimidade Material`**: cobre `pf_nbs`, `nao_sujeito_passivo`,
  `entidade_sem_autorizacao`. YAML: `BLOQ-LegitimidadeMaterial.yaml`.
- **`BLOQ - Processo Nome Terceiro`**: cobre `terceiro_sem_procuracao`,
  `terceiro_nome_proprio`. YAML: `BLOQ-ProcessoNomeTerceiro.yaml`.
- **`BLOQ - Fiscalização em Curso`**: cobre `fiscalizacao_em_curso`.
  YAML: `BLOQ-FiscalizaoemCurso.yaml`. Nome interno: `BLOQ-FiscalizaoemCurso`.
- **`BLOQ - Decisão Anterior`**: cobre `decisao_anterior`.
  YAML: `BLOQ-DecisoAnterior.yaml`. Nome interno: `BLOQ-DecisoAnterior`.
- **`BLOQ - Matéria Normatizada`**: cobre `materia_normatizada`,
  `constitucionalidade`. YAML: `BLOQ-MatriaNormatizada.yaml`.
  Nome interno: `BLOQ-MatriaNormatizada`.

Todos os BLOQs têm pergunta de reinício → ZZ → 00 (ou encerrar com despedida).

**Destinos de bloqueio — sanáveis (4 SANs):**

- **`SAN - DTE Ausente`**: orienta adesão ao DTE no e-CAC → se aderir, retoma
  em `05`. YAML: `SAN-DTEAusente.yaml`.
- **`SAN - Matriz ou Filial`**: orienta usar CNPJ da matriz → se confirmar,
  retoma em `06`. YAML: `SAN-MatrizouFilial.yaml`.
- **`SAN - Competência Errada`**: ICMS→SEFAZ / ISS→Município / IBS→cgibs.gov.br.
  Opção de refazer triagem. YAML: `SAN-CompetenciaErrada.yaml`.
  Nome interno: `SAN-CompetnciaErrada`.
- **`SAN - Fato Genérico`**: orienta reformulação com fato concreto → se
  reformulou, retoma em `08`. YAML: `SAN-FatoGenerico.yaml`.
  Nome interno: `SAN-FatoGenrico`.

**Conclusão positiva:**

- **`FIM - Apto para Protocolo`** (`IM-AptoparaProtocolo`): exibe checklist de
  aprovação + próximos passos por Anexo (I/II/III) + ressalva. Opção de reinício.
  YAML: `FIM-AptoparaProtocolo.yaml`. Nome interno: `IM-AptoparaProtocolo`.

**Bateria de 7+ testes aprovada:** fluxos PF/PJ/NBS até o FIM, BLOQs insanáveis
parando no lugar certo, SANs com retomada da triagem.

### Pendente 🔲

**Aplicar YAMLs limpos no Studio (pré-homologação):**
- Os 22 YAMLs em `topicos-gerados/` foram gerados sem [DEBUG] nesta sessão.
  O Studio ainda tem as versões COM [DEBUG] — é necessário colar os YAMLs limpos
  via editor de código (menu `...` do tópico → "Abrir o editor de códigos").
  Prioridade: fazer isso tópico a tópico, testando após cada colagem.
- Após aplicar o 07 limpo: verificar que o `BeginDialog` nu ao SAN-FatoGenrico
  (código morto) foi realmente removido pelo Studio (o YAML limpo já não o tem).

**Decisões pendentes com o usuário:**
- Validar: no tópico 03, órgão/entidade caem na pergunta versão PJ
  ("Representante legal da PJ (perfil e-CNPJ)...") — decidir se merecem texto
  próprio.
- Emendar Blueprint §4.3 (ramo Órgão): texto correto (arts. 14 §2º I, 23, 27 §1º)
  vs. "consulta meramente informativa" — decidir com os superiores se o ramo permanece.
- Tópicos 09/10: decidir como registrar que órgão não sujeito passivo dispensa
  declarações do art. 14 §2º I (hoje grava `SujeitoPassivo=true` genérico).
- Validar dispositivo legal exato do SAN Matriz/Filial (referência marcada como
  `[CONFERIR dispositivo exato com a Cosit antes da homologação]`).
- Validar nomes de Área de Concentração e Área Temática do e-CAC no FIM
  (tópico `IM-AptoparaProtocolo`) — estão preenchidos mas devem ser conferidos
  no e-CAC atual.

**Infraestrutura e publicação:**
- Compartilhar agente com a equipe (botão Compartilhar no Studio).
- Revisar tópicos automáticos `Saudação` e `Recomeçar` (conflito potencial com o fluxo).
- Discutir com TI: ambiente compartilhado (Sandbox); papéis de segurança;
  fase 2 do Blueprint §11 (Dataverse/Power Automate/Power BI).
- Analytics customizado (Blueprint §6) e publicação (§7).
- Re-exportar como NÃO gerenciada após aplicar todos os YAMLs limpos.
  Obs.: prefixo real do publisher é `cr7f3` (não `cosit` como planejado em §3).

## 6. Padrões e convenções de construção (IMPORTANTE)

### O "sanduíche" padrão de cada pergunta

```
Fazer uma pergunta (múltipla escolha, opções viram botões)
  └─ resposta salva em variável de TÓPICO, tipo choice
     (nome: resposta<Assunto>, ex.: respostaTipoPessoa)
Condição: resposta<Assunto> é igual a [OPÇÃO selecionada do dropdown]
  └─ Definir valor da variável: Global.<Variável> = fx "codigo"
  └─ (mensagem/redirecionamento do ramo)
```

- **Condição compara com a OPÇÃO** (texto exibido, escolhido no dropdown).
- **Gravação usa o CÓDIGO** (`"pf"`, `"nbs"`...) na variável global.
- Resposta de pergunta NUNCA vai direto para variável global string
  (incompatibilidade de tipo: EmbeddedOptionSet ≠ String).
- O ramo "Todas as outras condições" pode ficar vazio (a múltipla escolha
  reapresenta a pergunta até resposta válida).

### Valores em campos do Studio

- **Texto fixo digitado direto no campo:** SEM aspas (`nbs`, não `"nbs"`).
  Aspas digitadas em modo texto viram parte literal do valor — bug silencioso
  que quebra todas as comparações.
- **Editor de fórmula (fx):** strings COM aspas (`"nbs"`), booleanos sem
  (`true`/`false`). Booleanos SEMPRE via fx (digitado como texto vira string).
- Conferir o ícone `fx` na frente do campo para saber o modo ativo.

### Chips de variável nos nós

- **Setinha `>` na ponta do chip** = trocar QUAL variável o nó referencia.
- **Clique no corpo do chip** = abre Propriedades da variável (renomear ali
  renomeia no agente INTEIRO — perigo).

### Variáveis em mensagens

- Inserir via ícone `{x}` da barra de formatação da mensagem (vira chip).
  Digitar o nome como texto NÃO funciona.

### Tópicos alcançados só por redirecionamento

- Gatilho fica sem frases (ZZ, 01 em diante, BLOQ, SAN, FIM).
- Encadeamento: nó "Gerenciamento de tópicos → Ir para outro tópico".

### Testes

- Painel "Testar seu agente" → **Iniciar nova sessão** após CADA salvamento
  (o teste não recarrega sozinho).
- O popup `{x}` do painel de teste é **não confiável** nesta versão (mostra
  "Nenhuma variável usada" mesmo com variáveis ativas). Verificação oficial:
  **mensagens `[DEBUG]`** imprimindo as globais nos pontos-chave.
- Rastreamento visual: após um teste, abrir o tópico mostra ✓ nos nós
  executados.

## 7. Armadilhas conhecidas (lições aprendidas)

1. **Idioma principal é imutável** — definido na criação ("Configurações do
   agente (opcional)" no diálogo de nomeação). Agente criado em inglês teve
   de ser excluído e recriado.
2. **Duas abas/sessões do Studio no mesmo tópico** → Studio força criação de
   "(Copy)" e o fluxo passa a apontar para versão diferente da editada.
   Regra: UMA aba só. Se surgir "(Copy)", consolidar e excluir o excedente.
3. **Aspas literais em modo texto** (item 6) — já causou valor `"nbs"` com
   aspas embutidas.
4. **Gravar na global errada** — ramo Órgão chegou a gravar `TipoPessoa` em
   `TipoConsulta`, sobrescrevendo decisão anterior. Revisar variável + valor +
   fx de cada nó antes de salvar.
5. **Cache do navegador** pode corromper a sessão do Studio ("link desfeito",
   `SystemError`). Solução: outro navegador/janela anônima.
6. **Salvar antes de testar** — edições não salvas não rodam no teste.
7. Renomear variável global pelo painel de propriedades afeta o agente todo.
8. **Colagem no editor de código pode ser truncada** (YAML do tópico 02
   chegou cortado → pergunta sem opções, variável "unknown", erro "variável
   de resposta ausente"). Sempre conferir que a última linha colada é
   `outputType: {}` antes de salvar. Fluxo seguro: Claude Code salva o YAML
   em `topicos-gerados/` e copia para a área de transferência via `pbcopy`.
9. O nome interno do tópico (usado nas referências das condições) é gerado
   do nome de exibição no PRIMEIRO salvamento e não muda depois. Criar o
   tópico já com o nome definitivo antes de colar YAML com referências
   qualificadas (`...topic.02-LegitimidadeMaterial.main.question_X`).
10. **IDs de opção duplicados no mesmo tópico → `SystemError` em runtime.**
    Quando um tópico tem duas `Question` com `ClosedListEntity`, os `id`
    das opções precisam ser únicos no escopo do diálogo inteiro. Repetir
    o mesmo `id` em perguntas diferentes (ex.: `Não aderi ao DTE` em
    `question_dte` e em `question_dteRecheck`) é aceito pelo editor mas
    causa `SystemError` genérico no painel de teste — identificado como
    causa raiz do erro do tópico 04-DTE. Solução: usar ids curtos e
    distintos para cada pergunta (`dte_ativo`, `sem_dte`, `recheck_sim`,
    `recheck_nao`), nunca reutilizar o mesmo id dentro do mesmo tópico.

## 8. Fluxo de trabalho com o Claude Code

**ATUALIZAÇÃO 12/06/2026:** com a extensão **Claude in Chrome** conectada,
o Claude Code OPERA a interface do Copilot Studio diretamente (criou e
testou o tópico 03 sozinho). Receita que funcionou:

- Criar tópico em branco → renomear ANTES do 1º salvamento → salvar →
  menu Mais (⋯) → "Abrir o editor de códigos".
- Colagem do YAML: `pbcopy`/cmd+V NÃO alcançam a página via extensão e o
  `monaco` não é global. O que funciona: clicar no editor, `cmd+a`, e via
  javascript_tool despachar `ClipboardEvent('paste')` sintético com
  `DataTransfer` contendo o YAML na textarea `.monaco-editor textarea.inputarea`.
- Testes no painel: botão "Teste" → ícone "Iniciar nova sessão de teste"
  (CUIDADO: não confundir com o ícone ao lado, que abre a página
  "Avaliação") → ler o transcript via JS
  (`.webchat__basic-transcript__activity`) em vez de screenshots.
- Regra de UMA sessão por tópico continua valendo: não editar na aba do
  usuário enquanto o Claude edita na dele (badge "Editando" na lista de
  tópicos mostra quem está com o tópico aberto).

As pontes tradicionais (quando sem navegador):

1. **Editor de código YAML por tópico**: no Studio, menu `...` do tópico →
   abrir editor de código. Claude Code pode **gerar o YAML** de um tópico novo
   (usando os YAML do zip exportado como modelo de sintaxe) e o usuário cola
   no editor. Acelera muito a criação dos BLOQ/SAN (mensagens longas prontas
   no Blueprint).
2. **Zip da solução** (`Cosit - Admissibilidade SC`, exportação não
   gerenciada): contém todos os tópicos em YAML. Usar para: versionamento em
   git, diff entre versões, base de modelos, backup. Reimportável em qualquer
   ambiente (make.powerapps.com → Importar solução).
3. **Tarefas ideais para o Claude Code**: gerar YAML dos tópicos 02–10 e
   BLOQ/SAN/FIM a partir do Blueprint; revisar consistência de
   variáveis/códigos entre tópicos; preparar a bateria de 20 testes (§8 do
   Blueprint); gerar documentação; manter changelog.
4. **Sempre que gerar YAML**: respeitar nomes exatos das variáveis (§4),
   códigos minúsculos sem acento, e o padrão sanduíche (§6).
5. **Pasta `topicos-gerados/`**: cada YAML gerado/corrigido é salvo ali
   (fonte da verdade local, mais atual que o zip) e copiado para a área de
   transferência do usuário com `pbcopy < arquivo.yaml`. Prefixo real do
   publisher nas referências: `cr7f3_AssistentedeAdmissibilidadedeConsulta`.

## 9. Convenções de nomenclatura de tópicos

| Prefixo | Significado | Exemplos |
|---|---|---|
| `NN -` | Nível de triagem (ordem) | `00 - Tipo de Consulta`, `01 - Tipo de Pessoa` |
| `BLOQ -` | Bloqueio insanável | `BLOQ - Legitimidade Material` |
| `SAN -` | Alerta sanável | `SAN - DTE Ausente` |
| `FIM -` | Conclusão positiva | `FIM - Apto para Protocolo` |
| `ZZ -` | Utilitário interno | `ZZ - Inicializador de Variáveis` |

## 10. Regras de conteúdo das mensagens (do blueprint e da IN)

- Toda mensagem de bloqueio cita o artigo exato da IN RFB 2.058/2021.
- Sempre classificar: 🔴 INSANÁVEL ou 🟡 SANÁVEL (30 dias via intimação,
  art. 28, parágrafo único — hipóteses dos incisos I, II e XI a XIV do
  art. 27).
- Nunca declarar consulta "admissível" — apenas "aparentemente apta para
  protocolo", ressalvando que a admissibilidade formal é atribuição da Cosit.
- Linguagem formal, clara, acessível ao cidadão comum; jargão explicado.
- Prazo crítico a citar no FIM: 3 dias úteis para juntada após abertura do
  processo (art. 8º, §3º), sob pena de exclusão.

## 11. Ciclo de trabalho e economia de tokens

O trabalho é feito ETAPA POR ETAPA, um tópico por ciclo:

1. Gerar o YAML de UM único tópico (ordem: 02 → 10, depois BLOQ, SAN, FIM),
   seguindo §6 e usando os YAML de `solucao/` como modelo de sintaxe.
2. Entregar o YAML com instruções curtas: onde colar no editor de código do
   Copilot Studio e o que testar no painel de teste.
3. Aguardar a confirmação do usuário (resultado do teste ou erro).
4. Só então passar ao tópico seguinte.

Regras do ciclo:
- NUNCA gerar mais de um tópico por vez.
- Incluir mensagens [DEBUG] imprimindo as globais alteradas.
- Tópico de destino que ainda não existe → mensagem [PLACEHOLDER], não
  redirecionamento.
- Em divergência entre Blueprint e este arquivo, perguntar antes de decidir.
- Não reler a IN 2.058 (PDF) nem os Anexos a cada ciclo — consultar apenas
  quando a tarefa exigir o teor da norma. O Blueprint já contém as mensagens
  prontas.

Disciplina de tokens (lembrar o usuário ao fim de CADA ciclo):
- Sugerir rodar `/cost` para ver o consumo da sessão.
- Sugerir `/clear` antes de iniciar o próximo tópico — este CLAUDE.md é
  relido automaticamente, então nada do contexto essencial se perde.
- Tarefa mecânica (BLOQ/SAN: colar mensagens do Blueprint no molde) →
  sugerir `/model haiku` ou `/model sonnet`.
- Tarefa com lógica nova (primeira vez de um padrão, ex.: condição com
  dois valores) → sugerir modelo mais forte ou modo de planejamento.
- O usuário também pode usar `/model opusplan` (planeja com Opus, executa
  com Sonnet automaticamente).
