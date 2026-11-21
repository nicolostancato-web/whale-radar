"""Prima si VERIFICA il wallet, poi si avvisa.

Correzione chiesta da Nicolo' il 31/10, ed e' giusta: l'email non deve dire
quello che mi aspettavo di incassare, deve dire quello che E' ARRIVATO.

Se la transazione riuscisse ma il premio fosse diverso dal previsto,
manderei una cifra sbagliata su una notifica che fa battere il cuore.

Quindi: si esegue -> si aspetta il blocco -> si legge il saldo della cassa
PRIMA e DOPO -> si manda la differenza vera. Se non e' arrivato nulla,
NON si manda nessuna email trionfale: si manda un avviso di anomalia.
"""
import json, subprocess, sys, time, urllib.request, os
sys.path.insert(0,"agents")
from avvisa import avvisa
FOUNDRY=os.path.expanduser("~/.foundry/bin")
CASSA="0x055e75aEaCF141c3118d039D5E099a821152eB66"
U="https://ethereum-rpc.publicnode.com"
GETTONI={"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48":("USDC",6,1.0),
         "0xdac17f958d2ee523a2206206994597c13d831ec7":("USDT",6,1.0),
         "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":("WETH",18,None)}
def rpc(m,p,giri=4):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=15))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.4*(g+1))
    return None
def saldo_cassa(gettone):
    dato="0x70a08231"+CASSA[2:].zfill(64)
    v=rpc("eth_call",[{"to":gettone,"data":dato},"latest"])
    return int(v,16) if isinstance(v,str) and len(v)>2 else 0
TOPIC_TRASFERIMENTO = ("0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef")
def arrivato_dai_log(ricevuta, gettone):
    """Quanto di `gettone` e' arrivato alla cassa in QUESTA transazione.
    Somma i Transfer il cui destinatario e' la cassa. Unita' grezze."""
    tot = 0
    for l in (ricevuta or {}).get("logs") or []:
        if (l.get("address") or "").lower() != gettone.lower(): continue
        t = l.get("topics") or []
        if len(t) < 3 or t[0].lower() != TOPIC_TRASFERIMENTO: continue
        if ("0x"+t[2][-40:]).lower() != CASSA.lower(): continue
        d = l.get("data") or "0x"
        if len(d) > 2: tot += int(d, 16)
    return tot
def dopo_la_liquidazione(gettone_debito, posizione, transazione,
                         premio_atteso_usd, debito_usd, garanzia=""):
    """Verifica il wallet e avvisa SOLO con quello che e' arrivato davvero."""
    g=gettone_debito.lower()
    nome, dec, prezzo = GETTONI.get(g, ("?", 18, None))
    if prezzo is None:
        p=rpc("eth_call",[{"to":"0x54586be62e3c3580375ae3723c145253060ca0c2",
            "data":"0xb3596f07"+g[2:].zfill(64)},"latest"])
        prezzo=int(p,16)/1e8 if p else 0
    # L'ACCREDITO SI LEGGE DALLA TRANSAZIONE, non da un saldo prima/dopo.
    #
    # DIFETTO TROVATO il 3/11 sera, e sarebbe costato l'unica cosa che conta.
    # Qui c'era `prima=saldo_cassa(g)` seguito dall'attesa del blocco e da
    # `dopo=saldo_cassa(g)`. Ma chi chiama questa funzione (controlla_esito
    # nella sentinella) la chiama SOLO DOPO aver visto la ricevuta, cioe'
    # quando i soldi sono GIA' in cassa: "prima" e "dopo" erano lo stesso
    # numero, l'accredito calcolato era zero, e il codice usciva stampando
    # "nessuna email inviata". Se avessimo vinto, Nicolo' non l'avrebbe
    # saputo: il premio in cassa in silenzio e una riga in un log che
    # nessuno legge. Esattamente il guasto che questo sistema esiste per
    # impedire -- e il terzo oggi della stessa famiglia (ultimo stadio rotto
    # con tutto il resto verde).
    #
    # Ora si somma il Transfer verso la cassa DENTRO quella transazione:
    # e' esatto, non dipende da nessun momento in cui si legge, e funziona
    # anche se la funzione viene chiamata un'ora dopo.
    for _ in range(20):
        r=rpc("eth_getTransactionReceipt",[transazione])
        if r and r.get("blockNumber"): break
        time.sleep(3)
    ric = r or {}
    grezzo = arrivato_dai_log(ric, g)
    arrivato = grezzo/10**dec
    arrivato_usd = arrivato*prezzo
    if arrivato <= 0:
        # SI AVVISA COMUNQUE. La regola di Nicolo' e' "prima verifichi, poi
        # mi avvisi", non "mi avvisi solo se sai fare la sottrazione": una
        # mail che dice "entrata, in cassa ci sono X" vale infinitamente
        # piu' del silenzio.
        saldo = saldo_cassa(g)/10**dec
        print(f"   nessun Transfer verso la cassa isolato in questa "
              f"transazione; la cassa ha {saldo:,.6f} {nome}")
        # incerto=True: la cifra e' il SALDO, non il premio. Senza questo
        # l'oggetto avrebbe detto "PREMIO INCASSATO" su un numero che non
        # e' il premio (3/11 sera).
        avvisa(incerto=True, premio_usd=saldo*prezzo, debito_usd=debito_usd,
               posizione=posizione, transazione=transazione,
               garanzia=garanzia or f"saldo cassa {saldo:,.4f} {nome}",
               prova=False)
        print(f"   email inviata col SALDO della cassa (accredito non isolabile)")
        return True
    scarto=abs(arrivato_usd-premio_atteso_usd)/max(premio_atteso_usd,1)*100
    print(f"   VERIFICATO sulla cassa: {arrivato:,.6f} {nome} = ${arrivato_usd:,.2f}")
    if scarto>5:
        print(f"   (atteso ${premio_atteso_usd:,.2f}, scarto {scarto:.1f}%)")
    avvisa(premio_usd=arrivato_usd, debito_usd=debito_usd,
           posizione=posizione, transazione=transazione,
           garanzia=garanzia or f"{arrivato:,.4f} {nome}", prova=False)
    print(f"   email inviata con la cifra VERA")
    return True
if __name__=="__main__":
    # prova del meccanismo: si legge il saldo vero della cassa adesso
    for g,(n,d,p) in GETTONI.items():
        s=saldo_cassa(g)
        if s: print(f"   cassa ha {s/10**d:,.6f} {n}")
    e=rpc("eth_getBalance",[CASSA,"latest"])
    print(f"   cassa ha {int(e,16)/1e18:.6f} ETH (i 20 centesimi di prova)")
    print(f"\n   meccanismo pronto: verifica PRIMA, avvisa DOPO")
