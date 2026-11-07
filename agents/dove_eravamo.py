"""DOVE ERAVAMO, istante per istante. L'unica prova che vale per il live.

L'IMPOSTAZIONE E' DI NICOLO' (5/11 pomeriggio) e cambia il valore della
sorveglianza: nel LIVE noi eravamo GIA' POSIZIONATI -- avevamo mandato i
pacchetti, avevamo gli ordini, avevamo letto le salute in quel momento.
Quindi quando si chiude una liquidazione possiamo rispondere "perche' lui e
non io" coi NOSTRI dati di quell'istante.
Nello storico no: la posizione un mese fa magari non esisteva, e soprattutto
non c'e' traccia di dove eravamo noi. Lo storico dice cosa e' successo nel
mondo; solo il live dice quanto distavamo.

IL BUCO CHE CHIUDE: le nostre candidate finivano nel registro SOLO quando
la sentinella beccava un aggiornamento di prezzo. Se una liquidazione si
chiude in un momento senza aggiornamenti, non abbiamo la prova di dove
eravamo -- e l'autopsia non puo' rispondere. Qui si registra la nostra
posizione a intervalli regolari, legata al NUMERO DI BLOCCO, cosi' ogni
liquidazione trova la nostra fotografia piu' vicina.

Costa poco: sono dati che abbiamo gia' in casa, nessuna chiamata di rete
oltre al numero del blocco.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pescatore as P

D = "data/liquidazioni"
REG = f"{D}/dove_eravamo.jsonl"
TIENI = 3000          # righe tenute nel registro


def scatta():
    testa = P.rpc("eth_blockNumber", [])
    if not testa:
        return None
    testa = int(testa, 16)
    try:
        import sentinella as S
        cands = S.candidate()
    except Exception as e:
        cands = []
    try:
        VP = json.load(open(f"{D}/vendite_pronte.json"))
        pronti = sum(1 for v in VP.values() if v.get("chiamata"))
    except Exception:
        pronti = None
    try:
        sv = json.load(open(f"{D}/saluti_vive.json"))
        saluti = sv.get("saluti") or {}
        eta_saluti = int(time.time() - sv.get("quando", 0))
    except Exception:
        saluti, eta_saluti = {}, None
    riga = {
        "blocco": testa, "quando": int(time.time()),
        "ordini_pronti": pronti,
        "saluti_vive": len(saluti), "eta_saluti_s": eta_saluti,
        # la nostra posizione: chi avremmo mandato, con quanto
        "candidate": [{"u": c["utente"][:14], "salute": round(c["salute"], 5),
                       "premio": round(c.get("premio") or 0),
                       "mancia": round((c.get("mancia_wei") or 0)/1e18, 4)}
                      for c in cands],
        "candidate_quante": len(cands),
        "premio_nel_pacchetto": round(sum(c.get("premio") or 0 for c in cands)),
    }
    with open(REG, "a") as f:
        f.write(json.dumps(riga) + "\n")
    # si tiene corto
    try:
        righe = open(REG).readlines()
        if len(righe) > TIENI:
            t = REG + ".tmp"
            open(t, "w").writelines(righe[-TIENI:])
            os.replace(t, REG)
    except Exception:
        pass
    print(f"   DOVE ERAVAMO al blocco {testa}: {len(cands)} candidate, "
          f"${riga['premio_nel_pacchetto']:,} di premio nel pacchetto, "
          f"{pronti} ordini pronti, {len(saluti)} salute vive")
    return riga


def piu_vicina_al_blocco(n, tolleranza=60):
    """La nostra fotografia piu' vicina a quel blocco. None se non c'e'."""
    migliore, dist = None, None
    try:
        for l in open(REG):
            try:
                r = json.loads(l)
            except Exception:
                continue
            d = abs(r.get("blocco", 0) - n)
            if dist is None or d < dist:
                migliore, dist = r, d
    except FileNotFoundError:
        return None, None
    if dist is None or dist > tolleranza:
        return None, dist
    return migliore, dist


if __name__ == "__main__":
    scatta()
