#!/usr/bin/env python3
"""
PULSE — il POLSO dei token giovani. Nasce da un collo strutturale: l'OHLCV gratis di GeckoTerminal ci rifiuta
il 60% delle chiamate anche a 1 ogni 6s (free tier saturo) → ~8 candele per run, mentre su Base nascono ~1400
pool/giorno. Cosi' i token FRESCHI non li vedevamo mai e il demo forward restava a secco.
Qui cambiamo strada: DexScreener risponde a 30 pool IN UNA chiamata in 0.2s (gratis, no chiave). Non da' lo
storico, ma noi non ne abbiamo bisogno: il motore gira ogni 30 min, quindi le candele dei giovani ce le
COSTRUIAMO IN AVANTI campionandoli. Ogni punto porta anche buys/sells (il FLOW) senza scaricare i trade.
Scrive data/multichain/<chain>/pulse/<addr>.jsonl.gz (append, stesso formato dei candele). €0.
"""
import urllib.request, json, gzip, os, time, datetime, glob

CHAINS = {"solana": "solana", "bsc": "bsc", "base": "base"}   # nomi chain su DexScreener
DS = "https://api.dexscreener.com/latest/dex/pairs"
BATCH = 30                 # indirizzi per chiamata (limite DexScreener)
MAX_AGE_H = 96             # seguiamo un token gia' iniziato per i primi 4 giorni: dopo, o e' partito o e' morto
NUOVI_MAX_H = 4            # ne INIZIAMO di nuovi solo se hanno meno di 4h: l'entrata e' a +2h dalla nascita,
                           # prenderne uno gia' vecchio significherebbe averlo perso
MIN_LIQ = 5000             # sotto $5k di liquidita' non e' tradeabile: non sprechiamo righe
MAX_POOLS = 1200           # tetto per chain per run (tiene il repo leggero)
PAUSE = 0.25               # ~4 chiamate/s, molto sotto il limite DexScreener
now = int(time.time())


def age_h(p):
    c = p.get("created")
    if c:
        try:
            return (now - datetime.datetime.strptime(c, "%Y-%m-%dT%H:%M:%SZ")
                    .replace(tzinfo=datetime.timezone.utc).timestamp()) / 3600
        except Exception: pass
    return (now - p.get("seen", now)) / 3600


def get(url):
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "wr"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read())
    except Exception:
        return None


