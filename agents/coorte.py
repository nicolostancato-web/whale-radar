#!/usr/bin/env python3
"""
COORTE — separare "il token e' morto" da "non l'abbiamo guardato".

DA DOVE VIENE (14/09, richiesta del revisore avversariale). L'audit aveva misurato che le serie
escluse dall'analisi vivono 1 ora e quelle ammesse 23, e io l'avevo chiamato survivorship bias. Il
revisore ha corretto: e' una DURATA OSSERVATA, non la vita del token. La stessa differenza puo'
venire da mortalita' vera oppure da buchi nostri — frequenza, limiti della fonte, cambi di
identificativo, la soglia dei $5.000. Sono cose opposte: una e' il mondo, l'altra siamo noi.

IL TEST, che e' prospettico e non si puo' fare all'indietro: per ogni pool scoperto, a +3h si chiede
a un canale INDIPENDENTE se e' ancora vivo, e si confronta con quello che abbiamo noi.

  canale indipendente dice VIVO  + noi non abbiamo la candela  -> BUCO NOSTRO
  canale indipendente dice MORTO + noi non abbiamo la candela  -> mortalita' vera
  vivo + candela presente                                       -> copertura funzionante

L'INDIPENDENZA, dichiarata: su Base e Robinhood si interroga la CATENA (eth_call getReserves/slot0),
che e' una fonte diversa da quella delle candele. Su Solana non abbiamo un RPC: li' il confronto
userebbe la stessa fonte, quindi NON lo facciamo e lo dichiariamo, invece di fingere indipendenza.

Scrive in sola aggiunta su data/coorte.jsonl. Sola lettura sui dati, RPC pubblici gratuiti. €0.
"""
import json, glob, os, time, urllib.request

RPC = {"base": "https://mainnet.base.org", "robinhood": "https://rpc.mainnet.chain.robinhood.com"}
ETA_MIN_H = 3
ETA_MAX_H = 8            # oltre, la domanda "era vivo a +3h?" non e' piu' rispondibile adesso
MAX_POOL = int(os.environ.get("COORTE_MAX", 25))
REG = "data/coorte.jsonl"


def catena(chain, pool, dato):
    b = json.dumps({"jsonrpc": "2.0", "method": "eth_call",
                    "params": [{"to": pool, "data": dato}, "latest"], "id": 1}).encode()
    r = urllib.request.Request(RPC[chain], data=b,
                               headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r, timeout=20) as x:
            return (json.load(x) or {}).get("result")
    except Exception:
        return None


def vivo_secondo_la_catena(chain, pool):
    """Vivo = il contratto risponde con riserve non nulle. Se non risponde in nessuno dei due modi,
    non concludiamo: restituiamo None, che significa NON SO — non 'morto'."""
    r = catena(chain, pool, "0x0902f1ac")           # getReserves() stile V2
    if r and len(r) >= 130:
        try:
            if int(r[2:66], 16) > 0 and int(r[66:130], 16) > 0: return True
        except Exception: pass
        return False
    r3 = catena(chain, pool, "0x1a686502")          # liquidity() stile V3
    if r3:
        try: return int(r3, 16) > 0
        except Exception: return None
    return None


def abbiamo_la_candela(chain, pool, t0):
    for d in ("candles", "pulse"):
        f = f"data/multichain/{chain}/{d}/{pool}.jsonl.gz"
        if not os.path.exists(f): continue
        import gzip
        try:
            for l in gzip.open(f, "rt"):
                if not l.strip(): continue
                d2 = json.loads(l)
                ts = d2.get("ts")
                if ts and t0 <= ts <= t0 + ETA_MIN_H * 3600 + 3600: return True
        except Exception: pass
    return False


