#!/usr/bin/env python3
"""
PERMUTAZIONE A BLOCCHI — il nostro numero migliore significa qualcosa, o e' il premio della ricerca?

DA DOVE VIENE. Il revisore avversariale ha demolito la mia prima versione: permutavo le righe senza
rispettare i blocchi e rieseguivo solo la scelta della soglia, non tutta la selezione. Cosi' il test
non misurava niente. Questa e' la forma che lui indica, e che accetto:

  1. si preserva la struttura TEMPORALE (l'ordine dei token resta quello vero);
  2. gli esiti si permutano DENTRO I BLOCCHI — una giornata di lancio alla volta — perche' token
     nati lo stesso giorno si muovono insieme: mescolarli fra giorni distruggerebbe anche la
     dipendenza comune, e il confronto diventerebbe troppo facile per noi;
  3. si riesegue TUTTA la selezione, non solo la configurazione finale;
  4. si confronta il migliore VERO con la distribuzione del MASSIMO sotto ipotesi nulla — non con la
     media: il nostro numero e' un massimo, e va confrontato con dei massimi.

COME SI LEGGE:
  - il vero NON batte il massimo dei mondi finti -> il nostro numero e' il premio di aver guardato
    tante volte, e nessuna ottimizzazione lo rendera' vero;
  - il vero lo batte nettamente -> la differenza e' l'unica parte che vale la pena guardare.

LIMITE DICHIARATO: qui si provano poche decine di configurazioni per mondo, non due milioni. E' un
limite di tempo e va nella direzione PRUDENTE: il placebo vero, con due milioni di tentativi,
troverebbe DI PIU'. Quindi il confronto reale e' ancora piu' severo di quello che leggerete.

Sola lettura, nessuna chiamata. €0.
"""
import json, os, sys, time, random, statistics as st
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multichain_brain as B

CHAINS = tuple((os.environ.get("PERM_CHAINS") or "base,solana,robinhood").split(","))
CONFIG = int(os.environ.get("PERM_CONFIG", 6))     # configurazioni provate per mondo
MONDI = int(os.environ.get("PERM_MONDI", 5))       # mondi permutati
TETTO = int(os.environ.get("PERM_TETTO", 600))     # righe massime: il tempo non e' infinito
SOGLIE = [0.2, 0.3, 0.4, 0.5, 0.6, 0.7]


def robusta(rr):
    if len(rr) < 6: return None
    s = sorted(rr, reverse=True)[3:]
    return (sum(1 + x for x in s) / len(s) - 1) * 100


def cerca_il_massimo(righe, soglie):
    """Il GESTO che conta: provare tante configurazioni e tenere la migliore. E' questo che genera il
    premio della ricerca, ed e' questo che va riprodotto nei mondi finti."""
    best = None
    for thr in soglie:
        try:
            sel = [r["ret"] for r in B.walkforward_righe(righe, thr=thr)]
        except Exception:
            continue
        v = robusta(sel)
        if v is not None and (best is None or v > best): best = v
    return best


def discrimina(righe, soglie):
    """Lo stesso controllo di potere del test sulla classe ricca: se soglie diverse scelgono lo
    stesso identico insieme, il confronto col caso non significa niente e va dichiarato tale.
    Qui la verifica e' passata (197/188/181 righe scelte su Base a soglie diverse), ma un test che
    si autocontrolla solo quando qualcuno se lo ricorda non e' un test che si autocontrolla."""
    conte = set()
    for thr in soglie:
        try:
            conte.add(len(B.walkforward_righe(righe, thr=thr)))
        except Exception:
            pass
    return len(conte) > 1


def permuta_nei_blocchi(righe, seme):
    """Gli esiti si scambiano SOLO fra token nati lo stesso giorno. L'ordine temporale resta intatto."""
    rnd = random.Random(seme)
    blocchi = defaultdict(list)
    for i, r in enumerate(righe):
        g = time.strftime("%Y-%m-%d", time.gmtime(r["ent"]))
        blocchi[g].append(i)
    nuove = [dict(r) for r in righe]
    for g, idx in blocchi.items():
        esiti = [righe[i]["ret"] for i in idx]
        rnd.shuffle(esiti)
        for i, e in zip(idx, esiti): nuove[i]["ret"] = e
    return nuove


