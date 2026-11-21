"""Kleros: quanto spesso viene estratto un giurato, e quanto si guadagna.

Primo dei due candidati «pagati a cottimo» che sopravvivono alla soglia dei
costi, perche' non pagano pedaggio: non compri niente, fornisci un giudizio.
Il compenso e' pubblicato (0,005 ETH per voto coerente nella Corte Generale);
la FREQUENZA no, ed e' quella che decide se e' un reddito o un aneddoto.

Indirizzo verificato, non ricordato: si controlla che abbia codice e che emetta
le firme attese, calcolate con keccak.
"""
import sys, json, urllib.request, collections
sys.path.insert(0,"agents"); from keccak import keccak256
RPC="https://ethereum-rpc.publicnode.com"
K="0x988b3a538b618c7a603e1c11ab82cd16dbe28069"   # KlerosLiquid, da verificare
def rpc(m,p):
    r=urllib.request.Request(RPC,json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),
        {"content-type":"application/json","user-agent":"Mozilla/5.0"})
    try:
        with urllib.request.urlopen(r,timeout=45) as f: return json.load(f).get("result")
    except Exception: return None
def firma(s): return "0x"+keccak256(s.encode()).hex()
code=rpc("eth_getCode",[K,"latest"])
print(f"KlerosLiquid a {K[:12]}…: {'PRESENTE ('+str(len(code)//2)+' byte)' if code and len(code)>4 else 'ASSENTE'}")
if not code or len(code)<=4: raise SystemExit
ult=int(rpc("eth_blockNumber",[]),16)
GIORNI=30; BL=int(GIORNI*24*3600/12)      # ~12 s per blocco su Ethereum
FIRME={firma("Draw(address,uint256,uint256,uint256)"):"Draw",
       firma("NewPeriod(uint256,uint8)"):"NewPeriod",
       firma("DisputeCreation(uint256,address)"):"DisputeCreation",
       firma("TokenAndETHShift(address,uint256,int256,int256)"):"TokenAndETHShift"}
c=collections.Counter(); giurati=collections.Counter(); premi=[]
PASSO=40000
for b in range(ult-BL, ult, PASSO):
    L=rpc("eth_getLogs",[{"address":K,"fromBlock":hex(b),"toBlock":hex(min(b+PASSO-1,ult))}])
    if not isinstance(L,list): continue
    for x in L:
        t=x["topics"][0]; c[FIRME.get(t,t[:12])]+=1
        if FIRME.get(t)=="Draw" and len(x["topics"])>1:
            giurati["0x"+x["topics"][1][-40:]]+=1
print(f"\n   ultimi {GIORNI} giorni: {sum(c.values())} eventi")
for k,v in c.most_common(6):
    print(f"      {k:<22} {v:>5}   ({v/GIORNI:.1f} al giorno)")
if giurati:
    print(f"\n   giurati distinti estratti: {len(giurati)}")
    print(f"   estrazioni per giurato: mediana {sorted(giurati.values())[len(giurati)//2]}, "
          f"massimo {max(giurati.values())}")
    tot=sum(giurati.values())
    print(f"   un giurato medio viene estratto {tot/len(giurati)/GIORNI:.2f} volte al giorno")
    print(f"   a 10,46 EUR per voto: {tot/len(giurati)/GIORNI*10.46:.2f} EUR al giorno")