def main():
    now = int(time.time())
    nuove = []
    for chain in RPC:
        pf = f"data/multichain/{chain}/pools.json"
        if not os.path.exists(pf): continue
        try: pools = json.load(open(pf))
        except Exception: continue
        cand = []
        for a, v in pools.items():
            if len(a) != 42: continue
            t0 = (v or {}).get("seen")
            if not t0: continue
            eta = (now - t0) / 3600
            if ETA_MIN_H <= eta <= ETA_MAX_H: cand.append((a, t0))
        cand.sort(key=lambda x: -x[1])
        for a, t0 in cand[:MAX_POOL]:
            vivo = vivo_secondo_la_catena(chain, a)
            time.sleep(0.15)
            nuove.append({"acq": now, "chain": chain, "pool": a, "t0": t0,
                          "vivo_catena": vivo, "candela_nostra": abbiamo_la_candela(chain, a, t0)})
    if nuove:
        try:
            with open(REG, "a") as f:                # SOLA AGGIUNTA
                for r in nuove: f.write(json.dumps(r) + "\n")
        except Exception as e:
            print(f"COORTE | non riesco a scrivere: {type(e).__name__}", flush=True)

    # --- il riepilogo, sulla storia intera ---
    # UN POOL E' UN CASO, NON SETTE (15/09). Il test ricontrolla gli stessi pool a ogni giro, e il
    # riepilogo contava ogni controllo come un caso nuovo: 4.844 osservazioni erano 670 pool, ognuno
    # guardato in media sette volte. Il campione sembrava sette volte piu' solido di quanto fosse.
    # Me ne sono accorto solo andando a vedere i «14 casi incoerenti»: erano LO STESSO POOL,
    # contato quattordici volte.
    tutte = []
    if os.path.exists(REG):
        for l in open(REG):
            if l.strip():
                try: tutte.append(json.loads(l))
                except Exception: pass
    visti = {}
    for r in tutte:
        k = (r.get("chain"), r.get("pool"))
        if k not in visti: visti[k] = r          # la PRIMA osservazione, non l'ultima
    righe = list(visti.values())
    L = ["# 🧫 COORTE — è morto, o non l'abbiamo guardato?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · test prospettico · €0*", "",
         "> L'audit aveva misurato che le serie escluse vivono 1 ora e le ammesse 23, e l'avevo",
         "> chiamato survivorship bias. La revisione ha corretto: è una **durata osservata**, non la",
         "> vita del token. La stessa differenza può venire da mortalità vera **oppure da buchi",
         "> nostri**. Sono cose opposte: una è il mondo, l'altra siamo noi.", "",
         "> Qui si chiede a un canale **indipendente** — la catena, non la stessa fonte delle candele —",
         "> se il pool era vivo a +3h, e si confronta con quello che abbiamo noi.", "",
         f"**Osservazioni accumulate: {len(righe)}** (+{len(nuove)} in questo giro)", ""]
    if righe:
        m = {}
        for r in righe:
            k = (r.get("vivo_catena"), r.get("candela_nostra"))
            m[k] = m.get(k, 0) + 1
        L += ["| la catena dice | noi abbiamo la candela | quanti | lettura |", "|---|---|---|---|"]
        etichette = {(True, False): "🔴 **buco nostro**", (False, False): "⚫ mortalità vera",
                     (True, True): "🟢 copertura funzionante", (False, True): "⚠️ incoerente",
                     (None, False): "❓ non so (contratto muto)", (None, True): "❓ non so"}
        for k, v in sorted(m.items(), key=lambda x: -x[1]):
            L.append(f"| {k[0]} | {k[1]} | {v} | {etichette.get(k, '?')} |")
        noti = sum(v for k, v in m.items() if k[0] is not None and not k[1])
        buchi = m.get((True, False), 0)
        L += ["", f"> Fra i casi in cui **non abbiamo la candela** e la catena ha risposto: "
                  f"**{buchi} su {noti}** erano ancora vivi — cioè **buchi nostri**, non morti."
              if noti else "", ""]
    L += ["> ⚠️ **Cosa vuol dire «vivo» qui, per non farsi illusioni.** Vivo = il contratto risponde",
          "> con riserve non nulle. Non vuol dire che qualcuno lo stia scambiando, né che sia",
          "> vendibile: un pool può avere riserve e nessuno scambio. Quindi un «buco nostro» dice che",
          "> **il pool esisteva ancora**, non che valesse la pena guardarlo. È comunque la distinzione",
          "> che serviva: dice che non l'abbiamo guardato, non che era morto.", "",
          "> **Limite dichiarato**: su Solana non abbiamo un RPC pubblico, quindi il confronto userebbe",
          "> la stessa fonte delle candele. Non lo facciamo: un test che si conferma da solo non è un",
          "> test. Solana resta non giudicabile su questa domanda.", "",
          "> **Questo test non si può fare all'indietro**: chiede com'era il mondo a +3h da un pool",
          "> scoperto poche ore fa. Comincia oggi e si accumula."]
    open("COORTE.md", "w").write("\n".join(L))
    print(f"COORTE | {len(nuove)} nuove, {len(righe)} totali", flush=True)


if __name__ == "__main__":
    main()
