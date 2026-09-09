#!/usr/bin/env python3
"""Converte um PDF de norma em markdown greppável para o corpus.

    python3 legislacao/de_pdf.py arquivo.pdf in-rfb-2110-2022 --fonte "https://..."

Requer pypdf. O pacote `cryptography` do sistema está quebrado neste
ambiente, então instale num venv:

    python3 -m venv .venv && .venv/bin/pip install pypdf
    .venv/bin/python legislacao/de_pdf.py ...

QUALIDADE: nem todo PDF extrai. PDFs de texto (Planalto, DOU, normas RFB
recentes) saem fiéis. PDFs antigos com fontes sem mapa de caracteres saem
como lixo — o Decreto-lei 200/67 devolveu 58 mil caracteres sem um único
"Art.". O script mede isso e RECUSA o arquivo quando a extração falha,
para que texto corrompido nunca entre no corpus em silêncio.
"""
import argparse
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from _diagnostico import avaliar

try:
    import pypdf
except ImportError:
    sys.exit("[x] pypdf não instalado — veja o cabeçalho deste arquivo")

# hífen de quebra de linha: "contribui-\nção" -> "contribuição"
RE_HIFEN = re.compile(r"(\w)-\n(\w)")
# número de página solto numa linha
RE_PAGINA = re.compile(r"^\s*\d{1,4}\s*$", re.MULTILINE)


def extrair(caminho: Path) -> tuple[str, int]:
    leitor = pypdf.PdfReader(str(caminho))
    paginas = [p.extract_text() or "" for p in leitor.pages]
    return "\n\n".join(paginas), len(paginas)


def limpar(txt: str) -> str:
    txt = unicodedata.normalize("NFC", txt)
    txt = txt.replace("\xa0", " ").replace("​", "")
    txt = RE_HIFEN.sub(r"\1\2", txt)
    txt = RE_PAGINA.sub("", txt)
    txt = re.sub(r"[ \t]+", " ", txt)
    txt = re.sub(r" *\n *", "\n", txt)
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    # cada artigo começa em linha própria, para o grep pegar limpo
    txt = re.sub(r"(?<!\n)(Art\. \d+)", r"\n\1", txt)
    return txt.strip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", type=Path)
    ap.add_argument("nome", help="nome de saída sem extensão, ex.: in-rfb-2110-2022")
    ap.add_argument("--fonte", default="", help="URL oficial da norma")
    ap.add_argument("--ate-artigo", type=int, default=None,
                    help="número do último artigo da norma, se souber — detecta truncamento")
    ap.add_argument("--forcar", action="store_true", help="grava mesmo reprovando no diagnóstico")
    args = ap.parse_args()

    if not args.pdf.is_file():
        print(f"[x] não encontrei {args.pdf}", file=sys.stderr)
        return 1

    bruto, n_pag = extrair(args.pdf)
    texto = limpar(bruto)
    aprovado, msgs = avaliar(texto, args.ate_artigo)

    print(f"    {n_pag} páginas, {len(texto):,} chars")
    for m in msgs:
        print(f"    {m}")

    if not aprovado and not args.forcar:
        print("[x] extração reprovada — não vou gravar texto incompleto ou corrompido.\n"
              "    Consiga por outra via (página do Planalto salva em .htm, Documento\n"
              "    Google, PDF dividido) ou repita com --forcar se souber o que faz.",
              file=sys.stderr)
        return 1

    cabecalho = ["<!-- corpus local; não substitui o texto oficial -->",
                 f"<!-- extraído de {args.pdf.name} ({n_pag} páginas) -->"]
    if args.fonte:
        cabecalho.append(f"<!-- fonte: {args.fonte} -->")

    saida = Path(__file__).parent / f"{args.nome}.md"
    saida.write_text("\n".join(cabecalho) + "\n\n" + texto, encoding="utf-8")
    print(f"[ok] {saida.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
