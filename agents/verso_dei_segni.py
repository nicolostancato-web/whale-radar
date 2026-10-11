"""Quale famiglia di pool ha il segno invertito? Verifica sulla chain, con pazienza.

PERCHE' IN UNA CORSIA E NON A MANO (5/10). L'asimmetria e' misurata e replicata: nei primi sei
scambi la quota di ACQUISTI e' centrata su 0,23-0,38 per le pool con indirizzo (V2/V3) e su
0,63-0,72 per quelle con id (V4). Due famiglie sullo stesso mercato non possono comportarsi in
modo opposto: una delle due e' letta male.
Ho provato a risolverla a mano in due giri interattivi — 42 transazioni esaminate, nessun caso
isolabile, perche' ogni transazione passa da router e tocca molte pool. **Ho sbagliato
strumento**: e' una verifica che vuole centinaia di tentativi e un budget di tempo, non
venticinque minuti.

IL METODO, inequivocabile e senza interpretazione. Per una pool V2/V3 (che E' un contratto,
quindi i trasferimenti verso e da lei si vedono):
  · si prende uno scambio EMESSO DA QUELLA POOL;
  · si guardano i trasferimenti di gettoni con `to == pool` e `from == pool` nella stessa
    transazione;
  · se dall'evento risulta a0 > 0, la pool deve RICEVERE token0: se invece riceve token1,
    il segno e' invertito.
Nessuna plausibilita', nessuna correlazione: il confronto fra cio' che l'evento dichiara e cio'
che i gettoni hanno fatto.

PERCHE' NON SI PUO' FARE SULLE V4: in V4 il pool non e' un contratto, e' un id dentro il
PoolManager, quindi non esistono trasferimenti «verso la pool». La V4 si decide per differenza:
se la V2/V3 risulta CORRETTA, l'invertita e' la V4.

E NON SI APPLICA NESSUNA CORREZIONE QUI. Questo agente misura e scrive un verdetto. Invertire
la famiglia sbagliata raddoppierebbe il danno, quindi la correzione e' una decisione separata,
presa dopo aver letto il verdetto.
"""
import json
import os
import sys
import time
import urllib.error
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
import a_fette as AF                                              # noqa: E402

CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = float(os.environ.get("BUDGET_SEC", 900))
PAUSA = float(os.environ.get("PAUSA", 0.25))
BERSAGLIO = int(os.environ.get("BERSAGLIO", 30))
ESPLORATORI = {"robinhood": "https://robinhoodchain.blockscout.com",
               "base": "https://base.blockscout.com"}
SWAP = {"0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822": "V2",
        "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67": "V3"}
H = {"User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/129.0 Safari/537.36"),
     "Accept": "application/json", "Accept-Language": "en-US,en;q=0.9"}


def i256(h):
    v = int(h, 16)
    return v - (1 << 256) if v >= (1 << 255) else v


