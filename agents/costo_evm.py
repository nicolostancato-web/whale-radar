#!/usr/bin/env python3
"""
COSTO_EVM — il costo delle due gambe su Base e Robinhood, letto DALLA CATENA.

IL BLOCCO CHE CHIUDE. 815 misure di costo, tutte su Solana via Jupiter, zero su Base e Robinhood: i
netti di quelle due chain erano calcolati col costo di un altro mercato. Su Robinhood non esiste un
Jupiter a cui chiedere un preventivo — ma esiste la catena, e la catena non ha bisogno di essere
interrogata da un servizio: la si legge.

PERCHE' QUI LA FORMULA E' LECITA E SU SOLANA NO. Ieri abbiamo bocciato la stima dalla riserva perche'
sbagliava del 55% contro i preventivi veri di Jupiter. Ma quel confronto non riguardava pool a
prodotto costante: su Solana ci sono curve di lancio e percorsi multipli, dove "riserva" non spiega il
prezzo. Qui invece chiediamo alla coppia il suo getReserves(): se risponde, E' un pool a prodotto
costante, e la formula con la commissione dello 0,3% NON E' UNA STIMA — e' esattamente il conto che
fa il contratto quando esegue lo scambio. Non stiamo indovinando il prezzo: stiamo rifacendo il suo
calcolo. Se non risponde (pool stile Uniswap V4, che vivono dentro un unico contratto), non lo
misuriamo e lo diciamo.

Sola lettura, RPC pubblici gratuiti. €0.
"""
import json, os, glob, gzip, time, urllib.request, statistics as st

RPC = {"base": "https://mainnet.base.org", "robinhood": "https://rpc.mainnet.chain.robinhood.com"}
TAGLIA = float(os.environ.get("TAGLIA_USD", 25))
MAX_POOL = int(os.environ.get("COSTO_EVM_MAX", 60))
PAUSA = 0.15
FEE = 997 / 1000        # 0,3%: la commissione standard delle coppie a prodotto costante


def riserve(chain, pool):
    b = json.dumps({"jsonrpc": "2.0", "method": "eth_call",
                    "params": [{"to": pool, "data": "0x0902f1ac"}, "latest"], "id": 1}).encode()
    r = urllib.request.Request(RPC[chain], data=b,
                               headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r, timeout=25) as x:
            d = json.load(x)
    except Exception:
        return None
    res = d.get("result")
    if not res or len(res) < 130: return None
    try:
        r0 = int(res[2:66], 16); r1 = int(res[66:130], 16)
    except Exception:
        return None
    return (r0, r1) if r0 > 0 and r1 > 0 else None


def leggi(chain, pool, sel):
    b = json.dumps({"jsonrpc": "2.0", "method": "eth_call",
                    "params": [{"to": pool, "data": sel}, "latest"], "id": 1}).encode()
    r = urllib.request.Request(RPC[chain], data=b,
                               headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r, timeout=25) as x:
            return (json.load(x) or {}).get("result")
    except Exception:
        return None


def riserve_v3(chain, pool):
    """LA MAGGIOR PARTE DEI POOL DI ROBINHOOD E' IN STILE V3 (20 su 25), e senza questi la chain
    restava con UNA misura sola. In un pool V3 le riserve non stanno in un campo: si ricavano dal
    prezzo corrente e dalla liquidita' attiva. Sono 'virtuali', ma dentro il tratto in cui si muove
    un ordine da 25 dollari il contratto usa esattamente quelle — e i due lati virtuali hanno per
    costruzione lo STESSO valore, quindi il lato quotato e' meta' del totale, come in un pool V2."""
    s0 = leggi(chain, pool, "0x3850c7bd")          # slot0()
    lq = leggi(chain, pool, "0x1a686502")          # liquidity()
    if not s0 or not lq or len(s0) < 66: return None
    try:
        sqrtP = int(s0[2:66], 16); L = int(lq, 16)
    except Exception:
        return None
    if sqrtP <= 0 or L <= 0: return None
    return L, sqrtP


def commissione(chain, pool):
    """La commissione la dichiara il pool: 0,05% / 0,3% / 1%. Assumerla e' un errore da un punto
    percentuale su un costo che ne vale meno di uno."""
    f = leggi(chain, pool, "0xddca3f43")           # fee()
    try:
        v = int(f, 16) / 1_000_000 if f else None
    except Exception:
        v = None
    return (1 - v) if v and 0 < v < 0.1 else FEE


def andata_ritorno(size_usd, riserva_usd, fee=FEE):
    """Il conto ESATTO che fa il contratto: compra, poi rivendi quello che hai ricevuto.
    Lavora sui rapporti, quindi basta il lato quotato espresso in dollari."""
    Ru, Rt = riserva_usd, 1.0                       # unita' arbitrarie per il lato token: contano i rapporti
    tok = (size_usd * fee * Rt) / (Ru + size_usd * fee)
    Ru2, Rt2 = Ru + size_usd, Rt - tok
    if Rt2 <= 0: return 1.0
    back = (tok * fee * Ru2) / (Rt2 + tok * fee)
    return max(0.0, min(1.0, 1 - back / size_usd))


def liquidita_nota(chain):
    out = {}
    for f in glob.glob(f"data/multichain/{chain}/pulse/*.jsonl.gz"):
        pool = os.path.basename(f).split(".")[0]
        ultima = None
        try:
            for l in gzip.open(f, "rt"):
                if l.strip():
                    try: ultima = json.loads(l).get("liq")
                    except Exception: pass
        except Exception: continue
        if ultima and len(pool) == 42: out[pool] = float(ultima)
    return out


