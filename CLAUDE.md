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

### Concluído e testado de ponta a ponta ✅

1. **`Início da Conversa`** (sistema): mensagem de boas-vindas personalizada →
   redirecionamento ao ZZ.
2. **`ZZ - Inicializador de Variáveis`**: nó único "Definir variáveis" com as 12
   atribuições + mensagem `[DEBUG] Variáveis inicializadas ✓` (temporária).
3. **`00 - Tipo de Consulta`**: 8 frases de gatilho (`quero fazer uma consulta`,
   `consulta sobre tributo`, `solução de consulta`, `dúvida sobre legislação
   tributária`, `iniciar consulta`, `começar`, `sim`, `vamos começar`);
   pergunta de múltipla escolha (2 opções); ramos gravam `Global.TipoConsulta`;
   mensagens `[DEBUG]` por ramo; redirecionamento aos dois ramos → `01`.
   Reconhecimento validado por clique, número (`1`/`2`) e texto.
4. **`01 - Tipo de Pessoa`**: sem frases de gatilho (alcançado só por
   redirecionamento); condição de entrada `Global.TipoConsulta = nbs`;
   - ramo NBS: pergunta de confirmação de PJ → `Sim` grava `TipoPessoa = "pj"`;
     `Não` exibe `[PLACEHOLDER] BLOQ - Legitimidade Material (pf_nbs)`;
   - ramo Interpretação ("Todas as outras condições"): pergunta "Quem é o
     consulente?" com 4 opções → grava `pf`/`pj`/`orgao`/`entidade`;
   - mensagem `[DEBUG] TipoPessoa:` no ponto de convergência.
   - Corrigido em 11/06/2026 via colagem do YAML completo
     (`topicos-gerados/01-TipodePessoa.yaml`). Defeitos eliminados: condição
     de entrada comparava `Global.TipoPessoa` (sempre vazia) em vez de
     `Global.TipoConsulta`; ramo `Sim` tinha `TipoPessoa = "pj"` como 2ª
     linha da CONDIÇÃO (comparação, nunca gravava). Estado final: ramo
     `Não` grava `MotivoBloqueio="pf_nbs"` + `StatusFluxo="bloqueado_insanavel"`
     antes do placeholder; convergência (DEBUG + ir para 02) vale para os
     dois ramos, sob guarda `StatusFluxo = "iniciado"`. Retestado: NBS+Sim →
     pergunta de confirmação → pj → tópico 02; NBS+Não → bloqueio sem vazar
     para o 02. Lição: gravação dentro de condição é armadilha recorrente
     (ver §7 item 4).
5. **`02 - Legitimidade Material`**: criado por colagem de YAML
   (`topicos-gerados/02-LegitimidadeMaterial.yaml`) e testado nos 3 ramos.
   Ramificação por `TipoPessoa`: pf OU pj (operador `||` — primeira condição
   com dois valores no mesmo ramo), `orgao`, `entidade`.
   - pf/pj: pergunta de sujeito passivo → Sim grava `SujeitoPassivo=true`;
     Não → `MotivoBloqueio="nao_sujeito_passivo"` + bloqueio insanável
     (placeholder BLOQ).
   - orgao: pergunta se o órgão é sujeito passivo → ambos os ramos gravam
     `SujeitoPassivo=true`; o ramo "não figura como sujeito passivo" exibe
     aviso citando arts. 18, 23 e 27 §1º (efeitos não alcançam o sujeito
     passivo; solução meramente informativa). ATENÇÃO: a redação difere do
     Blueprint §4.3 — a IN não cria "consulta informativa"; rótulo da opção
     e aviso foram corrigidos (arts. 14 §2º I, 23, 27 §1º). Usuário vai
     deliberar com os superiores se o ramo permanece.
   - entidade: 3 opções → nome próprio (true), associados COM autorização
     (true + lembrete de juntar a autorização), associados SEM autorização
     (`entidade_sem_autorizacao`, bloqueio insanável).
   - Convergência: DEBUG SujeitoPassivo/StatusFluxo sob guarda
     `StatusFluxo = "iniciado"` (padrão a repetir nos próximos).
     Em 12/06/2026 o placeholder da convergência foi substituído pelo
     redirecionamento real (`BeginDialog` → `...topic.03-QuemProtocola`).
