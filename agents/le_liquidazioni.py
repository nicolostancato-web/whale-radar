"""Liquidazioni su Aave v3: il mestiere pagato per abilita' SENZA cancello.

Perche' e' diverso da tutto: con un prestito lampo si liquida senza mettere
capitale — prendi in prestito, ripaghi il debito altrui, incassi il premio e
restituisci, tutto in una transazione. Se non conviene, non avviene: si
rischia solo il gas.

Si misura: quante ce ne sono in un giorno, quanto pagano, e quanto e'
concentrato chi le prende. Se un solo indirizzo ne fa il 90%, c'e' un muro
di velocita'; se sono tanti, c'e' spazio.
"""
import sys, collections, json
sys.path.insert(0,"agents")
import base_rpc as B
from keccak import firma
POOL="0xa238dd80c259a72e81d7e4664a9801593f98d1c5"   # Aave v3 su Base
LIQ=firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
print(f"   firma evento: {LIQ[:18]}...")
ult=int(B.chiama("eth_blockNumber") or "0x0",16)
GIORNO=43200          # ~1 giorno di blocchi su Base (2 secondi)
print(f"   finestra: {GIORNO} blocchi (~1 giorno), fino a {ult}")
tutti=[]; falliti=0; finestre=0
for b in range(ult-GIORNO, ult, 900):
    r=B.log_di_finestra(LIQ, b, min(b+899,ult), indirizzo=POOL)
    finestre+=1
    if r is None: falliti+=1; continue
    tutti+=r
print(f"   finestre lette {finestre}, fallite {falliti}  "
      f"({falliti/finestre*100:.0f}% — se alta, il conto e' sottostimato)")
print(f"   liquidazioni trovate: {len(tutti)}\n")
if not tutti:
    print("   nessuna liquidazione in questa finestra su questa chain.")
    sys.exit(0)
chi=collections.Counter(); utenti=set()
for x in tutti:
    d=x["data"][2:]
    # dati non indicizzati: debtToCover, liquidatedCollateral, liquidator, receiveAToken
    if len(d)>=64*3:
        chi["0x"+d[64*2+24:64*3]]+=1
    if len(x["topics"])>3: utenti.add(x["topics"][3][-40:])
print(f"   {len(chi)} liquidatori diversi | {len(utenti)} utenti liquidati")
tot=sum(chi.values())
for a,n in chi.most_common(10):
    print(f"      {a[:42]:<44}{n:>4}  {n/tot*100:>5.1f}%")
primo = chi.most_common(1)[0][1]/tot*100 if tot else 0
print(f"\n   quota del primo: {primo:.0f}%")
print(f"   -> {'muro di velocita (uno solo prende tutto)' if primo>70 else 'spazio: il mestiere e distribuito'}")
