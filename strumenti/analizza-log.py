#!/usr/bin/env python3
"""Dice QUALE file ha prodotto ogni riga troppo lunga.

PERCHE' SERVE
Il log di LaTeX segnala «Overfull \\hbox (96pt too wide) in paragraph at lines
31--70», e quei numeri di riga sono relativi al file che era aperto in quel
momento — che il log non ripete. Con settanta file di sorgente, il messaggio
da solo non serve a niente.

Qui si segue l'annidamento delle parentesi del log, che e' come LaTeX dice
«sto aprendo questo file» e «l'ho chiuso», e si riattacca ogni avviso al suo
file.

USO
    python3 strumenti/analizza-log.py guida-sviluppatore.log [soglia_pt]
"""
from __future__ import annotations

import collections
import pathlib
import re
import sys

APRE = re.compile(r"\((?:\./)?([\w./\-]+\.(?:tex|sty|cls|def|ldf|cfg|fd))")
AVVISO = re.compile(r"Overfull \\hbox \((?P<pt>[\d.]+)pt too wide\)"
                    r"(?: in paragraph at lines (?P<righe>[\d\-]+))?")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    log = pathlib.Path(sys.argv[1])
    soglia = float(sys.argv[2]) if len(sys.argv) > 2 else 10.0

    pila: list[str] = []
    per_file: dict[str, list[tuple[float, str]]] = collections.defaultdict(list)

    for riga in log.read_text(encoding="utf-8", errors="replace").split("\n"):
        # L'annidamento: ogni '(' con un nome apre, ogni ')' chiude.
        i = 0
        while i < len(riga):
            c = riga[i]
            if c == "(":
                m = APRE.match(riga, i)
                if m:
                    pila.append(m.group(1))
                    i = m.end()
                    continue
                pila.append("?")
            elif c == ")" and pila:
                pila.pop()
            i += 1

        m = AVVISO.search(riga)
        if m and float(m.group("pt")) >= soglia:
            fonte = next((f for f in reversed(pila)
                          if f.endswith(".tex") and "texmf" not in f), "(ignoto)")
            per_file[fonte].append((float(m.group("pt")), m.group("righe") or "?"))

    if not per_file:
        print(f"      nessuna riga oltre {soglia:.0f}pt")
        return 0

    for f, voci in sorted(per_file.items(),
                          key=lambda kv: -max(p for p, _ in kv[1])):
        voci.sort(reverse=True)
        peggiori = ", ".join(f"{p:.0f}pt@{r}" for p, r in voci[:4])
        print(f"      {f}   ({len(voci)})  {peggiori}")
    print(f"      totale: {sum(len(v) for v in per_file.values())} "
          f"oltre {soglia:.0f}pt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
