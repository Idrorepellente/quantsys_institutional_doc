# ===========================================================================
#  Lyra — documentazione
# ===========================================================================
#
#    make                 compila tutti e due i PDF
#    make sviluppatore    solo la guida dello sviluppatore
#    make utente          solo il manuale utente
#    make figure          compila le figure TikZ una per una (per vederle sole)
#    make guarda          ricompila a ogni salvataggio
#    make pulisci         toglie i file intermedi, tiene i PDF
#    make pulisci-tutto   toglie anche i PDF
#
#  Serve: una TeX Live con latexmk. Nient'altro — niente Python, niente
#  --shell-escape, nessun font da installare. È il motivo per cui il codice è
#  composto con listings e non con minted: una documentazione che non compila
#  sulla macchina di chi la riceve non è documentazione.
# ===========================================================================

LATEXMK  := latexmk
OPZIONI  := -pdf -interaction=nonstopmode -halt-on-error -file-line-error

DOCUMENTI := guida-sviluppatore manuale-utente
PDF       := $(addsuffix .pdf, $(DOCUMENTI))

# Ricompila quando cambia QUALUNQUE sorgente, non solo il file principale:
# latexmk da solo non sa che guida-sviluppatore.tex dipende da sessanta file
# sotto sviluppatore/.
SORGENTI := $(shell find comune sviluppatore utente figure -name '*.tex' 2>/dev/null)

.PHONY: all sviluppatore utente figure guarda pulisci pulisci-tutto controlla ascii

all: $(PDF)

sviluppatore: guida-sviluppatore.pdf
utente:       manuale-utente.pdf

guida-sviluppatore.pdf: guida-sviluppatore.tex $(SORGENTI)
	@echo "  ==> guida dello sviluppatore"
	@$(LATEXMK) $(OPZIONI) $<

manuale-utente.pdf: manuale-utente.tex $(SORGENTI)
	@echo "  ==> manuale utente"
	@$(LATEXMK) $(OPZIONI) $<

# Ogni figura si compila anche DA SOLA, in un PDF ritagliato: serve a vederla a
# schermo intero mentre la si corregge, senza ricompilare duecento pagine.
#
# I file in figure/tikz/ contengono SOLO il disegno — nessun \documentclass —
# perché devono poter essere inclusi nel documento. L'involucro standalone lo
# genera qui, al volo, e lo si butta subito dopo.
figure:
	@mkdir -p figure/tikz/pdf
	@for f in figure/tikz/*.tex; do \
	  n=$$(basename "$$f" .tex); \
	  printf '%s\n' \
	    '\documentclass[border=5pt]{standalone}' \
	    '\usepackage[T1]{fontenc}' \
	    '\usepackage[utf8]{inputenc}' \
	    '\IfFileExists{italian.ldf}{\usepackage[italian]{babel}}{\usepackage[italian,provide=*]{babel}}' \
	    '\usepackage{mathpazo}' \
	    '\usepackage[scaled=0.90]{helvet}' \
	    '\usepackage{etoolbox}' \
	    '\usepackage{textcomp}' \
	    '\input{comune/colori}' \
	    '\input{comune/stile-codice}' \
	    '\input{comune/stile-tikz}' \
	    '\input{comune/macro}' \
	    '\begin{document}' \
	    "\\input{figure/tikz/$$n}" \
	    '\end{document}' > figure/tikz/pdf/_$$n.tex; \
	  echo "  ==> $$n"; \
	  $(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error \
	    -outdir=figure/tikz/pdf "figure/tikz/pdf/_$$n.tex" >/dev/null 2>&1 \
	    && mv "figure/tikz/pdf/_$$n.pdf" "figure/tikz/pdf/$$n.pdf" \
	    || echo "      ERRORE: vedi figure/tikz/pdf/_$$n.log"; \
	done
	@rm -f figure/tikz/pdf/_*.aux figure/tikz/pdf/_*.fdb_latexmk \
	       figure/tikz/pdf/_*.fls figure/tikz/pdf/_*.tex
	@echo "  ==> PDF delle figure in figure/tikz/pdf/"

guarda:
	@$(LATEXMK) $(OPZIONI) -pvc guida-sviluppatore.tex

# Controllo di coerenza: i riferimenti rotti non fermano la compilazione, e un
# \ref{} a un'etichetta che non esiste finisce nel PDF come "??". Qui si
# vedono.
controlla: ascii all
	@echo "  ==> riferimenti irrisolti"
	@grep -h "undefined" *.log 2>/dev/null | sort -u || echo "      nessuno"
	@echo "  ==> righe troppo lunghe (overfull > 15pt)"
	@grep -h "Overfull \\\\hbox ([0-9]\{2,\}" *.log 2>/dev/null | \
	   sed 's/^/      /' | head -20 || echo "      nessuna"

# I blocchi di codice devono essere in puro ASCII: un carattere accentato li
# dentro ferma la compilazione con un messaggio che indica il file .listing
# intermedio e non dice quale blocco l'ha causato. Lo script spiega anche come
# si rimedia (translitterare, oppure usare l'ambiente `commento`).
ascii:
	@echo "  ==> caratteri non ASCII nei blocchi di codice"
	@python3 strumenti/controlla-ascii.py

pulisci:
	@$(LATEXMK) -c $(DOCUMENTI) >/dev/null 2>&1 || true
	@rm -f *.aux *.bbl *.blg *.fdb_latexmk *.fls *.idx *.ilg *.ind \
	       *.lof *.log *.lot *.out *.toc *.synctex.gz *.run.xml
	@rm -rf figure/tikz/pdf
	@echo "  ==> file intermedi rimossi"

pulisci-tutto: pulisci
	@rm -f $(PDF)
	@echo "  ==> PDF rimossi"
