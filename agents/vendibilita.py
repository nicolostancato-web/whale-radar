"""VENDIBILITA' — in questo pool qualcuno e' mai riuscito a USCIRE?

Terzo pezzo del loop 1. Idea presa dai bot per memecoin su Solana (22/09, ricerca su GitHub):
prima di comprare verificano che il token si possa RIVENDERE, perche' ne esistono di progettati
per farti entrare e non uscire.

PERCHE' CI RIGUARDA PIU' CHE A LORO. La revisione esterna ha messo al primo posto proprio questo:
    «Il picco puo' essere reale e il profitto irrealizzabile. Un acquisto riuscito seguito da una
     vendita impossibile non e' un candidato da scartare.»
Nel nostro conteggio, fino ad ora, un pool del genere risultava un GUADAGNO: vedevamo il prezzo
salire e contavamo la salita. Ma se nessuno e' mai riuscito a vendere, quella salita non era
incassabile da nessuno, tantomeno da noi.

COME LO MISURIAMO SENZA CHIEDERE NIENTE A NESSUNO. Loro interrogano servizi esterni a pagamento.
Noi abbiamo gia' il dato: ogni scambio registra chi l'ha fatto e in che direzione. Le quantita'
`a0`/`a1` hanno segno opposto a seconda del verso, quindi si puo' contare quanti indirizzi
DISTINTI hanno venduto davvero.

TRE CASI, E IL TERZO E' QUELLO CHE CI INTERESSA:
  - vendite da molti indirizzi diversi  -> pool normale, si esce
  - vendite solo dal creatore           -> sospetto: esce solo lui
  - nessuna vendita, o vendite da un solo indirizzo, con molti compratori  -> TRAPPOLA

IL LIMITE, DICHIARATO. «Nessuno ha venduto» non prova che sia impossibile vendere: magari nessuno
ha ancora voluto. Per questo il segnale si da' solo quando ci sono ABBASTANZA compratori: se in
cinquanta hanno comprato e nessuno e' mai uscito, l'ipotesi «non hanno voluto» diventa fragile.
E resta scritto come sospetto, non come certezza.
"""
import gzip
import json
import os
import sys

CHAIN = os.environ.get("CHAIN", "base")
MIN_COMPRATORI = int(os.environ.get("MIN_COMPRATORI", 20))
FUORI = f"data/loop1/vendibilita_{CHAIN}.json"


def verso(r):
    """Chi ha fatto questo scambio stava comprando o vendendo il token non-base?

    Il segno delle quantita' dice la direzione: una e' positiva (entra nel pool) e l'altra negativa
    (esce). Non serve sapere QUALE dei due token sia la valuta di base per contare chi esce: basta
    che i due versi siano distinti e coerenti dentro lo stesso pool."""
    try:
        a0 = float(r.get("a0") or 0)
    except Exception:
        return None
    if a0 == 0:
        return None
    return "A" if a0 > 0 else "B"


def main():
    cartelle = [f"data/multichain/{CHAIN}/{c}" for c in ("storico", "vivo")]
    per_pool = {}
    for c in cartelle:
        if not os.path.isdir(c):
            continue
        for fn in os.listdir(c):
            pool = fn.split(".")[0]
            try:
                righe = [json.loads(l) for l in gzip.open(os.path.join(c, fn), "rt") if l.strip()]
            except Exception:
                continue
            per_pool.setdefault(pool, []).extend(righe)

    esiti = {}
    trappole = sospetti = normali = pochi = 0
    for pool, righe in per_pool.items():
        lato = {"A": set(), "B": set()}
        for r in righe:
            v = verso(r)
            w = (r.get("w") or "").lower()
            if v and w:
                lato[v].add(w)
        # il lato con piu' indirizzi distinti e' quello dei compratori: su una memecoin i
        # compratori sono sempre molti piu' dei venditori
        if len(lato["A"]) >= len(lato["B"]):
            compratori, venditori = lato["A"], lato["B"]
        else:
            compratori, venditori = lato["B"], lato["A"]
        nc, nv = len(compratori), len(venditori)
        if nc < MIN_COMPRATORI:
            pochi += 1
            stato = "non misurabile"          # non si dichiara nulla: troppo pochi
        elif nv == 0:
            stato = "trappola"                # tanti entrati, nessuno uscito
            trappole += 1
        elif nv <= 2:
            stato = "sospetto"                # esce solo una manciata di indirizzi
            sospetti += 1
        else:
            stato = "normale"
            normali += 1
        esiti[pool] = {"compratori": nc, "venditori": nv, "stato": stato}

    os.makedirs(os.path.dirname(FUORI), exist_ok=True)
    json.dump(esiti, open(FUORI, "w"))
    tot = trappole + sospetti + normali
    print(f"VENDIBILITA' | {CHAIN}: {len(esiti)} pool esaminati")
    print(f"   non misurabili (meno di {MIN_COMPRATORI} compratori): {pochi}")
    if tot:
        print(f"   normali  (escono in molti):        {normali}  = {100*normali/tot:.1f}%")
        print(f"   sospetti (escono in uno o due):    {sospetti}  = {100*sospetti/tot:.1f}%")
        print(f"   TRAPPOLE (nessuno e' mai uscito):  {trappole}  = {100*trappole/tot:.1f}%")
        print()
        print(f"   Questi {trappole} pool, nel conteggio di prima, risultavano guadagni normali.")
        print(f"   Chi ci fosse entrato non avrebbe potuto incassare niente.")
    print(f"   scritto {FUORI}")
    if not tot:
        sys.exit(1)


if __name__ == "__main__":
    main()
