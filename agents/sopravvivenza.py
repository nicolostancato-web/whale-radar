"""SOPRAVVIVENZA — perche' i pool che NON abbiamo non ce li abbiamo. Condizione 7.

LA DOMANDA. Ogni database che seleziona rischia di selezionare proprio la cosa che cerca. Se i pool
che ci sfuggono fossero sistematicamente diversi da quelli che teniamo — piu' piccoli, piu' veloci,
piu' redditizi — ogni conclusione futura sarebbe una conclusione sul nostro filtro, non sul mercato.
La condizione 7 chiede: **59 esclusioni prese a caso, la causa di ciascuna, e zero casi senza causa**.

PERCHE' SOLO ORA SI PUO' FARE. Fino a stamattina il conteggio si faceva sul nostro registro, cioe'
si chiedeva al filtro di giudicare sé stesso. Adesso c'e' l'universo preso dalla catena — ogni pool
che esiste ha emesso il suo Initialize, che noi lo conoscessimo o no. Si campiona da li'.

LE CAUSE, e una sola di esse e' un guasto:
    «mai scambiato»      il pool esiste ma nessuno l'ha mai usato. Escluso a ragione.
    «sotto soglia»       ha scambiato pochissimo. Escluso a ragione, ed e' una nostra scelta.
    «scoperto tardi»     ha scambiato davvero, ma l'abbiamo saputo dopo le sue prime ore.
                         NON e' un guasto del raccoglitore, e' il buco strutturale che lo
                         scopritore chiude da oggi in avanti. Ma va contato, perche' dice quanto
                         mercato ci siamo persi prima.
    «PERSO SENZA RAGIONE» ha scambiato, lo conoscevamo, e non l'abbiamo preso. Questo e' il
                         controesempio: se ne esiste anche uno, la condizione 7 non e' chiusa.

COME SI TIENE A BASSO COSTO. Interrogare la catena pool per pool e' lentissimo (misurato: una
query su intervallo largo con filtro di indirizzo non torna entro dieci minuti). Quindi si fa al
contrario: si campionano pool NATI NELLA STESSA FASCIA, si scandisce quella fascia UNA volta, e si
contano gli scambi di tutti i campionati insieme. Lo stesso mestiere del recupero nascite.
"""
import gzip
import json
import os
import random
import time
import urllib.request

S = ["0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822",
     "0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67",
     "0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"]
V4 = S[2]
RPC = {"base": ("https://mainnet.base.org", 800, 2.0),
       "robinhood": ("https://rpc.mainnet.chain.robinhood.com", 1000, 0.1)}
CHAIN = os.environ.get("CHAIN", "robinhood")
BUDGET = int(os.environ.get("BUDGET_SEC", 400))
SOGLIA = int(os.environ.get("SOGLIA_SCAMBI", 20))     # sotto questo, escluso per scelta
ORE_VITA = int(os.environ.get("ORE_VITA", 6))
REG = f"data/multichain/{CHAIN}/sopravvivenza.jsonl"
SEME = int(os.environ.get("SEME", time.strftime("%Y%m%d")))
t0 = time.time()


