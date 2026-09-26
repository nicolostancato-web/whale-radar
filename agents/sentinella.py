"""La sentinella: si accorge quando una corsia SMETTE DI PRODURRE pur non dando errori.

PERCHE' (25/09, dalla ricerca su come costruire meglio, delegata a Grok).
Tutti i guasti che ci hanno fatto perdere tempo in due giorni erano SILENZIOSI: la corsia girava,
usciva con successo, e non produceva niente. Nessun errore, nessun avviso.
 - le nascite giravano 1 volta invece di 15 (cron saltati)  -> scoperto dopo una notte
 - due raccolte si cancellavano a vicenda                    -> scoperto perche' un numero SCENDEVA
 - la restrizione non si applicava, 2,4 milioni invece di 600 mila -> scoperto leggendo i log

La regola che li unisce, scritta in positivo: **misura se il lavoro AVANZA, non se il processo
termina senza errori.** Un processo che finisce bene e non produce niente e' peggio di uno rotto,
perche' quello rotto almeno si vede.

COSA FA: per ogni archivio che ci interessa, confronta quanto conteneva l'ultima volta con quanto
contiene adesso. Se non e' cresciuto entro il tempo previsto, lo dice — e, se e' grave, avvisa su
Telegram.
"""
import gzip
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

STATO = "data/loop1/sentinella.json"

# archivio -> (ogni quanti minuti dovrebbe crescere, descrizione)
SORVEGLIATI = {
    "data/multichain/robinhood/iniziatori.json.gz": (90, "iniziatori robinhood"),
    "data/multichain/base/iniziatori.json.gz": (90, "iniziatori base"),
    "data/multichain/robinhood/hook.json": (90, "hook robinhood"),
    "data/multichain/base/hook.json": (90, "hook base"),
    "data/loop1/segnali.jsonl": (120, "previsioni"),
    # LA CORSIA NUOVA VA SORVEGLIATA COME LE ALTRE (26/09). `insieme.yml` e' nata stanotte e
    # ricostruisce i dati su cui si decide: se si ferma, le analisi continuano a girare sull'ultima
    # versione buona e nessuno se ne accorge — e' il modo peggiore di rompersi, perche' non sembra
    # rotto. Aggiungerla qui e' la condizione 2 dell'auto-apprendimento: un miglioramento si propaga
    # a tutti i pezzi simili nello stesso momento in cui lo si scopre.
    # Soglia larga (90 min) perche' la corsia gira ogni ~27 minuti ma la coda dei push puo' ritardarla.
    "data/loop1/insieme_robinhood.jsonl.gz": (90, "insieme robinhood"),
    "data/loop1/insieme_base.jsonl.gz": (90, "insieme base"),
}


def quanti(p):
    """Quante cose contiene. None se non si riesce a leggere — che NON e' zero."""
    if not os.path.exists(p):
        return None
    try:
        if p.endswith(".jsonl.gz"):
            # PRIMA DI QUESTA RIGA finiva nel ramo `.json.gz`, `json.load` si strozzava sulla seconda
            # riga e `quanti()` tornava None: il guardiano avrebbe detto «non riesco a leggere»
            # invece di contare. Un guardiano che non sa leggere cio' che sorveglia e' un guardiano
            # che tace (26/09, trovato mentre lo collegavo, non dopo).
            return sum(1 for l in gzip.open(p, "rt") if l.strip())
        if p.endswith(".json.gz"):
            d = json.load(gzip.open(p, "rt"))
            return len(d.get("da", d))
        if p.endswith(".json"):
            d = json.load(open(p))
            return len(d.get("hook", d.get("da", d)))
        return sum(1 for l in open(p) if l.strip())
    except Exception:
        return None


def main():
    ora = int(time.time())
    vecchio = {}
    if os.path.exists(STATO):
        try:
            vecchio = json.load(open(STATO))
        except Exception:
            vecchio = {}
    nuovo = {}
    fermi = []
    for p, (minuti, nome) in SORVEGLIATI.items():
        n = quanti(p)
        if n is None:
            print(f"SENTINELLA | {nome}: non leggibile, non giudico", flush=True)
            continue
        v = vecchio.get(p)
        nuovo[p] = {"n": n, "quando": ora}
        if not v:
            print(f"SENTINELLA | {nome}: prima misura, {n:,}", flush=True)
            continue
        passati = (ora - v["quando"]) / 60
        cresciuto = n - v["n"]
        if cresciuto < 0:
            fermi.append(f"{nome}: SCESO da {v['n']:,} a {n:,} — si sta cancellando lavoro")
        elif passati >= minuti and cresciuto == 0:
            fermi.append(f"{nome}: fermo a {n:,} da {passati:.0f} minuti (atteso entro {minuti})")
        else:
            print(f"SENTINELLA | {nome}: {n:,} (+{cresciuto:,} in {passati:.0f} min)", flush=True)
    # si conserva la misura precedente quando non e' passato abbastanza tempo
    for p, v in vecchio.items():
        if p in nuovo and (ora - v["quando"]) / 60 < SORVEGLIATI.get(p, (90,))[0]:
            nuovo[p] = v
    os.makedirs(os.path.dirname(STATO), exist_ok=True)
    json.dump(nuovo, open(STATO, "w"))
    if fermi:
        testo = "whale-radar: qualcosa si e' fermato senza dare errori.\n\n" + "\n".join(fermi)
        print("SENTINELLA | " + " | ".join(fermi), flush=True)
        try:
            import avvisa
            avvisa.avvisa(testo)
        except Exception:
            pass
        sys.exit(1)
    print("SENTINELLA | tutto avanza", flush=True)


if __name__ == "__main__":
    main()