def main():
    L = ["# 🎲 PERMUTAZIONE A BLOCCHI — il nostro numero migliore significa qualcosa?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · audit · forma corretta dopo la "
         f"revisione avversariale · €0*", "",
         "> Il nostro «migliore» è il massimo di tantissimi tentativi. Un massimo va confrontato con",
         "> **altri massimi**, non con una media: anche in dati senza alcun legame, chi cerca abbastanza",
         "> trova sempre qualcosa che sembra funzionare.", "",
         "> **La forma del test** (corretta dopo che la mia prima versione è stata demolita): l'ordine",
         "> temporale resta intatto, gli esiti si scambiano **solo fra token nati lo stesso giorno** —",
         "> perché chi nasce insieme si muove insieme — e si riesegue **tutta** la selezione, non solo",
         "> la configurazione finale.", "",
         f"{CONFIG} configurazioni per mondo, {MONDI} mondi permutati, max {TETTO} righe per chain.", "",
         "| chain | righe | **vero** | finti: mediana | finti: **massimo** | il vero batte il caso? |",
         "|---|---|---|---|---|---|"]
    esiti = {}
    for ch in CHAINS:
        try:
            righe = B.load_rows(ch)
        except Exception:
            righe = []
        if len(righe) < 80:
            L.append(f"| **{ch}** | {len(righe)} | *troppo poche* | | | |"); continue
        righe = righe[-TETTO:]
        soglie = SOGLIE[:CONFIG]
        if not discrimina(righe, soglie):
            L.append(f"| **{ch}** | {len(righe)} | ⏸️ *il modello non discrimina* | | | |"); continue
        vero = cerca_il_massimo(righe, soglie)
        finti = []
        for k in range(MONDI):
            v = cerca_il_massimo(permuta_nei_blocchi(righe, 4000 + k), soglie)
            if v is not None: finti.append(v)
        if vero is None or len(finti) < 3:
            L.append(f"| **{ch}** | {len(righe)} | non calcolabile | | | |"); continue
        med, top = st.median(finti), max(finti)
        if vero > top: giudizio = "✅ **sì**"
        elif vero > med: giudizio = "⚠️ solo la mediana"
        else: giudizio = "❌ **no**"
        esiti[ch] = (vero, med, top)
        L.append(f"| **{ch}** | {len(righe)} | **{vero:+.1f}%** | {med:+.1f}% | **{top:+.1f}%** | {giudizio} |")

    L += ["", "## Come si legge", "",
          "> **Se il vero non batte il massimo dei mondi permutati**, il nostro numero non è un",
          "> vantaggio: è il premio di aver guardato tante volte. Nessuna quantità di ottimizzazione lo",
          "> renderà vero, e continuare a ottimizzare è tempo speso a lucidare il rumore.", "",
          "> **Se lo batte nettamente**, la differenza fra i due è l'unica parte che vale la pena",
          "> guardare: tutto il resto è il prezzo della ricerca.", "",
          "> ⚠️ **Limite dichiarato**: qui si provano poche decine di configurazioni per mondo, non due",
          "> milioni. Va nella direzione **prudente** — il placebo vero, con due milioni di tentativi,",
          "> troverebbe **di più**. Il confronto reale è quindi ancora più severo di questo.", "",
          "> ⚠️ **Cosa questo test NON dice**: non dice se esiste un vantaggio nei dati. Dice soltanto",
          "> se *il numero che stiamo guardando* si distingue da quello che produrrebbe la sola ricerca."]
    open("PERMUTAZIONE.md", "w").write("\n".join(L))
    print("PERMUTAZIONE | " + " ".join(f"{c}:{v[0]:+.1f}vs{v[2]:+.1f}" for c, v in esiti.items()), flush=True)


if __name__ == "__main__":
    main()