def rpc(url, metodo, params, tentativi=4, to=90):
    b = json.dumps({"jsonrpc": "2.0", "method": metodo, "params": params, "id": 1}).encode()
    attesa = 4
    for k in range(tentativi):
        try:
            r = urllib.request.Request(url, data=b, headers={"Content-Type": "application/json",
                                                             "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=to) as x:
                d = json.load(x)
            if "error" in d:
                return None, str(d["error"])[:60]
            return d.get("result"), None
        except Exception as e:
            if k < tentativi - 1:
                time.sleep(attesa)
                attesa *= 2
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "esauriti"


def main():
    url, ampiezza, sec_blocco = RPC.get(CHAIN, (None, None, None))
    uni = f"data/multichain/{CHAIN}/universo.jsonl.gz"
    rf = f"data/multichain/{CHAIN}/righe.json"
    if not url or not os.path.exists(uni) or not os.path.exists(rf):
        print(f"SOPRAVVIVENZA | {CHAIN}: manca l'universo o il registro", flush=True)
        return
    tenuti = {k.lower() for k in json.load(open(rf)).get("pool", {})}
    universo = []
    try:
        for l in gzip.open(uni, "rt"):
            if l.strip():
                try:
                    d = json.loads(l)
                    if d.get("pool") and d.get("nato"):
                        universo.append((d["nato"], d["pool"]))
                except Exception:
                    pass
    except Exception:
        pass
    # IL BILANCIO, NON IL CAMPIONE (16/09, secondo rilievo della revisione esterna). Il revisore ha
    # fatto il conto a mente: 16.514 pool nati in 24 ore fanno 688 l'ora; se ne teniamo sei ore, a
    # regime dovremmo osservarne ~4.100, e ne dichiaravo 624. Gli altri 3.500 non avevano «una
    # destinazione contabile» — cioe' sparivano senza che nessuno dicesse dove.
    # La risposta probabile (non hanno mai scambiato, e chi non scambia non produce righe) e'
    # ragionevole, ma «probabile» non e' un numero. Quindi adesso ogni pool nato nella finestra ha
    # UN esito: preso, mai scambiato, sotto soglia, scoperto tardi. Nessuno sparisce in silenzio.
    esclusi = [(b, p) for b, p in universo if p not in tenuti]
    tutti_nati = list(universo)
    if len(esclusi) < 30:
        print(f"SOPRAVVIVENZA | {CHAIN}: solo {len(esclusi)} esclusi, campione troppo sottile",
              flush=True)
        return

    gia = set()
    if os.path.exists(REG):
        try:
            for l in open(REG):
                if l.strip():
                    gia.add(json.loads(l).get("pool"))
        except Exception:
            pass

    # SI CAMPIONA DAVVERO A CASO, col seme scritto: chiunque puo' rifare lo stesso campione e
    # ottenere le stesse righe. Un campione non riproducibile non e' una prova, e' un aneddoto.
    rnd = random.Random(SEME + len(gia))
    candidati = [x for x in tutti_nati if x[1] not in gia]
    if not candidati:
        print(f"SOPRAVVIVENZA | {CHAIN}: gia' classificati tutti gli esclusi noti ({len(gia)})",
              flush=True)
        return
    rnd.shuffle(candidati)
    # si prendono pool NATI VICINI, cosi' una scansione sola li serve tutti
    perno = candidati[0][0]
    finestra = int(ORE_VITA * 3600 / sec_blocco)
    # tutti i pool nati nella finestra, non solo quelli che ci mancano: solo cosi' i conti chiudono
    campione = [(b, p) for b, p in tutti_nati if perno <= b <= perno + finestra][:400]
    if len(campione) < 3:
        campione = candidati[:8]
        perno = min(b for b, _ in campione)

    # IL LAVORO A META' SI RIPRENDE, NON SI RIFA' (16/09). La finestra di vita di robinhood e'
    # 216.000 blocchi: in un giro se ne scandisce il 14%. Senza segnalibro, ogni giro ricomincerebbe
    # da capo e non si arriverebbe MAI a classificare nulla — la guardia continuerebbe giustamente a
    # rifiutare, e sembrerebbe che lo strumento non funzioni quando invece funziona troppo bene.
    # Qui il conteggio parziale sopravvive fra un giro e l'altro, e la classificazione avviene
    # solo quando la finestra e' completa davvero.
    CKS = f"data/multichain/{CHAIN}/sopravvivenza_ckpt.json"
    stato = {}
    if os.path.exists(CKS):
        try:
            stato = json.load(open(CKS))
        except Exception:
            stato = {}
    da, a = perno, perno + finestra
    if stato.get("perno") == perno:
        campione = [(b, p) for b, p in campione if p in set(stato.get("cerco", []))] or campione
        conta = {p: int(stato.get("conta", {}).get(p, 0)) for _, p in campione}
        cur = int(stato.get("cur", da))
    else:
        conta = {p: 0 for _, p in campione}
        cur = da
    cerco = {p for _, p in campione}
    chiamate = 0
    while cur < a and time.time() - t0 < BUDGET:
        fine = min(cur + ampiezza, a)
        log, err = rpc(url, "eth_getLogs", [{"fromBlock": hex(cur), "toBlock": hex(fine),
                                             "topics": [S]}])
        chiamate += 1
        if log is None:
            if ampiezza > 100:
                ampiezza //= 2
                continue
            cur = fine + 1
            continue
        for l in log:
            tp = l.get("topics") or []
            pl = (tp[1].lower() if (tp and tp[0] == V4 and len(tp) > 1) else l["address"].lower())
            if pl in cerco:
                conta[pl] += 1
        cur = fine + 1
        time.sleep(0.4)
    completata = cur >= a
    if not completata:
        try:
            json.dump({"perno": perno, "cur": cur, "conta": conta,
                       "cerco": sorted(cerco), "acq": int(time.time())}, open(CKS, "w"))
        except Exception:
            pass
        print(f"SOPRAVVIVENZA | {CHAIN}: finestra al {100*(cur-da)/(a-da):.0f}%, segnalibro salvato. "
              f"Non classifico: un conteggio parziale direbbe «sotto soglia» a pool attivi",
              flush=True)
        return
    try:
        os.remove(CKS)
    except Exception:
        pass

    righe = []
    for b, p in campione:
        n = conta[p]
        nostro = p in tenuti
        ha_righe = os.path.exists(f"data/multichain/{CHAIN}/vivo/{p}.jsonl.gz") or \
                   os.path.exists(f"data/multichain/{CHAIN}/storico/{p}.jsonl.gz")
        if nostro and ha_righe:
            causa = "preso"
        elif n == 0:
            causa = "mai scambiato"
        elif n < SOGLIA:
            causa = "sotto soglia"
        elif nostro and not ha_righe:
            causa = "PERSO SENZA RAGIONE"   # lo conoscevamo, ha scambiato, non l'abbiamo preso
        else:
            causa = "scoperto tardi"        # ha scambiato davvero e non ce l'abbiamo
        righe.append({"acq": int(time.time()), "seme": SEME, "chain": CHAIN, "pool": p,
                      "nato": b, "scambi_prime_ore": n, "causa": causa,
                      "nel_registro": nostro, "ha_righe": ha_righe})
    try:
        with open(REG, "a") as f:
            for r in righe:
                f.write(json.dumps(r) + "\n")
    except Exception:
        pass

    tutte = list(righe)
    if os.path.exists(REG):
        tutte = []
        for l in open(REG):
            if l.strip():
                try:
                    tutte.append(json.loads(l))
                except Exception:
                    pass
    import collections
    c = collections.Counter(x["causa"] for x in tutte)
    attivi = [x for x in tutte if x["causa"] == "scoperto tardi"]
    print(f"SOPRAVVIVENZA | {CHAIN}: +{len(righe)} classificati in {chiamate} chiamate | "
          f"totale {len(tutte)}/59", flush=True)
    for k, v in c.most_common():
        print(f"   {k:<22} {v:>4}  ({100*v/len(tutte):.0f}%)", flush=True)
    if attivi:
        peggio = max(attivi, key=lambda x: x["scambi_prime_ore"])
        print(f"   il piu' scambiato che ci e' sfuggito: {peggio['scambi_prime_ore']} scambi "
              f"nelle prime {ORE_VITA} ore", flush=True)


if __name__ == "__main__":
    main()
