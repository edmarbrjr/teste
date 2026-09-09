#!/usr/bin/env python3
"""Grava no corpus um arquivo vindo do Google Drive.

O Claude chama `download_file_content` (Drive MCP), que devolve o conteúdo em
base64, e canaliza esse base64 para este script:

    python3 legislacao/do_drive.py lei-8212-1991 --fonte "https://..." < base64.txt

Só stdlib. Normaliza quebras de linha e espaços não separáveis, preserva o
texto literal do dispositivo (nada de reescrita).
"""
import argparse
from datetime import date
import base64
import binascii
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _diagnostico import avaliar


def normalizar(txt: str) -> str:
    txt = txt.replace("\r\n", "\n").replace("\r", "\n")
    txt = txt.replace("\xa0", " ").replace("​", "")
    txt = re.sub(r"[ \t]+\n", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("nome", help="nome do arquivo sem extensão, ex.: lei-8212-1991")
    ap.add_argument("--fonte", default="", help="URL oficial da norma, para o cabeçalho")
    ap.add_argument("--drive-id", default="", help="id do arquivo no Drive, para rastreio")
    ap.add_argument("--consolidado-em", default=date.today().isoformat(),
                    help="data da consolidação do texto (padrão: hoje)")
    ap.add_argument("--ate-artigo", type=int, default=None,
                    help="número do último artigo da norma, se souber — detecta truncamento")
    ap.add_argument("--forcar", action="store_true", help="grava mesmo reprovando")
    args = ap.parse_args()

    b64 = "".join(sys.stdin.read().split())
    if not b64:
        print("[x] nada recebido na entrada padrão", file=sys.stderr)
        return 1
    try:
        bruto = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError) as e:
        print(f"[x] base64 inválido: {e}", file=sys.stderr)
        return 1

    for enc in ("utf-8", "latin-1"):
        try:
            texto = bruto.decode(enc)
            break
        except UnicodeDecodeError:
            continue
    else:
        print("[x] não consegui decodificar o texto", file=sys.stderr)
        return 1

    texto = normalizar(texto)
    if "�" in texto:
        print("[!] aviso: há caracteres de substituição — confira o encoding", file=sys.stderr)

    aprovado, msgs = avaliar(texto, args.ate_artigo)
    for m in msgs:
        print(f"    {m}")
    if not aprovado and not args.forcar:
        print("[x] reprovado no diagnóstico — não vou gravar texto incompleto "
              "ou corrompido.", file=sys.stderr)
        return 1

    cabecalho = ["<!-- corpus local; não substitui o texto oficial -->"]
    if args.fonte:
        cabecalho.append(f"<!-- fonte: {args.fonte} -->")
    cabecalho.append(f"<!-- consolidado-em: {args.consolidado_em} -->")
    if args.drive_id:
        cabecalho.append(f"<!-- drive: {args.drive_id} -->")

    arq = Path(__file__).parent / f"{args.nome}.md"
    arq.write_text("\n".join(cabecalho) + "\n\n" + texto, encoding="utf-8")

    print(f"[ok] {arq.name} — {len(texto):,} chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
