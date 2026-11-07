"""Fonde i pezzi degli arbitraggi: l'intersezione delle UNIONI.

Una transazione e' arbitraggio se QUALCHE fetta ha visto un acquisto e QUALCHE fetta ha visto
una vendita — non necessariamente la stessa, perche' il bot compra in una pool e vende in
un'altra, e le due pool possono stare in fette diverse.
Quindi: unione di tutti i «compra», unione di tutti i «vende», e l'intersezione delle due.
L'operazione e' associativa: il parallelo non cambia il risultato.

E SI DICHIARA SE E' COMPLETO: se una fetta non ha finito i suoi file, l'elenco e' parziale e
chi lo usa deve saperlo. Un elenco parziale usato come completo lascia passare arbitraggi.
"""
import glob
import gzip
import json
import os
import sys
import time

CHAIN = os.environ.get("CHAIN", "base")
BASE = f"data/multichain/{CHAIN}"


def main():
    pezzi = sorted(glob.glob(f"{BASE}/arbitraggi_pezzo_*.json"))
    if not pezzi:
        print(f"FONDI ARBITRAGGI | nessun pezzo in {BASE}: niente da fondere")
        return 1
    compra, vende = set(), set()
    letti = totali = saltati = 0
    complete = 0
    for p in pezzi:
        try:
            d = json.load(open(p))
        except Exception:
            continue
        compra |= set(d.get("compra", []))
        vende |= set(d.get("vende", []))
        letti += d.get("file_letti", 0)
        saltati += d.get("senza_verso", 0)
        totali = max(totali, d.get("file_totali", 0))
        complete += 1 if d.get("fetta_completa") else 0
    arb = sorted(compra & vende)
    # DUE PARTIALITA' DIVERSE, E CONFONDERLE BLOCCA IL LAVORO (6/10).
    # Il criterio di prima confrontava i file LETTI col totale e dichiarava l'elenco parziale
    # all'80%. Ma i file non letti erano ZERO: il divario erano i pool di cui non conosciamo
    # il lato valuta, che vengono SALTATI per scelta — non per mancanza di tempo.
    # Sono due cose diverse: «non ho finito» si risolve con piu' budget, «non so interpretare
    # questo pool» no. Chiamarle con lo stesso nome avrebbe tenuto l'elenco bloccato come
    # inutilizzabile per sempre, mentre e' completo rispetto a cio' che sappiamo leggere.
    # Resta una partialita' vera e va dichiarata: un arbitraggio che passa per un pool
    # illeggibile non lo vediamo.
    processati = letti + saltati
    finito = complete == len(pezzi) and processati >= totali * 0.99
    quota_illeggibile = saltati / max(totali, 1)
    completo = finito
    fuori = f"{BASE}/arbitraggi.json.gz"
    json.dump({"quando": int(time.time()), "chain": CHAIN, "pezzi": len(pezzi),
               "fette_complete": complete, "file_letti": letti,
               "file_saltati_verso_ignoto": saltati, "file_totali": totali,
               "completo": completo, "quota_pool_illeggibili": round(quota_illeggibile, 4),
               "transazioni_con_acquisto": len(compra),
               "transazioni_con_vendita": len(vende),
               "da": arb}, gzip.open(fuori, "wt"))
    for p in pezzi:
        os.remove(p)
    print(f"FONDI ARBITRAGGI | {CHAIN}: {len(pezzi)} pezzi ({complete} fette complete), "
          f"{letti:,}/{totali:,} file letti")
    print(f"   transazioni con acquisto {len(compra):,} · con vendita {len(vende):,}")
    print(f"   ARBITRAGGI: {len(arb):,} = "
          f"{len(arb)/max(len(compra | vende),1):.1%} delle transazioni")
    print(f"   elenco {'COMPLETO su cio che sappiamo leggere' if completo else 'PARZIALE: fette non finite'}"
          f" → {fuori}")
    print(f"   ATTENZIONE: il {quota_illeggibile:.0%} dei pool ha il lato valuta ignoto ed e'"
          f" saltato. Un arbitraggio che passa di la' non lo vediamo: questa e' una"
          f" partialita' VERA, diversa dall'aver finito o no.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
