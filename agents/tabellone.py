# -*- coding: utf-8 -*-
"""IL TABELLONE: cosa e' successo nel mondo, e noi l'abbiamo preso?

PERCHE' ESISTE, e la ragione e' la piu' importante di tutto il progetto.
Il 4/11 il C-check era a 83 verifiche e CINQUE BLOCCHI AL 100%, e nello
stesso momento perdevamo una liquidazione da $24.048.189 con un premio vero
di $297.942. Il check non l'ha visto, e non poteva: tutte le sue 83
verifiche guardano DENTRO la macchina -- il pescatore gira, il relay
accetta, l'ordine e' fresco. Nessuna guardava FUORI.
L'ha trovata Nicolo', chiedendo "siamo sicuri che non ci sono possibilita'?"
invece di fidarsi dei cinque blocchi pieni.

LA LEZIONE, e vale oltre questo progetto: controllare che ogni pezzo
funzioni come progettato NON dice che stiamo vincendo. Un controllo di
meccanismo non trova mai un errore di disegno, e non trova mai una
partita persa. Serve un controllo di ESITO: leggere il mondo e confrontarlo
con noi.

COSA FA: legge dalla catena le liquidazioni VERE di Aave, e per ognuna
chiede: la conoscevamo? avevamo l'ordine pronto? era nella corsia veloce
del pescatore? abbiamo sparato? abbiamo vinto? e se no, PERCHE'.
Quando la risposta e' "no" con un motivo nuovo, quello e' un blocco che
non avevamo considerato.
"""
import json, os, sys, time
sys.path.insert(0, "agents")
from keccak import firma
import vendita_curve as VC          # per _rpc/_call, che sanno ripiegare
D = "data/liquidazioni"
FUORI = f"{D}/tabellone.json"
POOL = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
EV = firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
ORE = float(os.environ.get("ORE", "6"))
S_PREZZO = firma("getAssetPrice(address)")[2:10]
ORACOLO = "0x54586bE62E3c3580375aE3723C145253060Ca0C2"
_PREZZI_AL_BLOCCO = {}
def prezzo_al_blocco(gettone, blocco):
    """Il prezzo che l'oracolo dava A QUEL BLOCCO.

    DIFETTO TROVATO il 4/11 sera, e mi ha fatto dare a Nicolo' una cifra
    sbagliata tre volte: calcolavo il premio di una liquidazione PASSATA
    coi prezzi di ADESSO. Sulla sconfitta da 24 milioni il premio e'
    passato da $297.942 a $333.230 a $473.609 in poche ore, senza che
    succedesse niente -- era il rapporto fra USDT e WETH che si muoveva.
    Il valore vero, ai prezzi di quel blocco, e' $947.639: quasi un
    milione, e si verifica perche' e' il 4,05% del debito chiuso, coerente
    col 4,50% che Aave paga su garanzia USDT.
    LEZIONE: il valore di un fatto passato si misura coi prezzi di quando
    e' accaduto. Usare i prezzi di oggi su un fatto di ieri non e' una
    approssimazione: e' un numero diverso.
    """
    k = f"{gettone}|{blocco}"
    if k in _PREZZI_AL_BLOCCO: return _PREZZI_AL_BLOCCO[k]
    c = {"jsonrpc":"2.0","id":1,"method":"eth_call","params":[
         {"to":ORACOLO,"data":"0x"+S_PREZZO+gettone[2:].lower().zfill(64)},
         hex(blocco)]}
    import urllib.request
    v = None
    for f in VC.FONTI:
        try:
            r = urllib.request.Request(f, data=json.dumps(c).encode(),
                headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
            h = json.load(urllib.request.urlopen(r, timeout=25)).get("result")
            if h and len(h) > 2: v = int(h, 16)/1e8; break
        except Exception: pass
    _PREZZI_AL_BLOCCO[k] = v
    return v
def leggi_liquidazioni(ore):
    testa = VC._rpc("eth_blockNumber", [])
    if not testa: return [], None
    t = int(testa, 16)
    blocchi = int(ore*3600/12)
    log = VC._rpc("eth_getLogs", [{"address": POOL, "topics": [EV],
           "fromBlock": hex(t-blocchi), "toBlock": hex(t)}]) or []
    PR = json.load(open(f"{D}/prezzi_oracolo.json"))
    out = []
    for l in log:
        tp = l.get("topics") or []
        if len(tp) < 4: continue
        d = l.get("data", "0x")[2:]
        if len(d) < 192: continue
        gar = ("0x"+tp[1][-40:]).lower(); deb = ("0x"+tp[2][-40:]).lower()
        utente = ("0x"+tp[3][-40:]).lower()
        coperto = int(d[0:64], 16); presa = int(d[64:128], 16)
        liquidatore = ("0x"+d[128:192][-40:]).lower()
        pd, pg = PR.get(deb), PR.get(gar)
        blocco = int(l["blockNumber"], 16)
        # i prezzi DI QUEL BLOCCO, non di adesso
        pdb = prezzo_al_blocco(deb, blocco) or (pd or {}).get("prezzo_usd")
        pgb = prezzo_al_blocco(gar, blocco) or (pg or {}).get("prezzo_usd")
        deb_usd = (coperto/10**pd["decimali"]*pdb) if (pd and pdb) else 0
        gar_usd = (presa/10**pg["decimali"]*pgb) if (pg and pgb) else 0
        out.append({"blocco": int(l["blockNumber"], 16), "tx": l["transactionHash"],
                    "utente": utente, "garanzia": gar, "debito": deb,
                    "debito_chiuso_usd": round(deb_usd, 2),
                    "garanzia_presa_usd": round(gar_usd, 2),
                    "premio_vero_usd": round(gar_usd-deb_usd, 2),
                    "liquidatore": liquidatore})
    return out, t
MEMORIA = f"{D}/liquidazioni_viste.json"
def congela(righe):
    """IL PREMIO DI UN FATTO PASSATO NON DEVE MUOVERSI.

    Difetto trovato il 4/11 sera: calcolavo il premio di una liquidazione
    GIA' AVVENUTA con i prezzi di ADESSO. Risultato: la stessa singola
    sconfitta e' passata da $333.230 a $473.609 in mezz'ora senza che
    succedesse niente, e la penalita' sul blocco 4 e' salita da -6 a -9
    punti. Un numero che si muove da solo rende la colpa arbitraria.
    Qui si ricorda il premio alla PRIMA volta che vediamo quella
    transazione, e dopo non lo si ritocca piu'. (Stesso spirito di "una
    costante, un nome": un fatto misurato si scrive una volta.)
    """
    try: vista = json.load(open(MEMORIA))
    except Exception: vista = {}
    for r in righe:
        k = r["tx"]
        if k in vista:
            r["premio_vero_usd"] = vista[k]["premio_vero_usd"]
            r["debito_chiuso_usd"] = vista[k]["debito_chiuso_usd"]
            r["premio_congelato_il"] = vista[k]["quando"]
        else:
            vista[k] = {"premio_vero_usd": r["premio_vero_usd"],
                        "debito_chiuso_usd": r["debito_chiuso_usd"],
                        "quando": time.time()}
    # si tiene un mese di memoria, non di piu'
    taglio = time.time() - 31*86400
    vista = {k: v for k, v in vista.items() if v.get("quando", 0) > taglio}
    json.dump(vista, open(MEMORIA, "w"), indent=1)
    return righe
def eravamo_pronti(u):
    """Tutto quello che sapevamo di quella posizione, al momento del controllo."""
    def L(f):
        try: return json.load(open(f"{D}/{f}.json"))
        except Exception: return {}
    co = {k.lower() for k in L("composizione")}
    V = L("vendite_pronte")
    corta = {x["indirizzo"].lower(): x for x in (L("lista_corta") or [])}
    sn = L("salute_note")
    o = V.get(u) or V.get(u.lower()) or {}
    # la corsia veloce: la soglia dipende dal premio (cambiata il 4/11)
    prem = o.get("premio") or 0
    sog = 1.25 if prem >= 100_000 else (1.10 if prem >= 10_000 else
          (1.05 if prem >= 1_000 else 1.02))
    s = corta.get(u, {}).get("salute")
    return {"in_composizione": u in co,
            "ordine_pronto": bool(o.get("sede") or o.get("stesso")),
            "premio_che_stimavamo": prem,
            "salute_in_lista": s,
            "salute_in_archivio": (sn.get(u) or {}).get("salute"),
            "sarebbe_in_corsia_veloce": (s is not None and s < sog),
            "soglia_della_sua_corsia": sog}
def abbiamo_sparato(u, blocco):
    """Abbiamo composto pacchetti per questa posizione, e quando?"""
    n = 0; ultima = None
    try:
        for riga in open(f"{D}/sentinella.jsonl"):
            try: x = json.loads(riga)
            except Exception: continue
            for c in x.get("candidate", []):
                if (c.get("u") or "").lower()[:14] == u[:14]:
                    n += 1; ultima = x.get("quando")
    except Exception: pass
    return {"volte_fra_le_candidate": n, "ultima_volta": ultima}
# il nostro contratto viene da un solo posto: vedi agents/indirizzi.py
# (ATTENZIONE: il 5/11 una sostituzione automatica sulla parola nuda "COLPA"
# ha colpito la PRIMA occorrenza, che stava in questo commento, spezzando il
# file. Il tabellone -- il giudice -- e' rimasto morto 3,8 ore, e stavo
# attribuendo la sua eta' alla cadenza del ciclo invece che a un errore di
# sintassi. Il check lo diceva; sono io che ho letto male.
# Una sostituzione su una parola nuda va sempre ancorata: "COLPA = " e non
# "COLPA".)
from indirizzi import contratto as _dove
_NOSTRO=_dove().lower()

# OGNI MOTIVO DI SCONFITTA DA' LA COLPA A UN BLOCCO.
# Direttiva di Nicolo' (4/11): il tabellone non compete con gli altri
# cinque, DA' LA COLPA agli altri cinque. Prima quel collegamento stava
# nella mia testa -- il tabellone diceva "perso per corsia lenta" ed ero io
# a capire che era il blocco 4. Ora lo fa la macchina: chi apre la tabella
# vede DOVE siamo rotti, non solo che abbiamo perso.
COLPA = [
 ("non la conoscevamo",            4, "non l'avevamo nell'elenco: e' un difetto del vedere"),
 ("senza ordine pronto",           5, "la conoscevamo ma non sapevamo venderla"),
 ("corsia LENTA",                  4, "la guardavamo troppo di rado"),
 ("mai messa in un pacchetto",     2, "non l'abbiamo mandata al relay"),
 # "c'eravamo e non siamo stati scelti" era attribuito al blocco 2
 # (consegna). Dal 4/11 va al BLOCCO 6: la consegna funziona (il relay
 # accetta), quello che mancava era arrivare a CHI COSTRUISCE quel blocco.
 ("nella gara e l'abbiamo persa",  6, "c'eravamo e non siamo arrivati a chi costruiva"),
]
def da_la_colpa(righe):
    """Da ogni sconfitta, a quale blocco va la colpa e quanto pesa."""
    colpe = {}
    for r in righe:
        if r.get("nostra"): continue
        prem = r.get("premio_vero_usd", 0)
        if prem < 50: continue
        m = r.get("motivo") or ""
        for chiave, blocco, spiega in COLPA:
            if chiave in m:
                c = colpe.setdefault(blocco, {"premio_perso": 0.0, "quante": 0,
                                              "perche": spiega})
                c["premio_perso"] += prem; c["quante"] += 1
                break
        else:
            c = colpe.setdefault(0, {"premio_perso": 0.0, "quante": 0,
                                     "perche": "MOTIVO NUOVO: nessun blocco lo copre"})
            c["premio_perso"] += prem; c["quante"] += 1
    return colpe
def main():
    liq, testa = leggi_liquidazioni(ORE)
    NOSTRI = {"0x4355962379c779009f833d81bd8d2912773749a0",
              _NOSTRO,
              "0x055e75aeacf141c3118d039d5e099a821152eb66"}
    righe, perse, vinte = [], 0.0, 0.0
    for x in liq:
        nostra = x["liquidatore"] in NOSTRI
        info = eravamo_pronti(x["utente"])
        sparo = abbiamo_sparato(x["utente"], x["blocco"])
        # IL MOTIVO, che e' la cosa che serve
        if nostra: motivo = "L'ABBIAMO PRESA NOI"
        elif not info["in_composizione"]: motivo = "non la conoscevamo"
        elif not info["ordine_pronto"]:   motivo = "la conoscevamo ma senza ordine pronto"
        elif not info["sarebbe_in_corsia_veloce"]:
            motivo = (f"ordine pronto ma in corsia LENTA "
                      f"(salute {info['salute_in_lista']}, soglia {info['soglia_della_sua_corsia']})")
        elif sparo["volte_fra_le_candidate"] == 0:
            motivo = "pronta e in corsia veloce, ma non l'abbiamo mai messa in un pacchetto"
        else: motivo = "eravamo nella gara e l'abbiamo persa"
        if nostra: vinte += x["premio_vero_usd"]
        else: perse += x["premio_vero_usd"]
        righe.append({**x, **info, **sparo, "nostra": nostra, "motivo": motivo})
    righe = congela(righe)
    # i totali si rifanno DOPO il congelamento, altrimenti si sommano
    # numeri freschi a numeri congelati
    vinte = sum(r["premio_vero_usd"] for r in righe if r.get("nostra"))
    perse = sum(r["premio_vero_usd"] for r in righe if not r.get("nostra"))
    righe.sort(key=lambda r: -r["premio_vero_usd"])
    print(f"   TABELLONE — ultime {ORE:.0f} ore, {len(liq)} liquidazioni vere")
    print(f"   premio preso da noi: ${vinte:,.0f}   |   premio andato ad altri: ${perse:,.0f}")
    if righe:
        print(f"\n   {'premio vero':>13s}  {'debito chiuso':>14s}  motivo")
        for r in righe[:8]:
            print(f"   {r['premio_vero_usd']:>13,.0f}  {r['debito_chiuso_usd']:>14,.0f}  {r['motivo']}")
    # E POI SI STUDIA CHI HA VINTO: e' la seconda meta' dello stesso blocco.
    # Direttiva di Nicolo' (4/11): non "abbiamo vinto si o no", ma "chi ha
    # vinto e come" -- perche' da come ha fatto si capisce cosa ci manca, e
    # i blocchi nuovi escono da questo studio invece di essere inventati.
    colpe = da_la_colpa(righe)
    if colpe:
        print(f"\n   LA COLPA, blocco per blocco:")
        for b in sorted(colpe):
            c = colpe[b]
            nome = f"blocco {b}" if b else "NESSUN BLOCCO"
            print(f"     {nome}: ${c['premio_perso']:,.0f} persi in "
                  f"{c['quante']} liquidazioni — {c['perche']}")
    json.dump({"quando": time.time(), "ore": ORE, "quante": len(liq),
               "premio_nostro": round(vinte, 2), "premio_altrui": round(perse, 2),
               "colpe": {str(k): v for k, v in colpe.items()},
               "liquidazioni": righe}, open(FUORI, "w"), indent=1)
    try:
        import subprocess
        subprocess.run([".venv_bot2/bin/python", "agents/studia_il_vincitore.py"],
                       timeout=600)
    except Exception as e:
        print(f"   lo studio del vincitore non e' girato: {str(e)[:60]}")
    return 0
if __name__ == "__main__":
    sys.exit(main())
