# -*- coding: utf-8 -*-
"""A che ORA e in che GIORNO cadono le liquidazioni?

Domanda di Nicolo' (2/11): il mercato si muove di piu' negli orari americani
e nei giorni lavorativi? Si misura, non si suppone: ogni liquidazione porta
il suo blocco, e il blocco si converte in ora.
"""
import json, sys, time, urllib.request
from collections import Counter
sys.path.insert(0,"agents")
D="data/liquidazioni"
PR=json.load(open(f"{D}/prezzi_oracolo.json"))
S=json.load(open(f"{D}/novanta_giorni.json"))
U="https://gateway.tenderly.co/public/mainnet"
def rpc(m,p):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    r=urllib.request.Request(U,data=c,headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
    return json.load(urllib.request.urlopen(r,timeout=35)).get("result")
# un blocco di riferimento con la sua ora vera, poi si extrapola a 12s
b=rpc("eth_getBlockByNumber",["latest",False])
B0=int(b["number"],16); T0=int(b["timestamp"],16)
def quando(blocco): return T0-(B0-blocco)*12
ev=[]
for e in S["eventi"].values():
    p=PR.get(e["debito"].lower())
    if not p: continue
    x=e["dati"][2:]
    if len(x)<64*3: continue
    pr=int(x[0:64],16)/10**p["decimali"]*p["prezzo_usd"]*0.07
    if pr>=5: ev.append((quando(e["blocco"]), pr))
print(f"   {len(ev)} liquidazioni sopra EUR 5\n")
GIORNI=["lunedi","martedi","mercoledi","giovedi","venerdi","sabato","domenica"]
og=Counter(); oo=Counter(); pg=Counter()
for t,pr in ev:
    g=time.gmtime(t)
    og[g.tm_wday]+=1; oo[g.tm_hour]+=1; pg[g.tm_wday]+=pr
print("   PER GIORNO DELLA SETTIMANA (ora UTC):")
tot=sum(og.values())
for i in range(7):
    n=og.get(i,0)
    barra="#"*int(40*n/max(og.values())) if og else ""
    print(f"     {GIORNI[i]:<10} {n:>3} ({100*n/tot:>4.1f}%)  EUR {pg.get(i,0):>9,.0f}  {barra}".replace(",","."))
feriali=sum(og.get(i,0) for i in range(5)); weekend=sum(og.get(i,0) for i in (5,6))
print(f"\n     feriali {feriali} su 5 giorni = {feriali/5:.1f} al giorno")
print(f"     weekend {weekend} su 2 giorni = {weekend/2:.1f} al giorno")
print(f"     -> i feriali sono {feriali/5/max(0.01,weekend/2):.1f} volte il weekend")
print("\n   PER ORA DEL GIORNO (UTC; New York = UTC-5, quindi 14 UTC = 9 del mattino):")
for h in range(24):
    n=oo.get(h,0)
    barra="#"*int(30*n/max(1,max(oo.values())))
    ny=(h-5)%24
    et="  <- mattina a New York" if h in (13,14,15,16) else ""
    print(f"     {h:>2}:00 UTC ({ny:>2}:00 NY) {n:>3}  {barra}{et}")
fasce=[("00-06 UTC (notte NY)",range(0,6)),("06-13 (mattina Europa)",range(6,13)),
       ("13-21 (giornata USA)",range(13,21)),("21-24 (sera USA)",range(21,24))]
print()
for et,rr in fasce:
    n=sum(oo.get(h,0) for h in rr)
    ore=len(list(rr))
    print(f"     {et:<26} {n:>3} in {ore} ore = {n/ore:>4.1f} per ora")
