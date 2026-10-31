"""LA STORIA COMPLETA DI UN PORTAFOGLIO, con dentro tutto quello che conta.

Rifatto dopo l'audit del 22/10. Tre correzioni rispetto alla versione ritirata:
 1. SI LEGGONO SOLO LE STORIE COMPLETE, scelte dallo screening (meno di 1000 firme): cosi'
    «incassato meno speso» e' la carriera e non l'ultima settimana. La versione precedente
    prendeva 200 firme dal piu' recente, cioe' le vendite di adesso senza gli acquisti di un
    mese fa: quei saldi sono stati ritirati.
 2. L'OPERATORE E' IL PROPRIETARIO DEL CONTO GETTONE, non il firmatario: cosi' entrano anche
    le operazioni instradate da un bot, che prima sparivano.
 3. ENTRANO LE TRANSAZIONI DI SOLI SOL: le mance ai validatori sono un COSTO vero e gli
    incassi di commissioni un RICAVO vero. Prima venivano buttate via dentro transazioni
    che stavamo gia' pagando per leggere.

E si salva anche la QUANTITA' di gettoni mossa, che serve per valutare l'inventario rimasto
in mano invece di segnarlo a zero per decreto.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import solana_rpc as S

PUMP = "6EF8rrecthR5Dkzon8Nwu78hRvfCKubJ14M5uBEwF6P"

SCREEN = "data/multichain/solana/screening.jsonl"
FUORI = "data/multichain/solana/storia2.jsonl"
FATTI = "data/multichain/solana/storia2_fatti.json"
TETTO_CREDITI = int(os.environ.get("TETTO_CREDITI", "8000"))


def leggi(sig, w):
    """Ritorna (tipo, dati) per una transazione: scambio, mancia, incasso, o nulla."""
    t = S.rpc("getTransaction", [sig, {"maxSupportedTransactionVersion": 2,
                                       "encoding": "jsonParsed", "commitment": "confirmed"}])
    if not t or t.get("meta", {}).get("err"):
        return None
    meta = t["meta"]
    chiavi = [a["pubkey"] if isinstance(a, dict) else a
              for a in t["transaction"]["message"]["accountKeys"]]
    if w not in chiavi:
        return None
    dsol = {k: (b - a) / 1e9 for k, a, b in zip(chiavi, meta["preBalances"], meta["postBalances"])}
    mio = dsol.get(w, 0.0)
    pre = {x["accountIndex"]: float(x["uiTokenAmount"]["uiAmount"] or 0)
           for x in meta.get("preTokenBalances", [])}
    dget = 0.0
    mint = None
    for x in meta.get("postTokenBalances", []):
        if x.get("owner") != w or x["mint"] == S.SOL:
            continue
        d = float(x["uiTokenAmount"]["uiAmount"] or 0) - pre.get(x["accountIndex"], 0.0)
        if abs(d) > abs(dget):
            dget, mint = d, x["mint"]
    if mint and dget and mio and (mio < 0) != (dget < 0):
        # RICEVUTO NON E' COMPRATO (23/10, verificato sulla chain). Un portafoglio che riceve
        # 14 milioni di gettoni da un distributore paga solo la CAUZIONE del conto, 0,001523
        # SOL: il lettore la leggeva come prezzo d'acquisto e ne usciva un «compra a 27
        # centesimi, vende a 500 euro», 54 volte su 54. I tre «migliori trader» non
        # compravano nulla. Un ingresso di gettoni con un'uscita di SOL pari alla cauzione,
        # e con i gettoni che arrivano da un INDIRIZZO invece che dal mercato, e' un REGALO.
        da_indirizzo = any(
            (y.get("owner") not in (None, w_none := None) and y["mint"] == mint
             and float(y["uiTokenAmount"]["uiAmount"] or 0) - pre.get(y["accountIndex"], 0.0) < 0
             and y.get("owner") != w)
            for y in meta.get("postTokenBalances", []))
        cauzione = 0.0012 < abs(mio) < 0.0025
        if dget > 0 and cauzione and da_indirizzo:
            return ("regalo", [t["slot"], mint, round(abs(dget), 4), round(abs(mio), 6)])
        return ("scambio", [t["slot"], abs(mio / dget), mio < 0, mint, round(abs(mio), 6),
                            round(abs(dget), 4)])
    if abs(mio) > 1e-9 and not mint:
        # SOLI SOL: tre cose diverse che finivano nella stessa colonna (22/10, verificato
        # sulla chain). Un portafoglio che risultava il piu' profittevole con +12,54 SOL
        # aveva solo RICEVUTO 28 SOL con un bonifico: non guadagnava niente.
        #   system        = ricarica o prelievo fra portafogli propri  -> NON e' guadagno
        #   spl-token     = cauzione del conto gettone restituita      -> NON e' guadagno
        #   pump.fun      = commissioni riscosse a blocchi             -> E' guadagno
        progs = set()
        for i in t["transaction"]["message"].get("instructions", []):
            q = i.get("program") or i.get("programId") or ""
            if "ComputeBudget" not in str(q):
                progs.add(str(q))
        if PUMP in progs:
            tipo = "commissioni"
        elif any("spl-token" in q or "associated" in q for q in progs):
            tipo = "cauzione"
        elif progs <= {"system"}:
            tipo = "bonifico"
        else:
            tipo = "altro"
        return ("solo_sol", [t["slot"], round(mio, 9), tipo])
    return None


def main():
    if not S.url():
        return 1
    scelti = [json.loads(x) for x in open(SCREEN)]
    scelti = [x for x in scelti if x["completa"] and x["riuscite"] >= 20]
    fatti = set(json.load(open(FATTI))) if os.path.exists(FATTI) else set()
    coda = [x for x in scelti if x["w"] not in fatti]
    print(f"STORIA2 | {len(scelti)} portafogli completi, da fare {len(coda)}", flush=True)
    costo = 0
    with open(FUORI, "a") as fh:
        for x in coda:
            if costo >= TETTO_CREDITI:
                print(f"   tetto {TETTO_CREDITI:,} crediti raggiunto, mi fermo e lo dico", flush=True)
                break
            w = x["w"]
            sig = S.rpc("getSignaturesForAddress", [w, {"limit": 1000}]) or []
            ops, sol, regali = [], [], []
            for y in sig:
                if y.get("err") or costo >= TETTO_CREDITI:
                    continue
                r = leggi(y["signature"], w)
                costo += 1
                if not r:
                    continue
                if r[0] == "scambio":
                    ops.append(r[1])
                elif r[0] == "regalo":
                    regali.append(r[1])
                else:
                    sol.append(r[1])
                time.sleep(0.01)
            ops.sort()
            fh.write(json.dumps({"w": w, "seme": x["seme"], "firme": len(sig),
                                 "ops": ops, "solo_sol": sol, "regali": regali}) + "\n")
            fh.flush()
            fatti.add(w)
            print(f"   {w[:14]} [{x['seme']}]: {len(ops)} scambi su "
                  f"{len({o[3] for o in ops})} gettoni, {len(sol)} movimenti di soli SOL, "
                  f"{len(regali)} gettoni RICEVUTI", flush=True)
    json.dump(sorted(fatti), open(FATTI, "w"))
    print(f"STORIA2 | fatti {len(fatti)}/{len(scelti)} | costo ~{costo:,} crediti")
    return 0


if __name__ == "__main__":
    sys.exit(main())
