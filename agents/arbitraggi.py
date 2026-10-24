"""L'elenco delle transazioni che sono ARBITRAGGIO, non posizioni. Costruito una volta sola.

PERCHE' SEPARATO (5/10). La prima correzione l'avevo messa dentro profitto_persone.py, e
aveva DUE difetti:
  · vedeva solo acquisto e vendita nella STESSA pool, mentre il bot compra nella pool A e
    vende nella pool B. L'agente legge un file di pool per volta, quindi il caso principale
    non poteva vederlo: ha catturato 2.400 arbitraggi su 50.000 posizioni, cioe' le briciole;
  · aggiungeva un secondo passaggio su tutte le righe, raddoppiando il lavoro — e cinque
    fette su otto sono morte per tempo scaduto.
Un difetto che attraversa i file non si corregge dentro un file che ne legge uno per volta.

COSA FA. Scorre TUTTE le pool e tiene, per ogni transazione, se quel portafoglio ha comprato
e se ha venduto — in qualunque pool. Se ha fatto entrambe le cose nella stessa transazione,
quella transazione e' un arbitraggio atomico: i gettoni non si sono fermati da lui, sono
passati da pool a pool.
Verificato sulla chain il 5/10: una transazione di questi bot aveva DIECI scambi su SEI pool,
quarantasei trasferimenti di gettoni e ZERO che toccassero il firmatario. E la domanda precisa
(trasferimenti di quel gettone per quel portafoglio, su tutto lo storico) ha dato ZERO per
sette casi su sette fra quelli che avevo riportato come vincenti.

NON SI CANCELLA NIENTE: l'elenco serve a ETICHETTARE, e gli arbitraggi si contano a parte.
COSTA ZERO CHIAMATE: legge i file degli scambi che abbiamo gia'.
"""
import glob
import gzip
import json
import os
import sys
import time

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import a_fette as AF                                              # noqa: E402
import verso as V                                                 # noqa: E402

CHAIN = os.environ.get("CHAIN", "base")
BUDGET = float(os.environ.get("BUDGET_SEC", 1080))
BASE = f"data/multichain/{CHAIN}"
CARTELLE = ("storico", "vivo", "trades")


def main():
    p = f"{BASE}/iniziatori.json.gz"
    if not os.path.exists(p):
        raise SystemExit(f"ARBITRAGGI | manca {p}: senza sapere chi ha firmato non si decide")
    mappa = {k.lower(): str(v).lower() for k, v in
             json.load(gzip.open(p, "rt")).get("da", {}).items()}
    # A FETTE, E L'INTERSEZIONE SI FA ALLA FUSIONE (5/10, secondo tentativo).
    # Il primo tentativo scorreva TUTTE le pool in un filo solo, «perche' l'elenco deve
    # vedere tutte le pool insieme»: 49.717 file, timeout, zero risultato.
    # Ma non serve vederle insieme nello stesso processo. Una transazione e' arbitraggio se
    # QUALCHE pool ha visto un acquisto e QUALCHE pool ha visto una vendita: quindi ogni
    # fetta emette i DUE INSIEMI che ha visto, e l'arbitraggio e' l'intersezione delle
    # UNIONI, calcolata quando si fondono i pezzi. L'operazione e' associativa, quindi il
    # parallelo non cambia il risultato.
    # «Deve vedere tutto insieme» era vero della DOMANDA, non del PROCESSO: confondere le due
    # cose mi e' costato un giro.
    file_tutti = []
    for c in CARTELLE:
        file_tutti += sorted(glob.glob(os.path.join(BASE, c, "*.jsonl.gz")))
    tutti_n = len(file_tutti)
    file_tutti = AF.mia_parte(file_tutti)
    i_f, n_f = AF.quale_fetta()
    print(f"ARBITRAGGI | {CHAIN} fetta {i_f+1}/{n_f}: {len(file_tutti):,} file su "
          f"{tutti_n:,}, {len(mappa):,} firmatari noti", flush=True)

    # per ogni transazione: ha comprato? ha venduto? — in qualunque pool
    compra, vende = set(), set()
    t0 = time.time()
    letti = senza_verso = 0
    for percorso in file_tutti:
        if time.time() - t0 >= BUDGET:
            print(f"   budget speso dopo {letti:,} file su {len(file_tutti):,}: "
                  f"l'elenco e' PARZIALE e si dichiara tale", flush=True)
            break
        pool = os.path.basename(percorso).split(".")[0]
        # QUI SERVE SOLO IL LATO, NON IL PREZZO (6/10). `valuta_lato` richiede che la valuta
        # sia in una lista fissa di cinque indirizzi, e saltava il 17,1% dei pool su base.
        # Ma per sapere se uno scambio e' un acquisto o una vendita il prezzo non serve:
        # serve solo quale dei due lati e' la valuta, e quello si ricava dalla FREQUENZA —
        # una valuta compare in migliaia di coppie, un memecoin in una o due.
        # Misurato: copertura dall'82,9% al 91,0% su base e dall'85,8% all'89,7% su robinhood.
        # Il prezzo resta legato alla lista fissa dove serve davvero (i dollari), perche'
        # inventarlo riprodurrebbe l'errore dei sedici milioni di dollari del 2/10.
        lato = V.lato_valuta_dai_dati(CHAIN, pool)
        if not lato:
            senza_verso += 1
            continue
        try:
            righe = [json.loads(l) for l in gzip.open(percorso, "rt") if l.strip()]
        except Exception:
            continue
        letti += 1
        for x in righe:
            tx = str(x.get("tx", "")).lower()
            if not tx or tx not in mappa:
                continue
            if V.quantita_lato(x, lato) <= 0:
                continue
            (compra if V.entra_valuta(x, lato) else vende).add(tx)
    completo = letti >= len(file_tutti) - senza_verso
    pezzo = AF.nome_pezzo(BASE, "arbitraggi")
    json.dump({"quando": int(time.time()), "chain": CHAIN,
               "file_letti": letti, "file_della_fetta": len(file_tutti),
               "file_totali": tutti_n, "senza_verso": senza_verso,
               "fetta_completa": completo,
               "compra": sorted(compra), "vende": sorted(vende)},
              open(pezzo, "w"))
    arbitraggi = compra & vende
    print(f"   file letti {letti:,}/{len(file_tutti):,} della fetta "
          f"({senza_verso:,} senza verso noto)", flush=True)
    print(f"   transazioni con un acquisto {len(compra):,} · con una vendita {len(vende):,}",
          flush=True)
    print(f"   arbitraggi visibili DENTRO questa fetta: {len(arbitraggi):,} "
          f"(il totale vero si sa solo fondendo i pezzi: un bot compra in una pool e vende "
          f"in un'altra, che puo' stare in un'altra fetta)", flush=True)
    print(f"   fetta {'completa' if completo else 'PARZIALE'} → {pezzo}", flush=True)


if __name__ == "__main__":
    main()
