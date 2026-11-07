#!/usr/bin/env python3
"""Segnala i caratteri non ASCII dentro i blocchi `codiceInterno`.

PERCHE' ESISTE
listings non sopporta UTF-8 nel corpo di un blocco di codice: la compilazione
si ferma con «Invalid UTF-8 byte sequence» e il messaggio indica il file
.listing intermedio, non il sorgente — quindi non dice quale blocco l'ha
causata. Su una guida con duecento blocchi, trovarlo a mano e' mezz'ora.

Qui si vede subito file e riga.

COSA FARE QUANDO SEGNALA QUALCOSA
Due strade, e la scelta dipende da cosa si sta citando:

  - e' CODICE con dentro una stringa accentata -> si translittera e si mette
    un commento accanto (`# nel sorgente: Naive con la dieresi`);

  - e' un COMMENTO in prosa, cioe' dieci righe di italiano che spiegano una
    decisione -> si usa l'ambiente `commento`, che e' testo LaTeX normale e
    quindi cita fedelmente accenti, virgolette e trattini.

    \\begin{commento}{dashboard/community.py:30}
    Il testo del commento, a capo come nel sorgente.
    \\end{commento}

USO
    python3 strumenti/controlla-ascii.py        # dalla radice del progetto
    make ascii
"""
from __future__ import annotations

import pathlib
import re
import sys

# Solo il CORPO: la riga \begin{...}{lingua}{didascalia}{file} e' testo LaTeX
# normale, e la didascalia e' in italiano — gli accenti li' dentro vanno
# benissimo. Segnalarli sarebbe rumore, e il rumore fa ignorare il controllo.
BLOCCO = re.compile(
    r"\\begin\{codiceInterno\}[^\n]*\n(?P<corpo>.*?)\\end\{codiceInterno\}",
    re.S,
)


def main() -> int:
    radice = pathlib.Path(__file__).resolve().parent.parent
    trovati = 0
    for percorso in sorted(radice.rglob("*.tex")):
        testo = percorso.read_text(encoding="utf-8")
        for blocco in BLOCCO.finditer(testo):
            fuori = sorted({c for c in blocco.group("corpo") if ord(c) > 127})
            if not fuori:
                continue
            riga = testo[: blocco.start("corpo")].count("\n") + 1
            rel = percorso.relative_to(radice)
            print(f"      {rel}:{riga}   {' '.join(fuori)}")
            trovati += 1

    if trovati:
        print(f"      {trovati} blocchi da correggere "
              f"(vedi il docstring di questo script)")
        return 1
    print("      nessuno")
    return 0


if __name__ == "__main__":
    sys.exit(main())
