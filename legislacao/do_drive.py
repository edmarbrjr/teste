#!/usr/bin/env python3
"""Grava no corpus um arquivo vindo do Google Drive.

O Claude chama `download_file_content` (Drive MCP), que devolve o conteúdo em
base64, e canaliza esse base64 para este script:

    python3 legislacao/do_drive.py lei-8212-1991 --fonte "https://..." < base64.txt

Só stdlib. Normaliza quebras de linha e espaços não separáveis, preserva o
texto literal do dispositivo (nada de reescrita).
"""
import argparse
import base64
import binascii
import re
import sys
from pathlib import Path


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

    cabecalho = ["<!-- corpus local; não substitui o texto oficial -->"]
    if args.fonte:
        cabecalho.append(f"<!-- fonte: {args.fonte} -->")
    if args.drive_id:
        cabecalho.append(f"<!-- drive: {args.drive_id} -->")

    arq = Path(__file__).parent / f"{args.nome}.md"
    arq.write_text("\n".join(cabecalho) + "\n\n" + texto, encoding="utf-8")

    arts = len(re.findall(r"\bArt\.\s*\d+", texto))
    print(f"[ok] {arq.name} — {len(texto):,} chars, {arts} ocorrências de 'Art. N'")
    if arts == 0:
        print("[!] nenhum 'Art. N' encontrado — provável extração ruim (PDF?)", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
