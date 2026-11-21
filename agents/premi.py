# -*- coding: utf-8 -*-
"""IL PREMIO VERO CHE AAVE PAGA, gettone per gettone, letto dal protocollo.

PERCHE' ESISTE (4/11, settimo blocco). Davamo per buono un premio del **7%**
su ogni garanzia. Letto dal protocollo, il premio vero va dal **4,50%**
(USDC, USDT) all'**8,50%** (sUSDe, USDe, LBTC).

E non e' un dettaglio di stima: e' un difetto che fa PERDERE SOLDI senza
accorgersene. La nostra soglia sulla resa delle rotte (RESA_MINIMA = 94%)
era giustificata cosi': "sotto il 94% la vendita si mangia il premio del
7%". Il conto vero e' premio = (1+bonus) x resa - 1,0005:
  garanzia weETH (bonus 7,00%): a resa 94% resta +0,58%  -> si guadagna
  garanzia USDC  (bonus 4,50%): a resa 94% resta -1,80%  -> SI PERDE
Con la stessa soglia, sulle garanzie a basso bonus stavamo autorizzando
vendite in perdita.

E al contrario: FRAZIONE_PREMIO_PRETESA chiede un quarto del premio
ASSUNTO. Su un gettone che paga l'8,50% chiedevamo meno del dovuto; su uno
che paga il 4,50% chiedevamo troppo, e il contratto poteva rifiutare prese
buone.

Come l'ho trovato: non da un controllo, ma guardando il premio VERO della
liquidazione che abbiamo perso -- 1,24% su garanzia USDT contro il 7% che
stimavamo. Un numero inventato regge finche' nessuno lo confronta col mondo.
"""
import json, os, sys, time
sys.path.insert(0, "agents")
from keccak import firma
D = "data/liquidazioni"
FUORI = f"{D}/premi_veri.json"
PDP = "0x41393e5e337606dc3821075af65aee84d7688cbd"
S_CONF = firma("getReserveConfigurationData(address)")[2:10]
PEDAGGIO = 0.0005        # il pedaggio del prestito lampo, 0,05%
DIFETTO = 0.045          # se non si riesce a leggere: il PIU' BASSO visto,
                         # perche' sbagliare in difetto costa un'occasione,
                         # sbagliare in eccesso costa una perdita.
def _leggi_dal_protocollo(gettone):
    import vendita_curve as VC
    h = VC._call(PDP, "0x"+S_CONF+gettone[2:].lower().zfill(64))
    if not h or len(h) < 200: return None
    x = h[2:]
    bonus = int(x[64*3:64*4], 16)      # punti base, 10000 = nessun bonus
    if bonus <= 10000: return None
    return (bonus-10000)/10000.0
_CACHE = {"quando": 0, "premi": {}, "vecchi": False}


def carica(eta=21600):
    """I premi veri. VECCHI VA BENE, INVENTATI NO (riparato il 4/11 sera).

    DIFETTO PAGATO: la finestra di freschezza era di 6 ore e nel giro del
    laghetto non c'era nessun passo che aggiornasse il file. Appena il file
    compiva 6,3 ore questa funzione lo SCARTAVA e tutti i gettoni
    ripiegavano sul difetto del 4,50%: su USDe, che paga l'8,50%, la soglia
    di resa diventava troppo severa e rifiutavamo rotte che guadagnavano.
    Buttare un dato VERO di sei ore per usare una COSTANTE SBAGLIATA e' il
    peggiore dei due scambi -- e il premio di liquidazione cambia solo per
    votazione della governance, non di ora in ora.
    Ordine giusto: fresco > vecchio ma vero > difetto. E se si usa il
    vecchio, lo si DICE (il campo "vecchi"), perche' un ripiego silenzioso
    su una cosa che conta e' una bugia.
    """
    if time.time()-_CACHE["quando"] < eta and _CACHE["premi"]:
        return _CACHE["premi"]
    sul_disco = {}
    eta_disco = None
    try:
        d = json.load(open(FUORI))
        sul_disco = d.get("premi") or {}
        eta_disco = time.time()-d.get("quando", 0)
        if eta_disco < eta:
            _CACHE.update({"quando": d["quando"], "premi": sul_disco,
                           "vecchi": False})
            return _CACHE["premi"]
    except Exception:
        pass
    # scaduto: si PROVA a rileggerlo dal protocollo
    try:
        aggiorna()
        d = json.load(open(FUORI))
        _CACHE.update({"quando": d["quando"], "premi": d.get("premi") or {},
                       "vecchi": False})
        return _CACHE["premi"]
    except Exception:
        pass
    if sul_disco:
        _CACHE.update({"quando": time.time(), "premi": sul_disco,
                       "vecchi": True})
        print(f"   premi VECCHI di {(eta_disco or 0)/3600:.1f} ore: li uso "
              f"comunque, sono veri (il difetto no)")
        return sul_disco
    return _CACHE["premi"]
def premio(gettone):
    """Quanto paga davvero Aave per liquidare QUESTA garanzia."""
    p = carica()
    v = p.get((gettone or "").lower())
    return v if v else DIFETTO
def resa_minima(gettone, margine=0.02):
    """La resa sotto la quale la vendita di QUESTA garanzia va in perdita,
    piu' un margine di sicurezza. Prima era 0,94 fisso per tutti, e su una
    garanzia che paga il 4,50% autorizzava vendite in perdita."""
    b = premio(gettone)
    pareggio = (1.0+PEDAGGIO)/(1.0+b)      # resa a cui il guadagno e' zero
    return min(0.999, pareggio+margine)
def aggiorna():
    import vendita_curve as VC
    from pescatore import AMMESSI
    out = {}
    for a in sorted(AMMESSI):
        v = _leggi_dal_protocollo(a)
        if v: out[a.lower()] = round(v, 4)
    if len(out) < 5:
        print(f"   solo {len(out)} premi letti: NON sovrascrivo"); return 1
    json.dump({"quando": time.time(), "premi": out}, open(FUORI, "w"), indent=1)
    _CACHE.update({"quando": time.time(), "premi": out})
    U = {x["gettone"]: x["simbolo"]
         for x in json.load(open(f"{D}/unita_gettoni.json"))}
    print(f"   {len(out)} premi veri letti dal protocollo")
    print(f"   {'gettone':10s} {'premio vero':>12s} {'resa minima':>12s}")
    for a, v in sorted(out.items(), key=lambda t: -t[1]):
        print(f"   {U.get(a,a[:8]):10s} {100*v:11.2f}% {100*resa_minima(a):11.2f}%")
    return 0
if __name__ == "__main__":
    sys.exit(aggiorna())