6. **`03 - Quem Protocola`**: criado em 12/06/2026 pelo PRÓPRIO Claude Code
   via extensão Claude in Chrome (ver §8). YAML em
   `topicos-gerados/03-QuemProtocola.yaml`. Estrutura: mensagem prévia
   (regra "Alterar perfil de acesso", Blueprint §4.4) → condição
   `TipoPessoa = "pf"` (pergunta versão PF) / "Todas as outras condições"
   (pergunta versão PJ — vale também para orgao/entidade, A VALIDAR com o
   usuário se merece texto próprio); 4 opções por versão: proprio /
   procurador_rfb / terceiro SEM procuração (`terceiro_sem_procuracao`,
   bloqueio insanável) / terceiro COM procuração mas em nome próprio
   (`terceiro_nome_proprio`, bloqueio insanável). Convergência sob guarda:
   DEBUG QuemAssina + placeholder do 04 - DTE. Testado de ponta a ponta:
   PF→próprio (chega ao placeholder 04) e NBS→PJ→contador com procuração
   em nome próprio (bloqueia sem vazar). DEBUG imprime booleano como
   "Sim" no webchat (SujeitoPassivo:Sim = true, normal).
7. **`04 - DTE`**: YAML em `topicos-gerados/04-DTE.yaml`. Causa raiz do
   SystemError: ids de opção duplicados no mesmo tópico — ver §7.10.
   Versão final usa ids curtos únicos (`dte_ativo`, `dte_sn`, `sem_dte`,
   `nao_sei`, `recheck_sim`, `recheck_nao`). Mensagem de orientação
   conservadora (sem acentos/emojis) para evitar corrupção. Redirect
   do tópico 03 reconstruído via UI após erro "tópico não disponível"
   no Verificador (§7.9). Pendente: testar ponta a ponta.

Tópicos automáticos criados pelo Studio em pt-BR: `Obrigado`, `Recomeçar`,
`Saudação`, `Tchau` — **ainda não revisados** (ver pendências).

### Pendente 🔲

- Tópicos de triagem `02` a `10` (Legitimidade Material, Quem Protocola, DTE,
  Matriz/Filial, Competência Federal, Fato Determinado, Procedimento Fiscal,
  Decisão Anterior, Checklist Formal) — especificação completa no Blueprint §4.
- 5 tópicos `BLOQ -` (insanáveis) e 3 `SAN -` (sanáveis) + `FIM - Apto para
  Protocolo` — mensagens prontas no Blueprint.
- Substituir os `[PLACEHOLDER]` por redirecionamentos reais aos BLOQ/SAN.
- Próximo imediato: **`05 - Matriz ou Filial`** (após conclusão do 04).
- Validar com o usuário: no tópico 03, órgão/entidade caem na pergunta
  versão PJ ("Representante legal da PJ (perfil e-CNPJ)...") — o Blueprint
  §4.4 só especifica PF e PJ; decidir se órgão/entidade merecem texto próprio.
- Emendar o Blueprint §4.3 (ramo Órgão): trocar "consulta meramente
  informativa" pela redação correta (situação em que o órgão não figura como
  sujeito passivo — arts. 14 §2º I, 23 e 27 §1º). Usuário deliberará com os
  superiores se o ramo Órgão permanece no fluxo.
- Tópicos 09/10 (Checklist): decidir como registrar que órgão não sujeito
  passivo dispensa as declarações do art. 14 (§2º, I) — hoje o fluxo grava
  `SujeitoPassivo=true` genérico e perde essa informação.
- Remover todas as mensagens `[DEBUG]` antes da homologação.
- Compartilhar agente com a equipe (botão Compartilhar; agentes não são
  visíveis entre usuários sem compartilhamento explícito).
- Revisar tópicos automáticos `Saudação` e `Recomeçar` (conflito potencial
  com o fluxo).
- Re-exportar a solução como NÃO gerenciada e descompactar em `solucao/` —
  o zip atual (`Cosit_1_0_0_1_managed.zip`) é GERENCIADO (não serve como
  backup editável) e está defasado em relação ao Studio (anterior à correção
  do tópico 01). Obs.: o prefixo real do publisher no export é `cr7f3`, não
  `cosit` como planejado no §3 — verificar/ajustar o publisher da solução.
- Mensagens [DEBUG] com `[` de abertura faltando (aparece `DEBUG]`): ramo
  Interpretação do tópico 00 e convergência do tópico 01 — cosmético, serão
  removidas antes da homologação de toda forma.
- Discutir com TI: ambiente compartilhado (Sandbox) para a equipe; papéis de
  segurança (faixa de "privilégios insuficientes" apareceu no make.powerapps);
  fase 2 do Blueprint §11 (Dataverse/Power Automate/Power BI).
- Analytics customizado (Blueprint §6) e publicação (§7).

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
