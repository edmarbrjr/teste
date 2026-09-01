#!/usr/bin/env python3
"""Baixa as normas listadas em FONTES.md do Planalto e converte para markdown.

Só stdlib. Rode de dentro da pasta do projeto:

    python3 legislacao/baixar.py

Se a rede do ambiente bloquear planalto.gov.br (403 no CONNECT), rode este
script na sua máquina local e comite os .md gerados.
"""
import html
import re
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

NORMAS = {
    "lei-8212-1991": "https://www.planalto.gov.br/ccivil_03/leis/l8212cons.htm",
    "lei-8213-1991": "https://www.planalto.gov.br/ccivil_03/leis/l8213cons.htm",
    "decreto-3048-1999": "https://www.planalto.gov.br/ccivil_03/decreto/d3048.htm",
    "lei-9876-1999": "https://www.planalto.gov.br/ccivil_03/leis/l9876.htm",
    "lei-10666-2003": "https://www.planalto.gov.br/ccivil_03/leis/2003/l10.666.htm",
    "lei-12546-2011": "https://www.planalto.gov.br/ccivil_03/_ato2011-2014/2011/lei/l12546.htm",
    "ec-103-2019": "https://www.planalto.gov.br/ccivil_03/constituicao/emendas/emc/emc103.htm",
}

DESCARTA = {"script", "style", "head", "meta", "link"}
QUEBRA = {"p", "br", "div", "tr", "li", "h1", "h2", "h3", "h4", "table"}


class Extrator(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.partes = []
        self.ignorando = 0

    def handle_starttag(self, tag, attrs):
        if tag in DESCARTA:
            self.ignorando += 1
        elif tag in QUEBRA:
            self.partes.append("\n")

    def handle_endtag(self, tag):
        if tag in DESCARTA and self.ignorando:
            self.ignorando -= 1
        elif tag in QUEBRA:
            self.partes.append("\n")

    def handle_data(self, data):
        if not self.ignorando:
            self.partes.append(data)

    def texto(self):
        return "".join(self.partes)


def limpar(bruto: str) -> str:
    ext = Extrator()
    ext.feed(bruto)
    txt = html.unescape(ext.texto())
    txt = txt.replace("\xa0", " ").replace("​", "")
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r" *\n *", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt.strip() + "\n"


def baixar(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        bruto = r.read()
    for enc in ("utf-8", "latin-1"):
        try:
            return bruto.decode(enc)
        except UnicodeDecodeError:
            continue
    return bruto.decode("utf-8", errors="replace")


def main() -> int:
    destino = Path(__file__).parent
    alvos = sys.argv[1:] or list(NORMAS)
    falhas = 0
    for nome in alvos:
        url = NORMAS.get(nome)
        if not url:
            print(f"[?] norma desconhecida: {nome}", file=sys.stderr)
            falhas += 1
            continue
        arq = destino / f"{nome}.md"
        try:
            texto = limpar(baixar(url))
        except Exception as e:  # rede bloqueada, 404, timeout...
            print(f"[x] {nome}: {e}", file=sys.stderr)
            falhas += 1
            continue
        arq.write_text(f"<!-- fonte: {url} -->\n\n{texto}", encoding="utf-8")
        print(f"[ok] {arq.name} ({len(texto):,} chars)")
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())
