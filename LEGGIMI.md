# Documentazione di Lyra

Due documenti, un progetto LaTeX.

| File | Che cos'è | A chi serve |
|---|---|---|
| `guida-sviluppatore.pdf` | Architettura, motore quantitativo, estensioni, rilascio. In italiano | A chi deve **modificare** Lyra |
| `user-guide.pdf` | La *User guide*, il manuale utente: che cosa fa ogni schermata e in quale ordine si usano. In inglese, come l'applicazione | A chi deve **usare** Lyra |

## Compilare

```
make                 # tutti e due i PDF
make sviluppatore    # solo la guida
make user            # solo la User guide (anche: make utente)
make figure          # ogni figura TikZ in un PDF ritagliato, per vederla sola
make controlla       # ASCII nei listati, riferimenti rotti, righe troppo lunghe
make guarda          # ricompila a ogni salvataggio
make pulisci         # toglie gli intermedi, tiene i PDF
```

Serve una TeX Live con `latexmk`. Nient'altro: niente Python per compilare,
niente `--shell-escape`, nessun font da installare. È il motivo per cui il
codice è composto con `listings` e non con `minted`.

### Due lingue, un preambolo

La guida dello sviluppatore è in italiano, la User guide in inglese
britannico; il preambolo in `comune/` è lo stesso. La lingua la sceglie il
file principale prima di includerlo:

```
\newcommand{\lyraLingua}{english}   % in user-guide.tex
\input{comune/preambolo}
```

Senza quella riga il documento è in italiano. La scelta decide babel, le
parole che le macro scrivono da sole (`\vediCap` scrive «capitolo» o
«Chapter») e il controllo della sillabazione qui sotto, che vale solo per
l'italiano. I titoli dei riquadri (`nota`, `attenzione`…) si scrivono a mano
nella lingua del documento.

### Se l'italiano non viene sillabato

I pacchetti `babel-italian` e i pattern di sillabazione italiani non sono in
tutte le installazioni. Il preambolo se la cava comunque — babel costruisce la
lingua dal proprio file `.ini` — ma **la sillabazione sta nel formato, non nel
pacchetto**: se manca, il testo viene spezzato con le regole inglesi e si vede.
Il log lo segnala con un avviso `Package lyra Warning`.

Per rimediare:

```
tlmgr install hyphen-italian babel-italian   # TeX Live completa
apt install texlive-lang-italian             # Debian / Ubuntu
fmtutil-sys --byfmt pdflatex                 # poi, in entrambi i casi
```

## Come è organizzato

```
comune/        preambolo, colori, stili, macro: condivisi dai due documenti
sviluppatore/  un capitolo per cartella, un file per sezione
user/          la User guide: un capitolo per cartella, in 00-chapter.tex
figure/tikz/   i disegni, uno per file
figure/schermate/  le immagini dell'applicazione
strumenti/     script di servizio (vedi sotto)
```

Il file `00-capitolo.tex` di ogni cartella contiene **solo** il titolo del
capitolo e l'elenco delle sue sezioni: nessun testo. Così si sposta una
sezione spostando un file, e due persone scrivono due sezioni dello stesso
capitolo senza toccare lo stesso file.

## Gli strumenti

| Script | A che serve |
|---|---|
| `strumenti/controlla-ascii.py` | Trova i caratteri non ASCII nei blocchi di codice, che fermano la compilazione con un messaggio che non dice dove |
| `strumenti/analizza-log.py` | Dice **quale file** ha prodotto ogni riga troppo lunga: il log di LaTeX non lo dice |
| `strumenti/genera-rotte.py` | Rigenera la tabella delle rotte HTTP leggendo il sorgente del progetto |

La tabella delle rotte nel capitolo di riferimento è **generata**, non
trascritta. Si aggiorna con:

```
python3 strumenti/genera-rotte.py /percorso/del/progetto
```

Se i numeri in fondo alla tabella non coincidono con quelli del progetto che
si ha davanti, la tabella è vecchia.

## Tre regole per chi scrive

1. **Nei blocchi di codice solo ASCII.** `listings` non sopporta UTF-8 nel
   corpo di un listato e l'errore indica un file intermedio, non il sorgente.
   Per citare un commento in italiano c'è l'ambiente `commento`, che è testo
   normale. `make controlla` segnala le violazioni.

2. **Dentro una figura TikZ si usa `\codT`, non `\cod`.** `\cod` è una
   `tcolorbox`, cioè una figura annidata: rompe lo stato di quella esterna e
   l'errore salta fuori sul nodo *successivo*.

3. **Un percorso lungo si scrive `\percorsoHTTP{}` o `\file{}`, non `\cod{}`.**
   `\cod` è una scatola indivisibile: in una colonna stretta sborda nel
   margine e non c'è niente che TeX possa fare.

## I quattro riquadri

| Ambiente | Significa |
|---|---|
| `nota` | Un chiarimento utile ma non necessario |
| `perche` | La ragione di una scelta che, vista da fuori, sembrerebbe potersi fare diversamente |
| `pratica` | Cosa fare, passo per passo |
| `attenzione` | Qui si rompe qualcosa: dati persi, denaro movimentato, o un errore che si scopre settimane dopo |

Sono quattro e devono restare quattro. Un documento con nove tipi di riquadro
è un documento in cui nessun riquadro significa qualcosa.

## Le schermate

Sono state fatte su un'installazione con **dati di esempio** generati al
calcolatore — non prezzi reali, non risultati di strategie. Il manuale lo dice
in apertura. Per rifarle serve una copia del progetto con dei dati dentro e
un browser pilotato da Playwright.
