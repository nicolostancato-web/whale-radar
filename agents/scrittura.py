"""Scrivere un file che qualcun altro sta leggendo.

PERCHE' ESISTE (5/11 mattina). I file di stato si scrivevano con un
`json.dump(dati, open(dove,"w"))` diretto. Sembra innocuo e non lo e': la
scrittura non e' istantanea, e chi legge in quella finestra trova il file a
META'. La lista corta la leggono OTTO agenti, fra cui la SENTINELLA -- quella
che compone i pacchetti -- e la sua ricostruzione dura minuti: in quella
finestra la sentinella non componeva NIENTE, in silenzio.
L'ho scoperto per caso, perche' una verifica e' diventata rossa con un errore
di lettura JSON proprio mentre la lista si riscriveva.

La regola: un file che altri leggono si SOSTITUISCE, non si riempie. Si
scrive di fianco e poi `os.replace`, che sul medesimo disco e' atomico.
"""
import json, os


def atomico(dati, dove, indent=None):
    tmp = dove + ".tmp"
    with open(tmp, "w") as f:
        json.dump(dati, f, indent=indent)
    os.replace(tmp, dove)
