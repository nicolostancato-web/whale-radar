"""I 53 SOL del ricevente sono guadagno o sono i soldi del mittente che tornano?

Un portafoglio che riceve e vende mostra solo RICAVI: il costo sta sull'altra
mano. La domanda di Nicolo' ("si riesce a trarre profitto?") si risponde solo
CONSOLIDANDO mittente + ricevente, come per un'unica azienda.

Regola gia' imparata: il guadagno di un'entita' =
   incassi esterni - esborsi esterni, cancellando i giri interni.
"""
import sys, collections
sys.path.insert(0, "agents"); import solana_rpc as S

COPPIE = [("GU63SH4oyp", "B6jqNwTJNyZPEeXFdoYuxGWeEtM2FX9dX7ZmzjovaVHg"),
          ("3XDcE2tQRo", "BegDtqRjVf3adLa7EMbL1T")]
MAX_TX = 120

def interi_da(w, pref):
    s = S.rpc("getSignaturesForAddress", [w, {"limit": 60}]) or []
    for x in s:
        if x.get("err"): continue
        t = S.rpc("getTransaction", [x["signature"], {"maxSupportedTransactionVersion":2,
              "encoding":"jsonParsed","commitment":"confirmed"}])
        if not t: continue
        for a in t["transaction"]["message"]["accountKeys"]:
            if a["pubkey"].startswith(pref): return a["pubkey"], t
    return None, None

def flussi(w, limite):
    """SOL netto del portafoglio w, separando i giri col socio."""
    s = S.rpc("getSignaturesForAddress", [w, {"limit": limite}]) or []
    tot = 0.0; n = 0; controparti = collections.Counter()
    for x in s:
        if x.get("err"): continue
        t = S.rpc("getTransaction", [x["signature"], {"maxSupportedTransactionVersion":2,
              "encoding":"jsonParsed","commitment":"confirmed"}])
        if not t: continue
        acc = [a["pubkey"] for a in t["transaction"]["message"]["accountKeys"]]
        if w not in acc: continue
        i = acc.index(w)
        d = (t["meta"]["postBalances"][i] - t["meta"]["preBalances"][i]) / 1e9
        tot += d; n += 1
        for j, a in enumerate(acc):
            if a != w and abs(t["meta"]["postBalances"][j]-t["meta"]["preBalances"][j]) > 1e7:
                controparti[a] += 1
    return tot, n, controparti

for pref, ric in COPPIE:
    print(f"\n=== ricevente {ric[:20]}… / mittente {pref}… ===")
    mitt, _ = interi_da(ric, pref)
    if not mitt:
        print("   mittente intero non ritrovato"); continue
    sr, nr, cr = flussi(ric, MAX_TX)
    sm, nm, cm = flussi(mitt, MAX_TX)
    print(f"   ricevente: {sr:+.3f} SOL netti su {nr} transazioni")
    print(f"   mittente : {sm:+.3f} SOL netti su {nm} transazioni")
    print(f"   CONSOLIDATO: {sr+sm:+.3f} SOL  (~{(sr+sm)*170:+,.0f} EUR a 170 EUR/SOL)")
    gira = cr.get(mitt,0) + cm.get(ric,0)
    print(f"   transazioni fra i due (giri interni): {gira}")
    print("   -> " + ("L'ENTITA' GUADAGNA DAVVERO" if sr+sm > 1 else
          "i soldi del ricevente sono l'esborso del mittente: NON e' guadagno"))
    print(f"   nota: finestra di {MAX_TX} transazioni per lato, non la storia intera")
