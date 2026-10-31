"""La spiegazione che salva l'ipotesi, verificata con un numero.

28 destinatari serviti una volta sola SEMBRA una distribuzione aperta.
Ma se i conti nuovi sono portafogli del distributore stesso, e' una mano sola.
Si distingue dal PRIMO bonifico in SOL: chi ha acceso il conto.
Prima transazione = l'ULTIMA della lista (le firme tornano dalla piu' recente).
"""
import sys, collections
sys.path.insert(0, "agents"); import solana_rpc as S
DIST = "4B8nfUUvp3yAx3nP7oJKjSF7dCW8h6nCbhsZNsKXq9sB"

sig = S.rpc("getSignaturesForAddress", [DIST, {"limit": 70}]) or []
dest = {}
for x in sig:
    if x.get("err"): continue
    t = S.rpc("getTransaction", [x["signature"], {"maxSupportedTransactionVersion":2,
          "encoding":"jsonParsed","commitment":"confirmed"}])
    if not t: continue
    meta = t["meta"]
    pre = {y["accountIndex"]: float(y["uiTokenAmount"]["uiAmount"] or 0)
           for y in meta.get("preTokenBalances", [])}
    for y in meta.get("postTokenBalances", []):
        o = y.get("owner")
        if o and o != DIST and float(y["uiTokenAmount"]["uiAmount"] or 0)-pre.get(y["accountIndex"],0.0) > 0:
            dest.setdefault(o, 0); dest[o] += 1

print(f"{len(dest)} destinatari | cerco CHI HA ACCESO ognuno\n")
fin = collections.Counter(); visti = 0
for d in list(dest)[:14]:
    s = S.rpc("getSignaturesForAddress", [d, {"limit": 1000}]) or []
    if not s: continue
    prima = s[-1]["signature"]          # l'ULTIMA e' la PIU' VECCHIA
    t = S.rpc("getTransaction", [prima, {"maxSupportedTransactionVersion":2,
          "encoding":"jsonParsed","commitment":"confirmed"}])
    if not t: continue
    visti += 1
    acc = [a["pubkey"] for a in t["transaction"]["message"]["accountKeys"]]
    pre_b, post_b = t["meta"]["preBalances"], t["meta"]["postBalances"]
    pagatore = "?"
    for i, a in enumerate(acc):
        if a != d and post_b[i] - pre_b[i] < -1_000_000:   # ha perso >0.001 SOL
            pagatore = a; break
    fin[pagatore] += 1
    eta = "nuovo" if len(s) < 100 else "vecchio"
    print(f"   {d[:22]}… ({len(s):>4} tx, {eta:<7}) acceso da {pagatore[:30]}")

print(f"\n   finanziatori distinti su {visti} conti: {len(fin)}")
for f, n in fin.most_common(5):
    print(f"      {f[:38]:<40} {n}  {'<-- E IL DISTRIBUTORE' if f==DIST else ''}")
dom = fin.most_common(1)[0][1]/max(visti,1) if fin else 0
print(f"\n   quota del finanziatore principale: {dom:.0%}")
print("   -> " + ("UNA MANO SOLA: non e' una distribuzione aperta"
      if dom > 0.5 else "FINANZIATORI DIVERSI: sono persone vere, la lista ha dei criteri"))