def main():
    base = ESPLORATORI.get(CHAIN)
    if not base:
        raise SystemExit(f"SEGNI | nessun esploratore per {CHAIN}")
    intest = dict(H)
    intest["Referer"] = base + "/"

    def get(u):
        with urllib.request.urlopen(
                urllib.request.Request(u, headers=intest), timeout=25) as r:
            return json.loads(r.read())

    p = f"data/multichain/{CHAIN}/coppie.json"
    if not os.path.exists(p):
        raise SystemExit(f"SEGNI | manca {p}")
    cop = json.load(open(p))["coppie"]
    # solo le pool che SONO contratti: su quelle i trasferimenti si vedono
    pool = AF.mia_parte([k for k in cop if len(k) == 42])
    i_f, n_f = AF.quale_fetta()
    print(f"SEGNI | {CHAIN} fetta {i_f+1}/{n_f}: {len(pool):,} pool con indirizzo", flush=True)

    t0 = time.time()
    coerenti = incoerenti = 0
    guardate = strozzate = 0
    casi = []
    for pid in pool:
        if time.time() - t0 > BUDGET or coerenti + incoerenti >= BERSAGLIO:
            break
        meta = cop[pid]
        t_0 = (meta.get("t0") or "").lower()
        t_1 = (meta.get("t1") or "").lower()
        if not t_0 or not t_1:
            continue
        # L'ENDPOINT ERA SBAGLIATO, E AVREI DOVUTO VEDERLO AL PRIMO TENTATIVO (5/10).
        # Chiedevo `/addresses/{pool}/transactions`: per una pool V2/V3 torna ZERO, perche'
        # gli scambi non sono transazioni VERSO la pool — sono transazioni verso il ROUTER,
        # che poi chiama la pool. La pool non e' ne' mittente ne' destinatario, quindi
        # quell'elenco e' vuoto per costruzione.
        # Ho messo in corsia un filtro che non avevo mai visto riuscire nemmeno una volta:
        # i due tentativi a mano avevano gia' dato zero casi, e invece di capire il perche'
        # ho scalato il fallimento a 1.600 transazioni. **Prima si fa funzionare una volta,
        # poi si scala.**
        # L'endpoint giusto e' `/logs`: gli scambi sono EVENTI EMESSI dalla pool, e ogni
        # evento porta la sua transazione. Verificato su tre casi prima di riscrivere qui.
        try:
            j = get(f"{base}/api/v2/addresses/{pid}/logs")
        except urllib.error.HTTPError:
            strozzate += 1
            time.sleep(2)
            continue
        except Exception:
            continue
        time.sleep(PAUSA)
        suoi = [l for l in (j.get("items") or [])
                if (l.get("topics") or [None])[0] in SWAP]
        for it in suoi[:3]:
            if time.time() - t0 > BUDGET or coerenti + incoerenti >= BERSAGLIO:
                break
            tx = it.get("transaction_hash") or it.get("tx_hash")
            if not tx:
                continue
            guardate += 1
            try:
                tr = get(f"{base}/api/v2/transactions/{tx}/token-transfers")
                time.sleep(PAUSA)
            except urllib.error.HTTPError:
                strozzate += 1
                time.sleep(2)
                continue
            except Exception:
                continue
            sw = [it]
            dentro = [x for x in (tr.get("items") or [])
                      if str((x.get("to") or {}).get("hash") or "").lower() == pid]
            if len(dentro) != 1:
                continue
            d = (sw[0].get("data") or "0x")[2:]
            campi = [d[i:i + 64] for i in range(0, len(d), 64)]
            ver = SWAP[(sw[0].get("topics") or [None])[0]]
            if ver == "V2":
                if len(campi) < 4:
                    continue
                a = [int(campi[i], 16) for i in range(4)]
                a0 = a[0] - a[2]
            else:
                if len(campi) < 2:
                    continue
                a0 = i256(campi[0])
            if a0 == 0:
                continue
            tok = dentro[0].get("token") or {}
            tin = str(tok.get("address_hash") or tok.get("address") or "").lower()
            quale = "token0" if tin == t_0 else ("token1" if tin == t_1 else None)
            if quale is None:
                continue
            atteso = "token0" if a0 > 0 else "token1"
            ok = quale == atteso
            coerenti += 1 if ok else 0
            incoerenti += 0 if ok else 1
            casi.append({"tx": tx, "pool": pid, "versione": ver, "a0": a0,
                         "entra_davvero": quale, "atteso": atteso, "coerente": ok})
    pezzo = AF.nome_pezzo(f"data/multichain/{CHAIN}", "verso_dei_segni")
    json.dump({"chain": CHAIN, "guardate": guardate, "strozzate": strozzate,
               "coerenti": coerenti, "incoerenti": incoerenti, "casi": casi},
              open(pezzo, "w"), ensure_ascii=False, indent=1)
    tot = coerenti + incoerenti
    print(f"   transazioni esaminate {guardate:,} · strozzate {strozzate} · "
          f"casi isolati {tot}", flush=True)
    if tot:
        print(f"   COERENTI {coerenti} · INCOERENTI {incoerenti} "
              f"({incoerenti/tot:.0%} incoerenti)", flush=True)
        print("   Se gli incoerenti sono la maggioranza, la famiglia V2/V3 e' letta "
              "al rovescio; se sono una minoranza, l'invertita e' la V4 (per differenza).",
              flush=True)
    else:
        print("   nessun caso isolabile: NON si conclude niente. "
              "Serve piu' budget o un filtro diverso.", flush=True)


if __name__ == "__main__":
    main()
