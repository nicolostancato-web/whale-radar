"""La METRICA: ogni posizione con la probabilita' VERA che cada.

Due modelli diversi, perche' due meccanismi diversi:

COPPIA UGUALE (garanzia e debito nella stessa valuta, es. weETH/WETH)
  Il mercato non le tocca. Cadono per:
    - deriva: crescita della garanzia MENO costo del debito, entrambi letti
      dal protocollo. Se la deriva e' positiva la salute MIGLIORA e non
      cadranno mai da sole.
    - sganciamento: la garanzia perde valore rispetto al suo riferimento.
      Raro ma reale (sUSDe l'ha gia' fatto in passato).

COPPIA DIVERSA (es. WBTC/dollaro)
  Cadono se il prezzo scende. Si usa la volatilita' storica vera per
  stimare la probabilita' che il calo necessario avvenga in 30 giorni.
"""
import json, math, time, urllib.request, sys, statistics as st
sys.path.insert(0,"agents")
from keccak import firma
U="https://ethereum-rpc.publicnode.com"
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
T=json.load(open("data/liquidazioni/tetti.json"))
NOMI={"0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":("wstETH","ETH"),
 "0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":("weETH","ETH"),
 "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":("WETH","ETH"),
 "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":("WBTC","BTC"),
 "0x514910771af9ca656af840dff83e8264ecf986ca":("LINK","LINK"),
 "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9":("AAVE","AAVE"),
 "0x9d39a5de30e57443bff2a8307a4256c8797a3497":("sUSDe","USD"),
 "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":("USDC","USD"),
 "0xdac17f958d2ee523a2206206994597c13d831ec7":("USDT","USD"),
 "0xc139190f447e929f090edeb554d95abb8b18ac1c":("USDtb","USD"),
 "0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f":("GHO","USD")}
# deriva annua netta misurata: crescita garanzia - costo debito
DERIVA={("weETH","WETH"):+0.70,("wstETH","WETH"):+0.80,
        ("sUSDe","USDC"):+0.70,("sUSDe","USDT"):-1.36,
        ("sUSDe","USDtb"):-0.50}
def rpc(m,p,giri=3):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=15))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.3)
    return None
def salute(a):
    v=rpc("eth_call",[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},"latest"])
    if isinstance(v,str) and len(v)>=2+64*6:
        x=v[2:]
        return int(x[320:384],16)/1e18, int(x[64:128],16)/1e8, int(x[0:64],16)/1e8
    return None,None,None
def volat(sym):
    """Volatilita' giornaliera vera, dai prezzi di Binance."""
    try:
        r=urllib.request.Request(
          f"https://api.binance.com/api/v3/klines?symbol={sym}USDT&interval=1d&limit=180",
          headers={"user-agent":"Mozilla/5.0"})
        k=json.load(urllib.request.urlopen(r,timeout=20))
        c=[float(x[4]) for x in k]
        r_=[math.log(c[i+1]/c[i]) for i in range(len(c)-1)]
        return st.stdev(r_)
    except Exception: return 0.03
VOL={}
for s in ("ETH","BTC","LINK","AAVE"):
    VOL[s]=volat(s); time.sleep(0.2)
# --- LA TAVOLA MISURATA, 31/10 (agents/difendono.py) ----------------------
# Il modello precedente calcolava la probabilita' che il prezzo scendesse del
# tanto che serve, trattando le posizioni come IMMOBILI. Dava EUR 311.878 di
# atteso in 30 giorni sulle nostre 99, mentre il mercato Aave INTERO paga
# EUR 407.000/mese lordi di cui vendibili 41.000: ci attribuiva 7,6 volte il
# mercato vendibile. Impossibile -> il modello era sbagliato, di ~9 volte.
#
# Il motivo: i debitori DIFENDONO. Nella banda 1,02-1,05, in 9 giorni, 10 sono
# cadute e 18 hanno MIGLIORATO la salute. Aggiungono garanzia, ripagano.
#
# Qui non c'e' piu' nessuna formula: c'e' il prima/dopo misurato su 300
# posizioni fra il blocco di 9 giorni fa e oggi, con l'intervallo al 95%.
# La finestra resta 9 GIORNI, quella misurata: non si extrapola a 30, perche'
# chi sopravvive cambia banda e il conto composto gonfierebbe di nuovo.
#
# BIAS dichiarato: il campione sono le posizioni a rischio OGGI. Chi e' caduto
# e stato liquidato al 50% ora ha salute ~1,5 e non e' nella lista -> le
# cadute si contano in DIFETTO. Il verso dell'errore e' noto.
# LA TAVOLA MISURATA, per TIPO DI COPPIA e per TAGLIA.
#
# Perche' la taglia: la prima versione della tavola, divisa solo per tipo di
# coppia, dava EUR 252.697 di atteso in 9 giorni contro EUR 122.114 pagati da
# TUTTO il mercato Aave nello stesso periodo. Due volte il mercato intero:
# impossibile. La causa e' che applicava la stessa percentuale a un premio da
# 130.000 e a uno da 200, mentre le posizioni GROSSE SONO DIFESE:
#   coppia diversa, caduta in 9 giorni, per debito:
#     0-10k      27,9% [16,7-42,7] su 43
#     10-100k     6,2% [ 2,5-15,0] su 64
#     100k-1M     2,8% [ 0,5-14,2] su 36
#     oltre 1M    0,0% [ 0,0-29,9] su 9
# Dieci volte meno, salendo di taglia. La percentuale senza la taglia e' una
# media fra popolazioni diverse -- lo stesso errore di
# feedback_righe_non_sono_casi, su un altro asse.
#
# Controprova che le due misure tornano: la mediana del premio delle 18 cadute
# osservate nel nostro laghetto e' $141; quella di TUTTE le 93 liquidazioni
# vere del mercato e' $134. Due contatori indipendenti della stessa quantita'.
BANDE_T=[(0,10_000),(10_000,100_000),(100_000,1_000_000),(1_000_000,10**15)]
TAVOLA = {   # (coppia_uguale, indice_taglia) -> (percentuale, basso, alto, n)
 (False,0): (27.9,16.7,42.7,43), (False,1): (6.2,2.5,15.0,64),
 (False,2): ( 2.8, 0.5,14.2,36), (False,3): (0.0,0.0,29.9, 9),
 (True, 0): ( 2.5, 0.4,12.9,40), (True, 1): (0.0,0.0, 7.7,46),
 (True, 2): ( 0.0, 0.0,11.4,30), (True, 3): (0.0,0.0,10.7,32),
}
def prob_misurata(uguale, salute, debito_usd):
    """La finestra e' 9 GIORNI, quella misurata. Non si extrapola a 30:
    chi sopravvive cambia banda e il conto composto gonfierebbe di nuovo."""
    for k,(a,b) in enumerate(BANDE_T):
        if a<=debito_usd<b:
            return TAVOLA[(uguale,k)]+((a,b),)
    return TAVOLA[(uguale,3)]+((BANDE_T[3]),)