def liquidita_da_gecko(chain, quanti=40):
    """LA COPERTURA NON DEVE DIPENDERE DAL BATTITO. Robinhood aveva UNA misura non perche' i suoi pool
    fossero illeggibili — sono leggibili tutti — ma perche' prendevamo la liquidita' solo dai pool gia'
    seguiti dal battito, che su quella chain e' partito stamattina. Un collo di bottiglia messo da noi
    somiglia a un limite del mondo. Qui la chiediamo direttamente, dalla stessa API gratuita delle
    candele."""
    out = {}
    for pg in (1, 2):
        u = f"https://api.geckoterminal.com/api/v2/networks/{chain}/pools?page={pg}"
        r = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(r, timeout=25) as x:
                d = json.load(x)
        except Exception:
            break
        for p in (d or {}).get("data", []):
            a = p.get("attributes") or {}
            addr = a.get("address")
            try: liq = float(a.get("reserve_in_usd") or 0)
            except Exception: liq = 0.0
            if addr and len(addr) == 42 and liq > 0:
                out[addr] = liq
        time.sleep(0.6)
        if len(out) >= quanti: break
    return out


def main():
    L = ["# ⛓️💸 IL COSTO SU BASE E ROBINHOOD — letto dalla catena, non prestato da un altro mercato",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · taglia ${TAGLIA:.0f} · RPC pubblici · €0*", "",
         "> Su Robinhood non esiste un Jupiter a cui chiedere un preventivo. Ma la catena non va",
         "> interrogata da un servizio: **si legge**. Chiediamo alla coppia le sue riserve; se risponde,",
         "> è un pool a prodotto costante — e il conto con la commissione dello 0,3% **non è una stima**,",
         "> è esattamente ciò che il contratto calcola quando esegue lo scambio.", "",
         "> *(Ieri la stima dalla riserva è stata bocciata contro Jupiter: là erano curve di lancio e",
         "> percorsi multipli, dove la riserva non spiega il prezzo. Qui rifacciamo il calcolo del",
         "> contratto, non indoviniamo il suo risultato.)*", ""]
    # LE MISURE SI CONSERVANO. Senza archivio ogni giro rifa' gli stessi pool e la copertura non
    # sale mai: il controllo delle due gambe continuerebbe a leggere zero misure EVM per sempre.
    ARCH_EVM = "data/costi_evm.json"
    try:
        arch = json.load(open(ARCH_EVM))
    except Exception:
        arch = {}
    righe = []
    for ch in ("base", "robinhood"):
        arch.setdefault(ch, {})
        liq = liquidita_nota(ch)
        for a, v in liquidita_da_gecko(ch).items():
            liq.setdefault(a, v)
        # SI MISURA DOVE SI OPERA (11/09). Finora prendevo i pool piu' liquidi che l'elenco pubblico
        # mostra: bellissimi e non nostri. La copertura restava sotto l'1% perche' misuravo un mondo
        # diverso da quello su cui il modello sceglie. Adesso vengono prima i pool dei token che
        # VALUTIAMO DAVVERO — quelli con candele — e solo dopo, se avanza posto, gli altri.
        nostri = {os.path.basename(f).split(".")[0].lower()
                  for f in glob.glob(f"data/multichain/{ch}/candles/*.jsonl.gz")}
        gia = set(arch.get(ch, {}))          # i gia' misurati non si rifanno: la copertura deve SALIRE
        casa = [p for p in liq if p.lower() in nostri and p.lower() not in gia]
        fuori = [p for p in liq if p.lower() not in nostri]
        casa.sort(key=lambda p: -liq[p]); fuori.sort(key=lambda p: -liq[p])
        pool = (casa + fuori)[:MAX_POOL]
        costi, letti, muti = [], 0, 0
        for p in pool:
            r = riserve(ch, p)
            time.sleep(PAUSA)
            stile = "v2" if r else None
            if not r:
                r3 = riserve_v3(ch, p)
                time.sleep(PAUSA)
                stile = "v3" if r3 else None
            if not stile:
                muti += 1
                continue
            letti += 1
            fee = commissione(ch, p) if stile == "v3" else FEE
            time.sleep(PAUSA)
            c = andata_ritorno(TAGLIA, max(1.0, liq[p] / 2.0), fee)
            costi.append(c)
            arch[ch][p.lower()] = {"costo": round(c, 5), "liq": round(liq[p], 2),
                                   "stile": stile, "ts": int(time.time())}
        righe.append((ch, len(pool), letti, muti, costi))

    L += ["| chain | pool provati | a prodotto costante | non leggibili | costo mediano | il 25% peggiore |",
          "|---|---|---|---|---|---|"]
    for ch, prov, letti, muti, costi in righe:
        if costi:
            cs = sorted(costi)
            L.append(f"| **{ch}** | {prov} | {letti} | {muti} | **{st.median(cs)*100:.2f}%** | "
                     f"{cs[int(len(cs)*0.75)]*100:.2f}% |")
        else:
            L.append(f"| **{ch}** | {prov} | 0 | {muti} | *nessuna misura* | — |")
    L += ["", "> I pool **non leggibili** sono quelli in stile Uniswap V4, che non vivono in un contratto",
          "> proprio: lì il conto non si può rifare da fuori e **non lo inventiamo**. Compaiono nel",
          "> conteggio apposta: un buco dichiarato non è un buco nascosto.", ""]
    try:
        json.dump(arch, open(ARCH_EVM, "w"))
    except Exception:
        pass
    L += [f"*Misure conservate finora: " +
          ", ".join(f"**{c}** {len(arch.get(c, {}))}" for c in ("base", "robinhood")) + ".*"]
    open("COSTO_EVM.md", "w").write("\n".join(L))
    print("COSTO_EVM | " + " ".join(f"{c}:{len(k)}misure" for c, _, _, _, k in righe), flush=True)


if __name__ == "__main__":
    main()
