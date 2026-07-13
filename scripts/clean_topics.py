#!/usr/bin/env python3
"""
Remove all [DEBUG] SendActivity nodes from topic YAMLs and fix known issues.
Outputs clean YAMLs to topicos-gerados/.
"""
import os
import re

BASE = "solucao/botcomponents/cr7f3_AssistentedeAdmissibilidadedeConsulta.topic."
OUT = "topicos-gerados/"

TOPIC_MAP = {
    "ZZ-InicializadordeVariveis": "ZZ-InicializadordeVariveis.yaml",
    "00-TipodeConsulta": "00-TipodeConsulta.yaml",
    "01-TipodePessoa": "01-TipodePessoa.yaml",
    "02-LegitimidadeMaterial": "02-LegitimidadeMaterial.yaml",
    "03-Quemprotocola": "03-QuemProtocola.yaml",
    "teste4A": "04-DTE.yaml",
    "05-MatrizouFilial": "05-MatrizouFilial.yaml",
    "06-CompetenciaFederal": "06-CompetenciaFederal.yaml",
    "07-FatoDeterminado": "07-FatoDeterminado.yaml",
    "08-ProcedimentoFiscal": "08-ProcedimentoFiscal.yaml",
    "09-DecisoAnterior": "09-DecisoAnterior.yaml",
    "10-ChecklistFormal": "10-ChecklistFormal.yaml",
    "IM-AptoparaProtocolo": "FIM-AptoparaProtocolo.yaml",
    "SAN-DTEAusente": "SAN-DTEAusente.yaml",
    "SAN-FatoGenrico": "SAN-FatoGenerico.yaml",
    "SAN-CompetnciaErrada": "SAN-CompetenciaErrada.yaml",
    "SAN-MatrizouFilial": "SAN-MatrizouFilial.yaml",
    "BLOQ-LegitimidadeMaterial": "BLOQ-LegitimidadeMaterial.yaml",
    "BLOQ-ProcessoNomeTerceiro": "BLOQ-ProcessoNomeTerceiro.yaml",
    "BLOQ-FiscalizaoemCurso": "BLOQ-FiscalizaoemCurso.yaml",
    "BLOQ-DecisoAnterior": "BLOQ-DecisoAnterior.yaml",
    "BLOQ-MatriaNormatizada": "BLOQ-MatriaNormatizada.yaml",
}

def get_indent(line):
    return len(line) - len(line.lstrip())

def is_list_item_start(line):
    stripped = line.lstrip()
    return stripped.startswith('- ')

def remove_debug_nodes(content, topic_name=""):
    """
    Remove SendActivity nodes whose activity contains [DEBUG].
    Also fixes known issues per topic.
    """
    lines = content.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]

        # Detect start of a list item: "    - kind: SendActivity"
        stripped = line.lstrip()
        if stripped.startswith('- kind: SendActivity'):
            indent = get_indent(line)
            # Collect all lines of this node (until next item at same indent level or shallower)
            block = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if next_line == '' or next_line == '\n':
                    block.append(next_line)
                    j += 1
                    continue
                next_stripped = next_line.lstrip()
                next_indent = get_indent(next_line)
                # If we hit another list item at same or shallower indent, or same-level key, stop
                if next_indent <= indent and (next_stripped.startswith('- ') or
                                               (next_indent < indent) or
                                               (next_indent == indent and not next_stripped.startswith(' '))):
                    break
                block.append(next_line)
                j += 1

            # Check if this block contains [DEBUG] in activity
            block_text = '\n'.join(block)
            # Match [DEBUG] or the malformed DEBUG] in activity field
            has_debug = bool(re.search(r'activity:\s*["\|].*(?:\[DEBUG\]|DEBUG\])', block_text, re.DOTALL))
            if not has_debug:
                # Check multi-line activity with [DEBUG]
                has_debug = bool(re.search(r'activity:\s*\|-?\s*\n\s*(?:\[DEBUG\]|DEBUG\])', block_text))

            if has_debug:
                # Skip this block (remove it)
                i = j
                # Remove trailing blank lines that were added to result
                while result and result[-1].strip() == '':
                    result.pop()
                continue
            else:
                result.extend(block)
                i = j
                continue

        # Special fix for topic 07: remove naked BeginDialog to SAN-FatoGenrico
        # at the very end (outside any condition group)
        if (topic_name == "07-FatoDeterminado" and
                stripped.startswith('- kind: BeginDialog') and
                i + 2 < len(lines) and
                'SAN-FatoGenrico' in lines[i+1] + (lines[i+2] if i+2 < len(lines) else '')):
            # Look ahead to confirm this is the naked one (not inside a condition)
            indent = get_indent(line)
            # Check: this item is at top-level actions indent (4 spaces)
            if indent == 4:
                # Skip this block
                j = i + 1
                while j < len(lines):
                    next_line = lines[j]
                    if next_line.strip() == '':
                        j += 1
                        continue
                    next_indent = get_indent(next_line)
                    if next_indent <= indent and lines[j].lstrip().startswith('- '):
                        break
                    if next_indent <= indent:
                        break
                    j += 1
                i = j
                # Remove trailing blank lines
                while result and result[-1].strip() == '':
                    result.pop()
                continue

        result.append(line)
        i += 1

    return '\n'.join(result)

os.makedirs(OUT, exist_ok=True)
stats = []

for topic_suffix, outfile in TOPIC_MAP.items():
    src = BASE + topic_suffix + "/data"
    dst = OUT + outfile

    with open(src) as f:
        original = f.read()

    cleaned = remove_debug_nodes(original, topic_suffix)

    # Count removals
    orig_debug = len(re.findall(r'\[DEBUG\]|DEBUG\]', original))
    clean_debug = len(re.findall(r'\[DEBUG\]|DEBUG\]', cleaned))
    removed = orig_debug - clean_debug

    with open(dst, 'w') as f:
        f.write(cleaned)

    stats.append((outfile, orig_debug, removed, clean_debug))

print("Topic                              | Original | Removed | Remaining")
print("-" * 70)
for name, orig, rem, remaining in stats:
    flag = " ⚠️" if remaining > 0 else ""
    print(f"  {name:<35} | {orig:>8} | {rem:>7} | {remaining:>9}{flag}")

total_removed = sum(r for _, _, r, _ in stats)
total_remaining = sum(rem for _, _, _, rem in stats)
print(f"\nTotal removed: {total_removed} | Remaining: {total_remaining}")
