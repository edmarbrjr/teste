"""Diagnóstico de qualidade e completude de texto legal extraído.

Duas patologias já observadas neste projeto, ambas silenciosas:

1. EXTRAÇÃO CORROMPIDA — PDF com fonte sem mapa de caracteres. O texto sai
   como `/0 /1 /2` e nenhum "Art." é encontrado (Decreto-lei 200/67).
2. EXTRAÇÃO TRUNCADA — o leitor devolve só o começo do documento. Pior que
   a primeira, porque o trecho entregue é perfeito e nada denuncia a falta.
   O Decreto 3.048/99 parou no art. 188 de 372, sem o art. 216 (arrecadação);
   a Constituição parou no art. 156, sem os arts. 195 e 201.

O truncamento é detectado por buracos na numeração dos artigos: um texto
legal íntegro tem sequência praticamente contínua.
"""
import re

RE_ARTIGO = re.compile(r"^Art\. ?(\d+)", re.MULTILINE)
PLAUSIVEIS = set(".,;:()§ºª-/\"'")


def numeros_de_artigo(texto: str) -> list[int]:
    return sorted({int(n) for n in RE_ARTIGO.findall(texto)})


def proporcao_plausivel(texto: str) -> float:
    if not texto:
        return 0.0
    bons = sum(1 for c in texto if c.isalnum() or c.isspace() or c in PLAUSIVEIS)
    return bons / len(texto)


def lacunas(numeros: list[int]) -> list[int]:
    """Números ausentes entre o primeiro e o último artigo encontrados."""
    if len(numeros) < 2:
        return []
    return [n for n in range(numeros[0], numeros[-1] + 1) if n not in set(numeros)]


def avaliar(texto: str, minimo_esperado: int | None = None) -> tuple[bool, list[str]]:
    """Retorna (aprovado, mensagens)."""
    nums = numeros_de_artigo(texto)
    prop = proporcao_plausivel(texto)
    faltando = lacunas(nums)
    msgs = []
    ok = True

    if not nums:
        msgs.append("nenhum 'Art. N' encontrado — extração provavelmente corrompida")
        return False, msgs

    ultimo = nums[-1]
    msgs.append(f"{len(nums)} artigos (até o art. {ultimo}), "
                f"{prop:.1%} de caracteres plausíveis")

    if prop < 0.90:
        msgs.append(f"caracteres implausíveis demais ({prop:.1%}) — fonte sem mapa?")
        ok = False

    if faltando:
        amostra = ", ".join(str(n) for n in faltando[:10])
        reticencias = "..." if len(faltando) > 10 else ""
        msgs.append(f"{len(faltando)} artigos ausentes na sequência: {amostra}{reticencias}")
        # buraco grande no fim = truncamento; buracos pequenos = revogações
        if len(faltando) > max(5, 0.25 * ultimo):
            msgs.append("buracos demais — provável TRUNCAMENTO, não revogação")
            ok = False

    if minimo_esperado and ultimo < minimo_esperado:
        msgs.append(f"termina no art. {ultimo}, mas era esperado ao menos o "
                    f"art. {minimo_esperado} — TRUNCADO")
        ok = False

    return ok, msgs
