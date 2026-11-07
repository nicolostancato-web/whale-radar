"""Gli zeri degli altri protocolli sono veri o e' sbagliata la mia configurazione?

Controllo in due passi, per ogni indirizzo:
  1) ha QUALSIASI log in questa finestra? Se no, l'indirizzo e' sbagliato o
     il contratto e' inattivo — non e' una prova che non ci siano liquidazioni.
  2) fra i log presenti, compare la firma che sto cercando? Se l'indirizzo
     e' vivo ma la firma non c'e' mai, la firma e' sbagliata.
"""
import json, time, urllib.request, sys, collections
sys.path.insert(0,"agents")
from keccak import firma
PROT={
 "aave_v3":   ("0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2",
               firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")),
 "spark":     ("0xc13e21b648a5ee794902342038ff3adab66be987",
               firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")),
 "morpho":    ("0xbbbbbbbbbb9cc5e90e3b3af64bdaf62c37eeffcb",
               firma("Liquidate(bytes32,address,address,uint256,uint256,uint256,uint256,uint256)")),
 "compound3": ("0xc3d688b66703497daa19211eedff47f25384cdc3",
               firma("AbsorbCollateral(address,address,address,uint256,uint256)")),
}
RPC=["https://eth.llamarpc.com","https://ethereum-rpc.publicnode.com",
     "https://rpc.ankr.com/eth","https://cloudflare-eth.com"]
def chiama(m,p=None,giri=6):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p or []}).encode()
    for g in range(giri):
        for u in RPC:
            try:
                r=urllib.request.Request(u,data=c,headers={
                  "content-type":"application/json","user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=30))
                if "result" in d and d["result"] is not None: return d["result"]
            except Exception: pass
        time.sleep(0.4*(g+1))
    return None
ult=int(chiama("eth_blockNumber"),16)
for nome,(ind,sig) in PROT.items():
    codice=chiama("eth_getCode",[ind,"latest"])
    vivo = codice and len(codice)>4
    tutti=[]
    b=ult-600
    while b<ult:
        f=min(b+199,ult)
        r=chiama("eth_getLogs",[{"fromBlock":hex(b),"toBlock":hex(f),"address":ind}])
        if r: tutti+=r
        b=f+1; time.sleep(0.1)
    firme=collections.Counter(x["topics"][0] for x in tutti if x.get("topics"))
    print(f"\n   {nome}  {ind[:14]}...")
    print(f"      contratto esiste: {'si' if vivo else 'NO — indirizzo sbagliato'}")
    print(f"      log in 600 blocchi: {len(tutti)}  ({len(firme)} firme diverse)")
    print(f"      la mia firma {sig[:14]}... {'C E' if sig in firme else 'non compare'}")
    if tutti and sig not in firme:
        print(f"      firme viste piu' spesso:")
        for s,n in firme.most_common(3): print(f"         {s[:20]}... x{n}")
