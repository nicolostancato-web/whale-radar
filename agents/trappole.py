#!/usr/bin/env python3
"""
TRAPPOLE — i token da cui NON si esce, marcati prima che il backtest li conti come uscite normali.

Dall'audit avversariale del 03/09, ed e' l'errore piu' insidioso trovato finora:

    «un honeypot spesso NON mostra -100% nella serie prezzi — il prezzo resta positivo,
     semplicemente non puoi vendere.»

Il backtest guarda il prezzo, vede uno stop a -40% e registra -40%. Nella realta' quel trade e'
-100%: il prezzo esisteva, l'uscita no. Sono due cose diverse e ne registravamo una sola — quella
sbagliata, e sempre nella direzione che ci fa comodo.

Qui si marcano i pool il cui token e' una trappola secondo GoPlus (honeypot dichiarato, vendita
impossibile, o tassa di vendita cosi' alta da equivalere a non poter uscire), piu' quelli che
Jupiter ci ha gia' detto invendibili quando abbiamo misurato i costi.

ANTI DOPPIO CONTEGGIO: chi valuta le strategie forza -100% SOLO se la serie di prezzi non lo mostra
gia'. Cosi' l'aggiustamento e' esatto token per token, non una probabilita' spalmata su tutti —
che e' esattamente l'errore del costo medio, ripetuto in un altro punto.

Scrive data/trappole.json. Sola lettura. €0.
"""
import json, os, glob, time

TASSA_PROIBITIVA = 0.30      # oltre il 30% di tassa in vendita, uscire equivale a non uscire
USCITA = "data/trappole.json"
now = int(time.time())


def _f(x):
    try: return float(x)
    except Exception: return None


def main():
    trappola = {}
    for p in glob.glob("data/sicurezza/*.jsonl"):
        chain = os.path.basename(p).replace(".jsonl", "")
        for l in open(p):
            try: d = json.loads(l)
            except Exception: continue
            tk = (d.get("token") or "").lower()
            if not tk: continue
            perche = None
            if str(d.get("honeypot") or "") == "1": perche = "honeypot dichiarato"
            elif str(d.get("cannot_sell_all") or "") == "1": perche = "non si vende tutto"
            else:
                t = _f(d.get("sell_tax"))
                if t is not None and t >= TASSA_PROIBITIVA: perche = f"tassa in vendita {t*100:.0f}%"
            if perche: trappola[tk] = {"chain": chain, "perche": perche, "fonte": "goplus"}

    # e quelle che abbiamo toccato con mano: Jupiter non trovava come rivenderle
    try:
        for mint, t in json.load(open("data/costi_archivio.json")).items():
            for v in (t.get("size") or {}).values():
                if not isinstance(v, dict): continue
                c = v.get("costo_roundtrip_pct")
                if "VENDITA IMPOSSIBILE" in str(v.get("errore", "")) or (c is not None and c >= 50):
                    trappola.setdefault(mint.lower(),
                                        {"chain": "solana", "perche": "Jupiter: uscita inesistente o nulla",
                                         "fonte": "misurato"})
                    break
    except Exception: pass

    # dal token al POOL, che e' come i nostri file sono indicizzati
    pool = {}
    for f in glob.glob("data/multichain/*/token_map.json"):
        ch = f.split("/")[-2]
        try: m = json.load(open(f))
        except Exception: continue
        for pa, tk in m.items():
            if (tk or "").lower() in trappola: pool[pa.lower()] = trappola[(tk or "").lower()]["perche"]

    json.dump({"ts": now, "token": trappola, "pool": pool}, open(USCITA, "w"))
    da_goplus = sum(1 for v in trappola.values() if v["fonte"] == "goplus")
    print(f"TRAPPOLE | {len(trappola)} token ({da_goplus} da GoPlus, {len(trappola)-da_goplus} misurati) | "
          f"{len(pool)} pool riconosciuti nei nostri dati", flush=True)


if __name__ == "__main__":
    main()
