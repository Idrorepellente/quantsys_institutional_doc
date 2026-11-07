#!/usr/bin/env python3
"""Genera la tabella di riferimento delle rotte HTTP della dashboard.

PERCHE' E' GENERATA E NON SCRITTA A MANO
Sono 246 percorsi su undici moduli. Una tabella trascritta a mano e' vera il
giorno in cui la si scrive e falsa tre settimane dopo, e una tabella di
riferimento falsa e' peggio di una tabella assente: la si consulta invece di
leggere il codice.

Qui si rilegge il sorgente e si riscrive il file .tex. Se il numero in fondo
alla tabella non coincide con quello che si trova nel progetto, la tabella e'
vecchia: si rilancia questo script.

USO
    python3 strumenti/genera-rotte.py /percorso/del/progetto
    python3 strumenti/genera-rotte.py            # prova ../progetto e ../app

Scrive:  sviluppatore/09-riferimento/rotte-generate.tex
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

ROTTA = re.compile(r'@(?:app|bp)\.route\(\s*(["\'])(?P<path>.*?)\1(?P<rest>[^)]*)\)')
METODI = re.compile(r"methods\s*=\s*\[(?P<m>[^\]]*)\]")
DEF = re.compile(r"\s*def\s+(\w+)")

# L'ordine in cui i moduli compaiono nella tabella: lo stesso in cui
# create_app() li monta, cosi' la tabella si legge accanto alla figura
# dell'assemblaggio.
ORDINE = ["app.py", "studio.py", "community.py", "marketplace_routes.py",
          "agent.py", "genetic.py", "auth.py",
          "ui_ext_a.py", "ui_ext_b.py", "ui_ext_e.py", "ui_ext_f.py"]

TITOLI = {
    "app.py": "app.py --- il nucleo",
    "studio.py": "studio.py --- blueprint \\cod{studio}",
    "community.py": "community.py --- blueprint \\cod{community}",
    "marketplace_routes.py": "marketplace\\_routes.py --- sul blueprint \\cod{community}",
    "agent.py": "agent.py --- blueprint \\cod{agent}",
    "genetic.py": "genetic.py --- blueprint \\cod{genetic}",
    "auth.py": "auth.py --- dentro \\cod{init\\_auth(app)}",
    "ui_ext_a.py": "ui\\_ext\\_a.py --- estensione v2",
    "ui_ext_b.py": "ui\\_ext\\_b.py --- estensione v2",
    "ui_ext_e.py": "ui\\_ext\\_e.py --- estensione v2",
    "ui_ext_f.py": "ui\\_ext\\_f.py --- estensione v2",
}


def esc(t: str) -> str:
    for a, b in (("\\", r"\textbackslash{}"), ("_", r"\_"), ("&", r"\&"),
                 ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
                 ("{", r"\{"), ("}", r"\}"), ("^", r"\textasciicircum{}"),
                 ("~", r"\textasciitilde{}")):
        t = t.replace(a, b)
    return t


def spezzabile(t: str) -> str:
    """Un percorso lungo deve poter andare a capo: senza, la colonna straborda
    e LaTeX lo segnala come overfull hbox invece di spezzarlo."""
    return esc(t).replace("/", r"/\allowbreak ")


def raccogli(radice: pathlib.Path) -> list[dict]:
    fuori = []
    for f in sorted((radice / "dashboard").glob("*.py")):
        testo = f.read_text(encoding="utf-8", errors="replace")
        righe = testo.split("\n")
        for i, riga in enumerate(righe):
            m = ROTTA.search(riga)
            if not m:
                continue
            met = METODI.search(m.group("rest"))
            metodi = ([x.strip().strip("\"'") for x in met.group("m").split(",")]
                      if met else ["GET"])
            funzione = ""
            for j in range(i + 1, min(i + 6, len(righe))):
                d = DEF.match(righe[j])
                if d:
                    funzione = d.group(1)
                    break
                if "@" not in righe[j] and righe[j].strip():
                    break
            fuori.append({"file": f.name, "path": m.group("path"),
                          "methods": metodi, "fn": funzione, "line": i + 1})
    return fuori


def main() -> int:
    qui = pathlib.Path(__file__).resolve().parent.parent
    if len(sys.argv) > 1:
        radice = pathlib.Path(sys.argv[1]).resolve()
    else:
        for tent in (qui.parent / "progetto", qui.parent / "app"):
            if (tent / "dashboard").is_dir():
                radice = tent
                break
        else:
            print("Non trovo il progetto. Passalo come argomento.", file=sys.stderr)
            return 2
    if not (radice / "dashboard").is_dir():
        print(f"{radice} non contiene dashboard/", file=sys.stderr)
        return 2

    rotte = raccogli(radice)

    # Un percorso, una riga: i metodi dichiarati in funzioni diverse si uniscono.
    per_file: dict[str, dict[str, dict]] = {}
    for r in rotte:
        voce = per_file.setdefault(r["file"], {}).setdefault(
            r["path"], {"methods": set(), "fn": set(), "line": r["line"]})
        voce["methods"].update(r["methods"])
        if r["fn"]:
            voce["fn"].add(r["fn"])

    out = [
        "% ===========================================================================",
        "%  GENERATO DA strumenti/genera-rotte.py --- non modificare a mano.",
        "%  Per aggiornarlo:  python3 strumenti/genera-rotte.py /percorso/del/progetto",
        "% ===========================================================================",
        "",
    ]
    totale = 0
    ordinati = ORDINE + sorted(set(per_file) - set(ORDINE))
    for nome in ordinati:
        voci = per_file.get(nome)
        if not voci:
            continue
        out.append(r"\subsection{%s}" % TITOLI.get(nome, esc(nome)))
        out.append(r"\begin{longtable}{@{}L{17mm}L{74mm}L{45mm}@{}}")
        out.append(r"\toprule")
        out.append(r"\textbf{Metodi} & \textbf{Percorso} & \textbf{Funzione} \\")
        out.append(r"\midrule\endfirsthead")
        out.append(r"\toprule")
        out.append(r"\textbf{Metodi} & \textbf{Percorso} & \textbf{Funzione} \\")
        out.append(r"\midrule\endhead")
        for i, (percorso, v) in enumerate(sorted(voci.items())):
            met = " ".join(sorted(v["methods"],
                                  key=lambda m: ["GET", "POST", "PUT",
                                                 "DELETE"].index(m)
                                  if m in ("GET", "POST", "PUT", "DELETE") else 9))
            fn = ", ".join(sorted(v["fn"])) or "---"
            riga = (r"\rigaTenue " if i % 2 else "")
            out.append(f"{riga}{{\\scriptsize\\sffamily {met}}} & "
                       f"{{\\ttfamily\\scriptsize {spezzabile(percorso)}}} & "
                       f"{{\\ttfamily\\scriptsize {esc(fn)}}} \\\\")
            totale += 1
        out.append(r"\bottomrule")
        out.append(r"\end{longtable}")
        out.append("")

    out.append(r"\begin{nota}{Quanti sono}")
    out.append(f"Questa tabella elenca \\num{{{totale}}} percorsi distinti, "
               f"da \\num{{{len(rotte)}}} decoratori \\cod{{@route}} su "
               f"\\num{{{len(per_file)}}} moduli. Se i numeri non coincidono con "
               r"quelli del progetto che si ha davanti, la tabella è vecchia: "
               r"si rigenera con \file{strumenti/genera-rotte.py}.")
    out.append(r"\end{nota}")

    dest = qui / "sviluppatore" / "09-riferimento" / "rotte-generate.tex"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"      {totale} percorsi, {len(rotte)} decoratori, "
          f"{len(per_file)} moduli -> {dest.relative_to(qui)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
