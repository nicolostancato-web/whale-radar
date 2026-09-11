#!/usr/bin/env python3
"""
RUBRICA — collega ogni POOL al suo TOKEN, per tutto l'archivio.

Il 02/09 e' venuto fuori che meta' del nostro database non si poteva usare, per un motivo banale:
i prezzi li salviamo per POOL, la sicurezza per TOKEN, e la rubrica che unisce i due copriva
250 pool su 3.475. Tutto il resto erano due mezzi dati che non si parlavano — candele senza
sapere di che token, e schede di sicurezza senza sapere che prezzo avesse fatto.

Qui la rubrica si riempie per TUTTI i pool di cui abbiamo le candele. DexScreener risolve 30 pool
per chiamata, senza chiave e senza costo. E' l'operazione con il miglior rapporto valore/prezzo
di tutto il progetto: non aggiunge un dato nuovo, rende utilizzabile quello che abbiamo gia'.

Idempotente: riparte da dove era e non richiede i pool gia' risolti. €0.
"""
import json, os, glob, time, urllib.request

CHAINS = os.environ.get("CHAINS", "base,bsc,solana,robinhood").split(",")
BUDGET = int(os.environ.get("BUDGET_SEC", 240))
PAUSA = 0.35                       # DexScreener: ~300 richieste/minuto, stiamo larghi
t0 = time.time()


def pool_con_candele(chain):
    out = []
    # "candles" e' la cartella vera delle candele: cercavamo solo i nomi italiani e quindi la
    # rubrica NON risolveva proprio i pool su cui poi si fanno tutte le analisi (03/09).
    for pat in ("candles", "serie", "candele", "pulse", "trades"):
        out += [os.path.basename(f).replace(".jsonl.gz", "")
                for f in glob.glob(f"data/multichain/{chain}/{pat}/*.jsonl.gz")]
    return list(dict.fromkeys(out))


def risolvi(chain, pools):
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/" + ",".join(pools)
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "wr"}),
                                    timeout=25) as r:
            d = json.loads(r.read())
    except Exception:
        return {}
    out = {}
    for p in (d.get("pairs") or d.get("pair") or []) if isinstance(d, dict) else []:
        pa = (p.get("pairAddress") or "").lower()
        tk = ((p.get("baseToken") or {}).get("address") or "")
        if pa and tk: out[pa] = tk
    return out


def main():
    tot_nuovi = 0
    for chain in CHAINS:
        f = f"data/multichain/{chain}/token_map.json"
        if not os.path.isdir(f"data/multichain/{chain}"): continue
        try: mappa = json.load(open(f))
        except Exception: mappa = {}
        # tutto in minuscolo: gli indirizzi EVM girano sia con le maiuscole di controllo sia senza,
        # e finche' le due forme convivevano nello stesso file l'aggancio falliva in silenzio.
        mappa = {k.lower(): v for k, v in mappa.items()}
        mancanti = [p for p in pool_con_candele(chain) if p.lower() not in mappa]
        nuovi = 0
        for i in range(0, len(mancanti), 30):
            if time.time() - t0 > BUDGET: break
            got = risolvi(chain, mancanti[i:i + 30])
            for k, v in got.items():
                if k not in mappa: mappa[k] = v; nuovi += 1
            time.sleep(PAUSA)
        json.dump(mappa, open(f, "w"))
        tot_nuovi += nuovi
        print(f"RUBRICA | {chain} | +{nuovi} risolti | rubrica ora {len(mappa)} | mancavano {len(mancanti)}",
              flush=True)
    print(f"RUBRICA | totale +{tot_nuovi}", flush=True)


if __name__ == "__main__":
    main()
