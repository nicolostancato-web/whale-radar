"""Otto conti con 378-393 transazioni: un caso o una flotta?

La spiegazione che salva l'ipotesi ("finanziatori diversi = persone vere")
va sospettata: finanziare da indirizzi diversi e' ESATTAMENTE cio' che
farebbe un operatore unico per sembrare in tanti.
Il numero che decide: quanto si sovrappongono i gettoni e gli slot.
Entita' = Jaccard SIMMETRICO >= 0.5 sui gettoni (min() fuse 31k conti in una).
"""
import sys, itertools, collections
sys.path.insert(0, "agents"); import solana_rpc as S

FLOTTA = ["6eBJ5dFVZMGz6Dobzw9kdu","A1CtnCqnxHVW8gbBPLN6vh","GGpeAobRNUzQEFUkdYrD2x",
          "4eAkjAQZkB93ZDLDqBKsdQ","9ap69Lct1B31cXtWopCTE1","ELrPiHAqwmTixGdGAjd6x7",
          "FumQUfyBJjrAU3JyeGMtCe","BegDtqRjVf3adLa7EMbL1T"]
DIST = "4B8nfUUvp3yAx3nP7oJKjSF7dCW8h6nCbhsZNsKXq9sB"

# gli indirizzi interi li ripesco dal distributore
sig = S.rpc("getSignaturesForAddress",[DIST,{"limit":70}]) or []
interi = {}
for x in sig:
    if x.get("err"): continue
    t = S.rpc("getTransaction",[x["signature"],{"maxSupportedTransactionVersion":2,
          "encoding":"jsonParsed","commitment":"confirmed"}])
    if not t: continue
    for a in t["transaction"]["message"]["accountKeys"]:
        p = a["pubkey"]
        for f in FLOTTA:
            if p.startswith(f): interi[f] = p

print(f"indirizzi interi ritrovati: {len(interi)}/8\n")
gett, slot = {}, {}
for f, w in interi.items():
    s = S.rpc("getSignaturesForAddress",[w,{"limit":120}]) or []
    g, sl = set(), set()
    for x in s[:45]:
        if x.get("err"): continue
        t = S.rpc("getTransaction",[x["signature"],{"maxSupportedTransactionVersion":2,
              "encoding":"jsonParsed","commitment":"confirmed"}])
        if not t: continue
        sl.add(t["slot"])
        for y in t["meta"].get("postTokenBalances",[]):
            if y.get("owner")==w: g.add(y["mint"])
    gett[f], slot[f] = g, sl
    print(f"   {f}… {len(g):>3} gettoni, {len(sl):>3} slot")

print("\n   sovrapposizione a coppie (Jaccard simmetrico sui gettoni)")
alti = 0; tot = 0
for a,b in itertools.combinations(gett,2):
    u = gett[a] | gett[b]
    if not u: continue
    j = len(gett[a] & gett[b])/len(u)
    cs = len(slot[a] & slot[b])
    tot += 1
    if j >= 0.5 or cs >= 5:
        alti += 1; print(f"      {a[:14]}~{b[:14]}  J={j:.2f}  slot comuni={cs}")
print(f"\n   coppie molto sovrapposte: {alti}/{tot}")
print("   -> " + ("UNA SOLA ENTITA' con piu' maschere: la 'distribuzione aperta' e' una fattoria"
      if alti > tot*0.3 else "conti INDIPENDENTI: la somiglianza dei conteggi non basta a condannarli"))