def main():
    tot = 0
    for chain, dsname in CHAINS.items():
        base = f"data/multichain/{chain}"
        pf = f"{base}/pools.json"
        if not os.path.exists(pf): continue
        pools = json.load(open(pf))
        # 1) chi stiamo GIA' seguendo va continuato: senza il seguito perdiamo il prezzo d'uscita, cioe' il
        #    risultato del trade. 2) poi i nuovi nati, i piu' giovani per primi (vanno presi entro ~2h).
        gia = {os.path.basename(f).replace(".jsonl.gz", "") for f in glob.glob(f"{base}/pulse/*.jsonl.gz")}
        seguiti = [a for a, p in pools.items() if a in gia and age_h(p) <= MAX_AGE_H]
        nuovi = [a for a, p in pools.items() if a not in gia and age_h(p) <= NUOVI_MAX_H]
        # GARANZIA DI LAVORO: se non ci sono pool freschissimi (su Solana quelli sotto le 4 ore erano ZERO,
        # e infatti il pulse aveva 13 file contro i 418 di Base), si prendono comunque i piu' giovani
        # disponibili. Meglio seguire token di 12 ore che non seguirne nessuno.
        if len(nuovi) < 50:
            ripiego = [a for a, p in pools.items() if a not in gia and age_h(p) <= MAX_AGE_H]
            ripiego.sort(key=lambda a: age_h(pools[a]))
            nuovi = list(dict.fromkeys(nuovi + ripiego))[:MAX_POOLS]
        seguiti.sort(key=lambda a: age_h(pools[a])); nuovi.sort(key=lambda a: age_h(pools[a]))
        young = (seguiti + nuovi)[:MAX_POOLS]
        if not young: continue
        os.makedirs(f"{base}/pulse", exist_ok=True)
        # INDIRIZZI SEMPRE IN MINUSCOLO (04/09). Qui si scrivevano nella forma con le maiuscole di
        # controllo, mentre la rubrica li normalizza: lo stesso pool finiva due volte, e a ogni giro
        # la rubrica oscillava fra 917 e 1053 voci fondendo i doppioni. Non si perdeva niente, ma il
        # controllo "nessun archivio arretra" suonava a ogni ciclo — e un allarme che suona sempre
        # smette di essere un allarme. Il primo guasto vero, quando arriva, non lo guarderebbe nessuno.
        rf = f"{base}/token_map.json"
        rubrica = {}
        if os.path.exists(rf):
            try: rubrica = {k.lower(): v for k, v in json.load(open(rf)).items()}
            except Exception: rubrica = {}
        n = 0
        for i in range(0, len(young), BATCH):
            chunk = young[i:i + BATCH]
            d = get(f"{DS}/{dsname}/" + ",".join(chunk))
            time.sleep(PAUSE)
            for p in (d or {}).get("pairs") or []:
                addr = p.get("pairAddress")
                if not addr: continue
                # RUBRICA POOL->TOKEN: la salviamo per TUTTI i pool interrogati, anche quelli che poi
                # scarteremo per liquidita' bassa. Prima buttavamo via l'indirizzo del token insieme al
                # pool, e il perito si ritrovava con 71 candidati su 43.000 pool scoperti. Ma proprio i
                # pool scartati sono il TRASH che dobbiamo imparare a riconoscere: senza il loro
                # indirizzo non possiamo chiedere se sono honeypot, chi li ha creati, che tasse hanno.
                tk_any = (p.get("baseToken") or {}).get("address")
                if tk_any: rubrica[addr.lower()] = tk_any
                try: price = float(p.get("priceUsd") or 0)
                except Exception: price = 0.0
                liq = float((p.get("liquidity") or {}).get("usd") or 0)
                if price <= 0 or liq < MIN_LIQ: continue
                vol = (p.get("volume") or {}).get("h1") or 0
                tx = (p.get("txns") or {}).get("h1") or {}
                buys, sells = tx.get("buys", 0), tx.get("sells", 0)
                # stesso formato dei candele (ts,op,hi,lo,cl,vol) cosi' il cervello lo legge senza modifiche,
                # piu' il FLOW che DexScreener ci regala gia' aggregato
                # t0 = NASCITA VERA del pool (da DexScreener). Serve perche' il nostro primo campione puo'
                # arrivare ore dopo il listing: senza t0 il cervello crederebbe che il token sia nato quando
                # abbiamo iniziato a guardarlo, e l'entrata "a +2h" cadrebbe nel punto sbagliato.
                t0 = p.get("pairCreatedAt")
                # l'indirizzo del TOKEN (non del pool): DexScreener ce lo da' gia' a ogni giro e non lo
                # salvavamo. Serve a chiedere sicurezza (GoPlus) e quote (Jupiter), che vogliono il token.
                tok = (p.get("baseToken") or {}).get("address")
                row = {"ts": now, "op": price, "hi": price, "lo": price, "cl": price, "vol": vol,
                       "liq": round(liq, 2), "buys": buys, "sells": sells}
                if t0: row["t0"] = int(t0 / 1000)
                if tok: row["tk"] = tok
                with gzip.open(f"{base}/pulse/{addr.lower()}.jsonl.gz", "at") as fo:
                    fo.write(json.dumps(row) + "\n")
                n += 1
        try: json.dump(rubrica, open(rf, "w"))
        except Exception: pass
        tot += n
        print(f"  {chain}: {n} punti su {len(young)} giovani | rubrica token: {len(rubrica)}", flush=True)
    print(f"PULSE | {tot} punti scritti", flush=True)


if __name__ == "__main__":
    main()
