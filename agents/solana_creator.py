#!/usr/bin/env python3
"""
SOLANA_CREATOR — chi ha creato il token, sulla chain dove non lo sappiamo mai.

Solana e' la nostra chain piu' grossa per numero di token e ha il 5% di copertura del creator,
contro il 99% di BSC. Senza quel campo, la pista piu' promettente che abbiamo — la reputazione di
chi crea i token — su Solana non si puo' nemmeno testare.

Perche' e' difficile, e cosa abbiamo gia' escluso:
  - l'autorita' del mint su Solana e' quasi sempre REVOCATA: non dice chi l'ha creato
  - l'API pubblica di pump.fun risponde 530 (bloccata)
  - "il primo compratore e' il creator" sembrava ragionevole: PROVATO su BSC e Base, dove il creator
    vero lo conosciamo, e coincide nel 2-3% dei casi. Scartata. Meglio due minuti di verifica che
    una settimana di analisi costruita su un'assunzione comoda.

Resta Helius (chiave gia' nei secret, piano gratuito): l'API degli asset restituisce le authorities
e i creators dichiarati nei metadati. Una chiamata per token.

NOTA ONESTA sul metodo: questo agente non ho potuto provarlo in locale, perche' la chiave vive solo
su GitHub. Percio' e' scritto per FALLIRE IN MODO RUMOROSO — se la chiave manca, se la risposta ha
un formato diverso, se non trova niente, lo dice nel verbale invece di scrivere zero e sembrare a
posto. Un agente che tace quando non funziona e' peggio di un agente assente.

Scrive data/sicurezza/solana_creator.jsonl (file suo, nessun altro lo tocca — vedi il guasto del 4/9
in cui due scrittori si distruggevano l'archivio a vicenda) + SOLANA_CREATOR.md. €0.
"""
import json, os, time, urllib.request

USCITA = "data/sicurezza/solana_creator.jsonl"
MAX = int(os.environ.get("MAX_TOKEN", 60))
BUDGET = int(os.environ.get("BUDGET_SEC", 240))
PAUSA = 0.2
now = int(time.time()); t0 = time.time()


def gia_fatti():
    out = {}
    if os.path.exists(USCITA):
        for l in open(USCITA):
            try:
                d = json.loads(l)
                if d.get("token"): out[d["token"]] = d
            except Exception: pass
    return out


def da_fare(fatti):
    """i token Solana censiti che non hanno ancora un creator."""
    out = []
    p = "data/sicurezza/solana.jsonl"
    if not os.path.exists(p): return out
    for l in open(p):
        try: d = json.loads(l)
        except Exception: continue
        tk = d.get("token")
        if tk and not d.get("creator") and tk not in fatti: out.append(tk)
    return list(dict.fromkeys(out))


def chiedi(key, mint):
    """(creator, come l'abbiamo trovato) oppure (None, perche' no) — il motivo e' un dato, non un errore."""
    body = json.dumps({"jsonrpc": "2.0", "id": "wr", "method": "getAsset",
                       "params": {"id": mint}}).encode()
    req = urllib.request.Request(f"https://mainnet.helius-rpc.com/?api-key={key}", data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        return None, f"http {e.code}"
    except Exception as e:
        return None, type(e).__name__
    res = d.get("result")
    if not isinstance(res, dict):
        return None, ("nessun risultato" if "error" not in d
                      else str(d["error"].get("message", "errore"))[:40])
    # i creators dichiarati nei metadati sono la firma piu' vicina a "chi l'ha fatto"
    for c in (res.get("creators") or []):
        if c.get("address"): return c["address"], "creators"
    for a in (res.get("authorities") or []):
        if a.get("address"): return a["address"], "authority"
    own = (res.get("ownership") or {}).get("owner")
    if own: return own, "owner"
    return None, "nessun creator nei metadati"


def main():
    key = os.environ.get("HELIUS_KEY", "").strip() or os.environ.get("HELIUS_KEY2", "").strip()
    fatti = gia_fatti()
    L = ["# 🧬 CHI HA CREATO IL TOKEN — Solana",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · €0*", "",
         "> Solana è la nostra chain più grossa e ha la copertura più bassa del creator. Senza quel",
         "> campo, la reputazione di chi crea i token — la pista più promettente che abbiamo — lì non",
         "> si può nemmeno testare.", ""]
    if not key:
        L += ["## ❌ Manca la chiave", "",
              "L'agente non può girare senza `HELIUS_KEY` fra i secret del repo. **Non scrive zero",
              "fingendo di aver lavorato**: dichiara che non ha potuto."]
        open("SOLANA_CREATOR.md", "w").write("\n".join(L))
        print("SOLANA_CREATOR | manca HELIUS_KEY: non ho girato", flush=True); return

    lista = da_fare(fatti)[:MAX]
    trovati = 0; motivi = {}; come = {}
    with open(USCITA, "a") as fo:
        for mint in lista:
            if time.time() - t0 > BUDGET: break
            cr, perche = chiedi(key, mint)
            if cr:
                trovati += 1; come[perche] = come.get(perche, 0) + 1
                fo.write(json.dumps({"token": mint, "chain": "solana", "ts": now,
                                     "creator": cr, "fonte": f"helius:{perche}"}) + "\n")
            else:
                motivi[perche] = motivi.get(perche, 0) + 1
            time.sleep(PAUSA)

    tot = len(fatti) + trovati
    L += [f"| | |", "|---|---|",
          f"| token interrogati in questo giro | {len(lista)} |",
          f"| creator trovati ora | **{trovati}** |",
          f"| creator raccolti in tutto | **{tot}** |", ""]
    if come:
        L += ["Da dove arriva il nome:", ""] + [f"- {k}: {v}" for k, v in sorted(come.items())] + [""]
    if motivi:
        L += ["Perché su alcuni non si trova (i motivi contano quanto i risultati):", ""] + \
             [f"- {k}: {v}" for k, v in sorted(motivi.items(), key=lambda x: -x[1])[:5]] + [""]
    if trovati == 0 and lista:
        L += ["> ⚠️ **Zero risultati su un giro pieno.** O la chiave non ha i permessi giusti, o la",
              "> risposta ha un formato diverso da quello che leggo. Va guardato: uno zero silenzioso",
              "> è il modo in cui un agente rotto sembra un agente che non ha niente da fare."]
    open("SOLANA_CREATOR.md", "w").write("\n".join(L))
    print(f"SOLANA_CREATOR | {len(lista)} interrogati | {trovati} trovati | totale {tot} | "
          f"motivi: {motivi}", flush=True)


if __name__ == "__main__":
    main()
