"""La tabellina di ogni giro: Nicolo' deve capire in cinque secondi se sono
sul pezzo.

Chiesto il 5/11 sera: un aggiornamento ogni 30 minuti, breve, con una tabella
riassuntiva sempre UGUALE -- cosi' si legge la differenza fra un giro e
l'altro invece di rileggere tutto.
Si legge dai file di stato, non rifa' le misure: il C-check e le guardie
girano da soli ogni 15 minuti.
"""
import json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

D = "data/liquidazioni"


def _j(nome):
    try:
        return json.load(open(f"{D}/{nome}"))
    except Exception:
        return None


def riga(eti, valore, nota=""):
    print(f"   {eti:<26} {valore:<22} {nota}")


def tabella():
    import pescatore as P
    import indirizzi as I
    # il live
    q = _j("perche_lui_e_non_io.json") or {}
    casi = q.get("casi") or []
    d1 = [c for c in casi if c.get("distanza") == 1]
    d25 = [c for c in casi if (c.get("distanza") or 0) >= 2]
    vinte = [c for c in casi if c.get("vinta_da_noi")]
    sv = _j("da_quando_siamo_veri.json") or {}
    # l'offerta
    dq = _j("di_quanto_abbiamo_perso.json") or {}
    noti = [r for r in (dq.get("casi") or [])
            if r.get("quota_del_vincitore") is not None]
    loro = None
    if noti:
        v = sorted(r["quota_del_vincitore"] for r in noti)
        loro = v[len(v) // 2]
    nostra = noti[0].get("nostra_quota") if noti else None
    # il gas
    saldo = base = None
    for _ in range(3):
        x = P.rpc("eth_getBalance",
                  ["0x4355962379c779009f833d81bd8d2912773749a0", "latest"])
        if x:
            saldo = int(x, 16) / 1e18
            break
        time.sleep(0.8)
    for _ in range(3):
        b = P.rpc("eth_getBlockByNumber", ["latest", False])
        if b:
            base = int(b["baseFeePerGas"], 16) / 1e9
            break
        time.sleep(0.8)
    fino = (saldo / (1_100_000 * 1e-9)) if saldo else None
    # il cassetto e i blocchi
    VP = _j("vendite_pronte.json") or {}
    pronti = sum(1 for v in VP.values() if v.get("chiamata"))
    bl = _j("blocchi.json") or {}
    righe = bl.get("righe") or []
    cento = sum(1 for r in righe if (r.get("percento") or 0) >= 100)
    cassa = (_j("cassa.json") or {}).get("valore_usd")
    sen = _j("sentinella_viva.json") or {}

    print("   COSA                       ADESSO                 NOTA")
    riga("liquidazioni nel mondo",
         f"{len(casi)} in {sv.get('ore','?')}h",
         f"vinte da noi: {len(vinte)}")
    riga("di cui c'eravamo (dist. 1)", f"{len(d1)}",
         f"fuori dal pacchetto: {len(d25)}")
    riga("nostra offerta",
         f"{100*nostra:.1f}% del premio" if nostra else "non misurata",
         f"loro {100*loro:.1f}% (mediana)" if loro else "")
    riga("gas", f"{base:.2f} gwei" if base else "non lo so",
         f"in gara fino a {fino:.0f} gwei ({fino/base:.0f}x)"
         if (fino and base) else "")
    riga("portafoglio del gas",
         f"{saldo:.4f} ETH" if saldo else "non lo so",
         f"{saldo/(1_100_000*4*1e-9):.0f} vittorie a 4 gwei" if saldo else "")
    riga("ordini pronti", f"{pronti} su {len(VP)}",
         f"offerta su {sum(1 for v in VP.values() if (v.get('mancia_wei') or 0)>0)}")
    riga("pacchetti spediti",
         f"{sen.get('composti','?')} composti",
         f"accettati {sen.get('accettati','?')}")
    riga("blocchi al 100%", f"{cento} su {len(righe)}",
         ", ".join(f"{r['blocco'].split('.')[0]}:{r['percento']}%"
                   for r in righe if (r.get("percento") or 0) < 100) or "tutti")
    riga("cassa", f"${cassa}" if cassa is not None else "non lo so", "")


if __name__ == "__main__":
    tabella()
