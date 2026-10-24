"""Esiste il mestiere di MERCANTE (mettere liquidita') dopo il diploma?

403 su blocchi vecchi = limite d'archivio della chain (lezione di Base: il 403
non e' un errore passeggero, e' il confine). Quindi si guarda OGGI.

Tre domande, in ordine di quanto chiudono la faccenda:
  1. qualcuno mette/toglie liquidita' (ModifyLiquidity)? se no, non c'e' mestiere
  2. l'hook restituisce agli LP (Donate)? era l'ipotesi di Astra
  3. quanta commissione pagano i traders in una finestra, e su quale liquidita'
"""
import json, os, urllib.request, collections
RPC = os.environ.get("RPC_ROBINHOOD", "https://rpc.mainnet.chain.robinhood.com")
GEST = "0x8366a39cc670b4001a1121b8f6a443a643e40951"
INIT="0xdd466e674ea557f56295e2d0218a125ea4b4f0f6f3307b95f85e6110838d6438"
MODL="0xf208f4912782fd25c7f114ca3723a2d5dd6f3bcc3ac8db5af63baa85f711d5ec"
DONA="0x29ef05caaff9404b7cb6d1c0e9bbae9eaa7ab2541feba1a9c4248594c08156cb"
SWAP="0x40e9cecb9f5f1f1c5b9c97dec2917b7ee92e57ba5563708daca94dd84ad7112f"
NOMI={INIT:"Initialize",MODL:"ModifyLiquidity",DONA:"Donate",SWAP:"Swap"}

def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,
      "params":p}).encode(),{"content-type":"application/json","user-agent":"Mozilla/5.0"})
    with urllib.request.urlopen(r,timeout=60) as f:
        return json.load(f).get("result")

ult=int(rpc("eth_blockNumber",[]),16)
FIN=2000                      # ~4,6 minuti a 0,093 s/blocco
print(f"ultimo blocco {ult:,} | finestra {FIN} blocchi (~{FIN*0.093/60:.0f} min)\n")
c=collections.Counter(); pool_mod=collections.Counter(); pool_swap=collections.Counter()
passo=100
for b in range(ult-FIN, ult, passo):
    logs=rpc("eth_getLogs",[{"address":GEST,"topics":[[INIT,MODL,DONA,SWAP]],
             "fromBlock":hex(b),"toBlock":hex(min(b+passo-1,ult))}]) or []
    for L in logs:
        n=NOMI.get(L["topics"][0],"?"); c[n]+=1
        if n=="ModifyLiquidity": pool_mod[L["topics"][1]]+=1
        if n=="Swap": pool_swap[L["topics"][1]]+=1
print("   eventi nella finestra:")
for k,v in c.most_common(): print(f"      {k:<18} {v:,}")
print(f"\n   pool con scambi: {len(pool_swap)} | pool dove si TOCCA la liquidita': {len(pool_mod)}")
print(f"   rapporto scambi/mosse di liquidita': {c['Swap']/max(c['ModifyLiquidity'],1):.1f}")
print("\n   -> " + ("NESSUN mercante: la liquidita' non si muove, non c'e' mestiere da imitare"
      if c["ModifyLiquidity"]==0 else
      ("Donate presente: l'hook RESTITUISCE agli LP (ipotesi di Astra confermata)"
       if c["Donate"]>0 else "la liquidita' si muove ma nessun Donate: la commissione non torna agli LP via hook")))
