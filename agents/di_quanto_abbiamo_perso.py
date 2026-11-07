"""Di QUANTO abbiamo perso. La distanza sottile.

L'IMPOSTAZIONE E' DI NICOLO' (5/11 sera): il goal dei giri e' assottigliare
la vicinanza. Ma "distanza 1" e' grossolana: dice che c'eravamo e abbiamo
perso, non DI QUANTO. Un conto che dice "perso per il 3%" si puo' chiudere;
uno che dice "perso" no.

COSA MISURA: per ogni liquidazione in cui eravamo nel pacchetto, quanto ha
incassato chi costruisce il blocco oltre le normali commissioni -- cioe' il
pagamento interno del vincitore -- e lo confronta con quello che offrivamo
noi. Il metodo del residuo:
   pagato = (saldo del costruttore a N) - (a N-1) - priority fee di tutte le
            tx - prelievi dei validatori - trasferimenti espliciti
I saldi storici li servono solo drpc e blastapi: il nostro nodo no.

IL LIMITE, dichiarato: il residuo e' di BLOCCO, non del singolo searcher. Se
nel blocco c'e' altro MEV, il numero e' gonfiato. Quindi vale come ordine di
grandezza e come TENDENZA fra un giro e l'altro, non come cifra esatta.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registri as R

D = "data/liquidazioni"
FUORI = f"{D}/di_quanto_abbiamo_perso.json"


def pagato_dal_vincitore(n):
    """(pagamento interno in ETH, costruttore) oppure (None, perche')."""
    b = R.blocco(n, True)
    if not b:
        return None, "il blocco non si e' letto"
    cb = b["miner"].lower()
    base = int(b["baseFeePerGas"], 16)
    s0 = s1 = None
    for u in R.FONTI[1:]:                 # il nostro nodo non serve lo storico
        try:
            s0 = R._chiedi(u, "eth_getBalance", [cb, hex(n - 1)])
            s1 = R._chiedi(u, "eth_getBalance", [cb, hex(n)])
            if s0 and s1:
                break
        except Exception:
            s0 = s1 = None
    if not (s0 and s1):
        return None, "i saldi storici non si sono letti"
    delta = (int(s1, 16) - int(s0, 16)) / 1e18
    rr = None
    for u in R.FONTI:
        try:
            rr = R._chiedi(u, "eth_getBlockReceipts", [hex(n)])
            if rr:
                break
        except Exception:
            rr = None
    if not rr:
        return None, "le ricevute non si sono lette"
    prio = sum(max(0, int(r.get("effectiveGasPrice", "0x0"), 16) - base)
               * int(r.get("gasUsed", "0x0"), 16) for r in rr) / 1e18
    esp = sum(int(t.get("value", "0x0"), 16) for t in b["transactions"]
              if (t.get("to") or "").lower() == cb) / 1e18
    wd = sum(int(w["amount"], 16) * 1e9
             for w in (b.get("withdrawals") or [])
             if (w.get("address") or "").lower() == cb) / 1e18
    return delta - prio - esp - wd, cb


def misura():
    try:
        q = json.load(open(f"{D}/perche_lui_e_non_io.json"))
    except FileNotFoundError:
        print("   di quanto abbiamo perso: non c'e' ancora un'autopsia")
        return None
    pz = json.load(open(f"{D}/prezzi_oracolo.json"))[
        "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"]["prezzo_usd"]
    import indirizzi as I
    righe = []
    for c in (q.get("casi") or []):
        if c.get("distanza") != 1:
            continue
        res, chi = pagato_dal_vincitore(c["blocco_catena"])
        prem = c.get("premio") or 0
        # quello che offrivamo noi: la frazione del guadagno vero stimato
        nostra = prem / I.QUANTO_IL_PREMIO_GONFIA * I.FRAZIONE_MANCIA
        righe.append({
            "blocco": c["blocco_catena"], "premio": prem,
            "pagato_dal_vincitore_usd": (res * pz) if res is not None else None,
            "quota_del_vincitore": (res * pz / prem) if (res is not None and prem) else None,
            "nostra_offerta_usd": nostra,
            "nostra_quota": nostra / prem if prem else None,
            "perche_no": None if res is not None else chi,
            "costruttore": chi if res is not None else None})
    out = {"quando": time.time(), "casi": righe}
    tmp = FUORI + ".tmp"
    json.dump(out, open(tmp, "w"), indent=1)
    os.replace(tmp, FUORI)
    if not righe:
        print("   di quanto abbiamo perso: nessun caso a distanza 1")
        return out
    print(f"   DI QUANTO ABBIAMO PERSO ({len(righe)} casi in cui c'eravamo):")
    noti = [r for r in righe if r["quota_del_vincitore"] is not None]
    for r in righe:
        if r["quota_del_vincitore"] is None:
            print(f"     ${r['premio']:>8,.0f}  non lo so: {r['perche_no']}")
            continue
        print(f"     ${r['premio']:>8,.0f}  lui ha pagato ${r['pagato_dal_vincitore_usd']:>9,.0f} "
              f"({100*r['quota_del_vincitore']:>6.1f}% del premio) | "
              f"noi offrivamo ${r['nostra_offerta_usd']:>7,.0f} "
              f"({100*r['nostra_quota']:.1f}%)")
    if noti:
        qv = sorted(r["quota_del_vincitore"] for r in noti)
        print(f"     quota pagata dai vincitori: mediana {100*qv[len(qv)//2]:.1f}%"
              f" | la nostra: {100*noti[0]['nostra_quota']:.1f}%")
    return out


if __name__ == "__main__":
    misura()
