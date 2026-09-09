#!/usr/bin/env python3
"""Mostra a idade de cada norma do corpus e sinaliza as defasadas.

    python3 legislacao/status.py            # tabela
    python3 legislacao/status.py --limite 180   # muda o limiar de alerta

Legislação tributária e previdenciária muda o tempo todo. Um corpus antigo é
mais perigoso que corpus nenhum: o texto parece autoritativo e ninguém
desconfia. Este script existe para que a defasagem seja sempre visível.
"""
import argparse
import re
import sys
from datetime import date, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _diagnostico import numeros_de_artigo

RE_META = re.compile(r"<!--\s*([\w-]+):\s*(.*?)\s*-->")
LIMITE_PADRAO = 180  # dias


def ler_meta(texto: str) -> dict[str, str]:
    cabecalho = texto[:1000]
    return {k: v for k, v in RE_META.findall(cabecalho)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limite", type=int, default=LIMITE_PADRAO,
                    help=f"dias a partir dos quais alertar (padrão {LIMITE_PADRAO})")
    args = ap.parse_args()

    hoje = date.today()
    linhas = []
    defasadas = 0

    for md in sorted(Path(__file__).parent.glob("*.md")):
        if md.name == "FONTES.md":
            continue
        texto = md.read_text(encoding="utf-8")
        meta = ler_meta(texto)
        artigos = len(numeros_de_artigo(texto))
        bruto = meta.get("consolidado-em", "")
        try:
            consolidado = datetime.strptime(bruto, "%Y-%m-%d").date()
            idade = (hoje - consolidado).days
            alerta = "DEFASADA" if idade > args.limite else "ok"
            if idade > args.limite:
                defasadas += 1
            data_txt, idade_txt = consolidado.strftime("%d/%m/%Y"), f"{idade}d"
        except ValueError:
            alerta, data_txt, idade_txt = "SEM DATA", "—", "—"
            defasadas += 1
        linhas.append((md.stem, data_txt, idade_txt, str(artigos), alerta))

    largura = [max(len(l[i]) for l in linhas + [("norma", "consolidado", "idade", "arts", "situação")])
               for i in range(5)]
    cab = ("norma", "consolidado", "idade", "arts", "situação")
    print("  ".join(c.ljust(w) for c, w in zip(cab, largura)))
    print("  ".join("-" * w for w in largura))
    for l in linhas:
        print("  ".join(c.ljust(w) for c, w in zip(l, largura)))

    print()
    if defasadas:
        print(f"{defasadas} de {len(linhas)} normas passaram de {args.limite} dias.")
        print("Baixe de novo do Planalto/sijut, ponha na pasta do Drive e reconverta.")
        print("O git mostra exatamente o que mudou: git diff legislacao/")
    else:
        print(f"Todas as {len(linhas)} normas dentro de {args.limite} dias.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
