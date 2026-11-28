"""Un modello che INCROCIA tutte le caratteristiche, invece di due soglie contate a mano.

PERCHE' (23/09 notte). Il fondatore, giustamente: «abbiamo i modelli piu' forti del pianeta e ne
usciamo con «entriamo dopo due ore se ci sono 50 compratori»». Aveva ragione: non era troppo
semplice il metodo, erano troppo poveri i dati in ingresso — cinque contatori.

COSA FA. Regressione logistica con penalizzazione L2 su 33 caratteristiche (pressione,
concentrazione, accelerazione, forma del prezzo, struttura dei partecipanti), scritta a mano perche'
sul cloud non c'e' scikit-learn. Prevede: questo pool fara' +BERSAGLIO entro l'orizzonte?

COME SI GIUDICA, e qui sta tutto. Mai una divisione casuale: si addestra sul PASSATO e si giudica
sul FUTURO, perche' il 23/09 abbiamo imparato a caro prezzo che un risultato puo' battere il rumore
nello stesso campione e sparire nel periodo successivo. Il numero che conta non e' quanto il modello
spiega i dati su cui ha studiato, ma quanto guadagna il decimo migliore dei pool MAI VISTI.
"""
import gzip
import json
import math
import os
import sys

import numpy as np

CHAIN = os.environ.get("CHAIN", "robinhood")
BERSAGLIO = float(os.environ.get("BERSAGLIO", 0.5))
QUOTA_ADDESTRAMENTO = float(os.environ.get("QUOTA_ADDESTRAMENTO", 0.7))
PENALITA = float(os.environ.get("PENALITA", 1.0))
GIRI = int(os.environ.get("GIRI", 3000))


def carica():
    # IL FILE ORA E' COMPRESSO E LO RIFA' UNA CORSIA (25/09): prima lo costruivo a mano sul
    # portatile, ed e' andato perso con una pulizia del disco.
    p = f"data/loop1/insieme_{CHAIN}.jsonl.gz"
    righe = [json.loads(l) for l in gzip.open(p, "rt") if l.strip()]
    # SI ADDESTRA SOLO SU CIO' CHE E' GIUDICABILE (25/09). Un pool nato un'ora fa non ha ancora un
    # esito: dargliene uno insegna al modello il rumore dell'ultima ora di raccolta.
    # Il criterio e' l'eta' rispetto alla fine della raccolta, NON le ore in cui l'abbiamo visto
    # scambiare: quel secondo criterio scarta i pool morti, cioe' proprio le trappole, e fa
    # sembrare tutto migliore di sette punti. Errore commesso e corretto lo stesso giorno.
    righe = [r for r in righe if r.get("_giudicabile")]
    if not righe:
        print(f"MODELLO | {CHAIN}: nessun pool giudicabile", flush=True)
        raise SystemExit(0)
    nomi = sorted(k for k in righe[0] if not k.startswith("_"))
    righe.sort(key=lambda r: r["_t"])                 # ORDINE TEMPORALE: e' il punto
    X = np.array([[float(r[k]) for k in nomi] for r in righe], dtype=float)
    # SI PREVEDE L'USCITA, NON IL PREZZO (25/09). `_rend` e' il prezzo all'orizzonte: un numero a
    # cui qualcuno COMPRAVA. `_uscita` e' il prezzo mediano di chi ha VENDUTO, cioe' cio' che si
    # incassa davvero. Sullo stesso campione i due differiscono di ventidue punti.
    # Un modello bravissimo a prevedere un prezzo non incassabile non serve a niente.
    y = np.array([1.0 if r["_uscita"] >= BERSAGLIO else 0.0 for r in righe])
    rend = np.array([r["_uscita"] for r in righe])
    X = np.clip(np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0), -1e12, 1e12)
    return nomi, X, y, rend


def addestra(X, y, penalita, giri):
    """Discesa del gradiente con penalizzazione: pesi piccoli, meno illusioni."""
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    passo = 0.5
    for _ in range(giri):
        z = X @ w + b
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))
        g = p - y
        gw = X.T @ g / n + penalita * w / n
        gb = g.mean()
        w -= passo * gw
        b -= passo * gb
    return w, b


def prevedi(X, w, b):
    return 1.0 / (1.0 + np.exp(-np.clip(X @ w + b, -30, 30)))


def auc(y, s):
    """Probabilita' che un pool vincente abbia punteggio piu' alto di uno perdente."""
    o = np.argsort(s)
    r = np.empty(len(s))
    r[o] = np.arange(1, len(s) + 1)
    n1 = y.sum()
    n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return 0.5
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def main():
    nomi, X, y, rend = carica()
    n = len(y)
    taglio = int(n * QUOTA_ADDESTRAMENTO)
    Xa, ya = X[:taglio], y[:taglio]
    Xp, yp, rp = X[taglio:], y[taglio:], rend[taglio:]
    mu, sd = Xa.mean(0), Xa.std(0)
    sd[sd == 0] = 1.0                                  # media e scala dal SOLO addestramento
    w, b = addestra((Xa - mu) / sd, ya, PENALITA, GIRI)
    sa = prevedi((Xa - mu) / sd, w, b)
    sp = prevedi((Xp - mu) / sd, w, b)
    print(f"\n=== {CHAIN}: {n} pool, {len(nomi)} caratteristiche, bersaglio +{100*BERSAGLIO:.0f}% ===")
    print(f"   addestrato sui primi {taglio}, giudicato sugli ultimi {n-taglio} (MAI VISTI)")
    print(f"   capacita' di ordinare — su cui ha studiato: {auc(ya,sa):.3f} | "
          f"sul futuro: {auc(yp,sp):.3f}   (0,5 = come tirare a caso)")
    base = yp.mean()
    print(f"\n   {'gruppo (dal peggiore al migliore)':<36} | {'fanno il bersaglio':>18} | {'rendimento medio':>17}")
    ordine = np.argsort(sp)
    for k in range(5):
        idx = ordine[k * len(ordine) // 5:(k + 1) * len(ordine) // 5]
        q = yp[idx].mean()
        rmed = np.mean(1 + rp[idx]) - 1
        print(f"   {k+1}° quinto ({len(idx)} pool){'':<14} | {100*q:>17.1f}% | {100*rmed:>16.1f}%")
    dieci = ordine[-max(1, len(ordine) // 10):]
    print(f"\n   il DECIMO migliore ({len(dieci)} pool): {100*yp[dieci].mean():.1f}% "
          f"fanno il bersaglio contro il {100*base:.1f}% di tutti "
          f"-> {yp[dieci].mean()/max(base,1e-9):.1f} volte")
    print(f"   rendimento medio del decimo migliore: {100*(np.mean(1+rp[dieci])-1):+.1f}% "
          f"| di tutti: {100*(np.mean(1+rp)-1):+.1f}%")
    print(f"\n   le dieci caratteristiche che pesano di piu':")
    for i in np.argsort(-np.abs(w))[:10]:
        print(f"      {nomi[i]:<30} {w[i]:+.3f}")


if __name__ == "__main__":
    main()