comp=json.load(open("data/liquidazioni/composizione.json"))
# IL CRUSCOTTO DEVE MOSTRARE CIO' CHE IL SISTEMA PUO' DAVVERO COLPIRE.
# Filtrare sui TETTI invece che sugli AMMESSI mostrava 31 posizioni con
# garanzia USDC, che non e' armata: occasioni che non esistono per noi.
from pescatore import AMMESSI as _ARMATI
AM=set(T.keys()) & set(_ARMATI)
righe=[]
for u,c in comp.items():
    g=c["garanzia_principale"].lower(); d=c["debito_principale"].lower()
    if g not in AM: continue
    hf,deb,gar=salute(u)
    if hf is None: continue
    ng,fg=NOMI.get(g,("?","?")); nd,fd=NOMI.get(d,("?","?"))
    calo=(1-1/hf)*100 if hf>0 else 0
    quota=1.0 if hf<0.95 else 0.5
    dus=deb*quota
    tetto=T.get(g,100_000); tagliato=dus*1.07>tetto
    if tagliato: dus=tetto/1.07
    premio=dus*0.07
    uguale = (fg==fd)
    tipo = "coppia uguale" if uguale else "coppia diversa"
    pc, lo, hi, n_oss, banda = prob_misurata(uguale, hf, deb)
    p30 = pc/100           # NB: la finestra e' 9 giorni, non 30 (nome storico)
    dove=(f"debito ${banda[0]:,}-{banda[1]:,}" if banda[1]<10**15
          else f"debito oltre ${banda[0]:,}")
    if uguale:
        der=DERIVA.get((ng,nd))
        agg=(f"; deriva {der:+.2f}%/anno" if der is not None else "")
        nota=(f"misurato su {n_oss} posizioni {dove}: {pc:.1f}% "
              f"[{lo:.1f}-{hi:.1f}] in 9 giorni{agg}")
    else:
        nota=(f"misurato su {n_oss} posizioni {dove}: {pc:.1f}% "
              f"[{lo:.1f}-{hi:.1f}] in 9 giorni; {fg} si muove "
              f"{VOL.get(fg,0.03)*100:.1f}%/giorno")
    righe.append({"pos":u,"garanzia":ng,"debito":nd,"tipo":tipo,
      "salute":round(hf,4),"calo":round(calo,2),
      "debito_usd":round(deb),"chiude_usd":round(dus),
      "premio":round(premio),"tagliato":tagliato,
      "prob30":round(p30*100,1),"basso":lo,"alto":hi,"n_oss":n_oss,
      "nota":nota})
righe.sort(key=lambda x:-x["prob30"]*x["premio"])
json.dump({"quando":time.strftime("%Y-%m-%d %H:%M UTC",time.gmtime()),
  "volatilita":{k:round(v*100,2) for k,v in VOL.items()},
  "posizioni":righe}, open("data/liquidazioni/metrica.json","w"), indent=1)
print(f"   {len(righe)} posizioni | volatilita' giornaliera: "
      + ", ".join(f"{k} {v*100:.1f}%" for k,v in VOL.items()))
for r in righe:
    print(f"   {r['pos'][:12]} {r['garanzia']:<7}/{r['debito']:<6} "
          f"sal {r['salute']:.4f} calo {r['calo']:>6.2f}% "
          f"prem ${r['premio']:>8,} p9gg {r['prob30']:>5.1f}%  {r['tipo']}")

# LEZIONE 31/10 (misurata, non supposta) -----------------------------------
# Le cifre grosse di questa metrica sono di posizioni che NON cadono.
# Su 9 giorni veri (93 liquidazioni, agents/quanto_avrebbe_pagato.py):
#   premio mediano per liquidazione reale: EUR 134
#   le 3 piu' grosse (39.862 / 17.122 / 12.319) erano TUTTE su garanzie
#   che non sappiamo vendere -> il premio vendibile e' il 10% del totale.
# Quindi: il laghetto va allargato verso le COPPIE DIVERSE su garanzie
# nei tetti, non verso i premi alti. Il premio alto e' l'invendibile.
# Fonti che reggono eth_getLogs su 4.000 blocchi con archivio di giorni:
#   gateway.tenderly.co/public/mainnet e rpc.mevblocker.io
#   (drpc da 400, publicnode chiude a 403 dopo 2 giri, 1rpc max 50 blocchi)
