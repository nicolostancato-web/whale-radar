"""IL METRO CONGELATO — quattro casi che devono dare sempre la stessa risposta.

PERCHE' ESISTE. In una settimana abbiamo ucciso otto strategie, e almeno quattro volte le abbiamo
uccise (o salvate) con uno STRUMENTO DI MISURA ROTTO:

 1. **il verso**: `a0 > 0` veniva letto come «vendita», ma quale token sia il memecoin dipende
    dall'ordine alfabetico degli indirizzi. Nel 73% dei pool contavamo gli ACQUISTI come vendite.
 2. **la taglia**: un prezzo a 10x sembrava un'uscita reale; a quel prezzo passavano 32 dollari.
 3. **la finestra**: misuravamo esiti a 24 ore su pool osservati sei.
 4. **il criterio di scarto**: «poche ore osservate» toglieva i pool MORTI, cioe' le trappole.

Ogni volta la scoperta e' arrivata giorni dopo, e nel frattempo abbiamo preso decisioni su numeri
falsi. Un difetto del metro non si vede guardando il risultato: **il risultato sembra sempre
plausibile.** E' per questo che serve un banco di prova con le risposte gia' note.

I quattro casi qui sotto sono costruiti a mano, con l'esito calcolato a penna. Se un giorno il
codice smette di darli, qualcosa nel metro si e' spostato — e lo si scopre PRIMA di pubblicare,
non tre giorni dopo aver deciso qualcosa.

Non e' un test di programmazione: e' un **campione di riferimento**, come il chilo di platino.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import verso as V                                              # noqa: E402

ESITI = []


def prova(nome, atteso, ottenuto, spiega=""):
    ok = atteso == ottenuto
    ESITI.append((ok, nome))
    print(f"   {'ok  ' if ok else 'ROTTO'} {nome}: atteso {atteso}, ottenuto {ottenuto} {spiega}")
    return ok


def main():
    print("METRO | i quattro casi congelati")

    # --- 1. IL VERSO. Stesso scambio, due pool con i token in ordine opposto.
    # Il memecoin entra nel pool = VENDITA. La valuta entra nel pool = ACQUISTO.
    meme_e_token0 = {"a0": 1000, "a1": -5}      # entra memecoin, esce valuta -> vendita
    prova("verso: memecoin=token0, memecoin che entra e' una VENDITA",
          True, V.e_vendita(meme_e_token0, meme_t0=True))
    prova("verso: memecoin=token1, gli stessi numeri sono un ACQUISTO",
          False, V.e_vendita(meme_e_token0, meme_t0=False),
          "(qui a0 e' la VALUTA che entra: qualcuno ha comprato)")

    # --- 2. IL PREZZO E' VALUTA PER MEMECOIN, mai l'inverso.
    # 1000 gettoni contro 5 di valuta -> 0,005 di valuta per gettone.
    prova("prezzo: valuta per memecoin quando il memecoin e' token0",
          0.005, V.prezzo(meme_e_token0, meme_t0=True))
    prova("prezzo: e l'inverso quando i token sono scambiati di posto",
          200.0, V.prezzo(meme_e_token0, meme_t0=False))

    # --- 3. LA TAGLIA. Il massimo incassabile deve venire dalle sole VENDITE, non da ogni prezzo.
    # Un acquisto a prezzo altissimo non e' un'uscita: e' qualcuno che entra caro.
    scambi = [
        {"a0": 100, "a1": -1},        # vendita a 0,01
        {"a0": -10, "a1": 5},         # ACQUISTO a 0,5 — prezzo altissimo, non incassabile
    ]
    vendite = [V.prezzo(x, True) for x in scambi if V.e_vendita(x, True)]
    prova("taglia: il prezzo alto di un ACQUISTO non entra fra le uscite",
          [0.01], vendite)

    # --- 4. LA VALUTA IN GIOCO. Su quale lato si conta il denaro.
    prova("valuta: si conta il lato della VALUTA, non quello del memecoin",
          5.0, V.valuta({"a0": 1000, "a1": -5}, meme_t0=True))

    rotti = [n for ok, n in ESITI if not ok]
    print()
    if rotti:
        print(f"METRO ROTTO in {len(rotti)} casi su {len(ESITI)}:")
        for n in rotti:
            print("   -", n)
        print("\nQualcosa nel metro si e' spostato. NON si pubblica finche' non torna.")
        return 1
    print(f"METRO | tutti i {len(ESITI)} casi tornano: il metro e' quello di ieri")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
