"""Contratto o portafoglio? La differenza fra «l'ha fatta un'azienda» e «l'ha
fatto uno».

Grok ha troncato due volte (abbonamento che limita dopo quattro consultazioni
pesanti), quindi la parte che si puo' sapere dalla chain la si prende dalla
chain: codice presente o no, saldo, e da quanto esiste l'indirizzo.
"""
import sys
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import keccak256
APP=["0x7bf90111ad7c22bec9e9dff8a01a44713cc1b1b6",
     "0x0469a4bd3724dc86c9542f4694c976da13c450c0",
     "0xf1bc42fa0a54dab2b66a3bbd6b8e268d3d08d3af",
     "0x67421e82e0157a3ca9508ee92f6417a93bbf59cb",
     "0xc8d077444625eb300a427a6dfb2b1dbf9b159040",
     "0x5aafc1f252d544f744d17a4e734afd6efc47ede4",
     "0xc06ebbefd94032b85424d51906e2a335efae264b",
     "0x885b00aa42f066d6c3fe944c10b1c6f8dbcdcd43"]
def sel(s): return "0x"+keccak256(s.encode()).hex()[:8]
print("   indirizzo                                    tipo        saldo ETH   n. operazioni")
for a in APP:
    code=B.chiama("eth_getCode",[a,"latest"])
    tipo = "CONTRATTO" if code and len(code)>4 else "portafoglio"
    bal=B.chiama("eth_getBalance",[a,"latest"])
    eth=int(bal,16)/1e18 if isinstance(bal,str) else float("nan")
    n=B.chiama("eth_getTransactionCount",[a,"latest"])
    nn=int(n,16) if isinstance(n,str) else -1
    extra=""
    if tipo=="CONTRATTO":
        for f in ("owner()","name()"):
            r=B.chiama("eth_call",[{"to":a,"data":sel(f)},"latest"])
            if r and len(r)>2:
                if f=="owner()": extra=f"  proprietario {('0x'+r[-40:])[:14]}…"
                break
    print(f"   {a}  {tipo:<11} {eth:>10.4f}   {nn:>6}{extra}")
print("\n   un PORTAFOGLIO che incassa = la cassa di un progetto piccolo")
print("   un CONTRATTO con proprietario = un prodotto strutturato")
print("   (il numero di operazioni conta solo per i portafogli: per i contratti e' sempre 1)")
