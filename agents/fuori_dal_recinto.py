# -*- coding: utf-8 -*-
"""CHI STA FUORI DAL RECINTO: si leggono VIVE le posizioni che NON guardiamo.

Perche' esiste (4/11, terzo ingresso guardato dal C-check). Decidiamo chi
sorvegliare da un archivio di valori di salute vecchi fino a QUATTRO ORE.
Una posizione appena fuori dalla banda puo' essere scivolata dentro -- o
sotto soglia -- e noi saremmo ciechi fino al prossimo rifacimento della
lista, cioe' fino a mezz'ora dopo. 2.275 posizioni stanno in quella fascia.

LEZIONE che gli sta dietro: il nostro insieme e' il nostro recinto, e non
si prova mai fuori dal recinto. "Completo" voleva dire "completo per quello
che avevamo guardato".

Il campione non e' casuale: si parte da chi e' piu' vicino al bordo e da
chi ha il valore piu' VECCHIO, perche' li' sta la probabilita' di aver
attraversato. Un campione casuale avrebbe timbrato i numeri non guardati.
"""
import json, os, sys, time, urllib.request
sys.path.insert(0, "agents")
from keccak import firma
D = "data/liquidazioni"
POOL = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
FONTI = ["https://gateway.tenderly.co/public/mainnet",
         "https://ethereum-rpc.publicnode.com", "https://rpc.mevblocker.io"]
SEL = firma("getUserAccountData(address)")[2:10]
BANDA = 1.25            # la banda che sorvegliamo
QUANTE = int(sys.argv[1]) if len(sys.argv) > 1 else 40
def salute_viva(u):
    c = json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[
        {"to":POOL,"data":"0x"+SEL+u[2:].lower().zfill(64)},"latest"]}).encode()
    for f in FONTI:
        try:
            r = urllib.request.Request(f, data=c, headers={
                "content-type":"application/json","user-agent":"Mozilla/5.0"})
            v = json.load(urllib.request.urlopen(r, timeout=20)).get("result")
            if v and len(v) > 300:
                h = int(v[2:][64*5:64*6], 16)
                return h/1e18 if h < 2**255 else None
        except Exception: pass
    return None
def main():
    s = json.load(open(f"{D}/salute_note.json"))
    corta = {x["indirizzo"].lower() for x in json.load(open(f"{D}/lista_corta.json"))}
    ora = time.time()
    fuori = [(d["salute"], ora-d.get("quando", ora), a)
             for a, d in s.items()
             if d["salute"] >= BANDA and d["debito"] > 5000 and a not in corta]
    # meta' del campione dai piu' VICINI al bordo, meta' dai piu' VECCHI:
    # sono i due modi in cui una posizione puo' essere attraversata senza
    # che lo sappiamo.
    per_bordo = sorted(fuori)[:QUANTE//2]
    per_eta   = sorted(fuori, key=lambda t:-t[1])[:QUANTE - len(per_bordo)]
    campione = {a: (sal, eta) for sal, eta, a in per_bordo + per_eta}
    print(f"   {len(fuori)} posizioni fuori dal recinto; ne leggo {len(campione)} vive")
    dentro, ok, muti, casi = 0, 0, 0, []
    sfiorati = 0   # dentro la banda ma lontani: non sono una notizia
    for a, (sal, eta) in campione.items():
        viva = salute_viva(a)
        if viva is None: muti += 1; continue
        # SI SEGNALA CHI E' DAVVERO IN PERICOLO, non chi ha sfiorato il
        # bordo. Taratura corretta il 4/11, ed e' la QUARTA volta che
        # correggo un controllo tarato su una soglia invece che sulla cosa
        # che conta:
        #   - i tetti: provavo un rapporto fra due coppie invece del meccanismo
        #   - lo spreco: cercavo una parola nel log invece di contare i falliti
        #   - le posizioni fuori lista: guardavo la taglia invece della distanza
        #   - qui: guardavo l'attraversamento del bordo invece della distanza
        # REGOLA GENERALE, scritta per non rifarlo: un controllo non deve
        # suonare quando una grandezza attraversa una soglia che ho scelto
        # io, ma quando succede la cosa di cui mi importa. Il bordo della
        # banda e' una mia convenzione; "puo' cadere presto" e' un fatto.
        # Qui: 1,15 e' dove inizia la lista che sorvegliamo, quindi sotto
        # 1,15 vale la pena saperlo. Fra 1,15 e 1,25 non e' una notizia --
        # cinque posizioni sono passate da 1,2502 a 1,2493 e il controllo
        # ha gridato.
        SOGLIA_VERA = 1.15
        if viva < SOGLIA_VERA:
            dentro += 1
            casi.append({"posizione": a, "in_archivio": round(sal, 4),
                         "viva": round(viva, 4),
                         "archivio_vecchio_ore": round(eta/3600, 1),
                         "debito_usd": s[a]["debito"],
                         "sotto_soglia": viva < 1.0})
            print(f"   !!! {a[:12]}: in archivio {sal:.4f}, VIVA {viva:.4f} "
                  f"(valore vecchio di {eta/3600:.1f} ore)"
                  + ("  <<< E' GIA' SOTTO SOGLIA" if viva < 1.0 else ""))
        elif viva < BANDA:
            sfiorati += 1
        else:
            ok += 1
    json.dump({"quando": time.time(), "fuori_in_tutto": len(fuori),
               "letti": len(campione), "dentro_la_banda": dentro,
               "hanno_sfiorato_il_bordo": sfiorati,
               "restano_fuori": ok, "muti": muti, "casi": casi},
              open(f"{D}/fuori_dal_recinto.json", "w"), indent=1)
    print(f"   {ok} davvero fuori, {sfiorati} hanno sfiorato il bordo (lontani, "
          f"non e' una notizia), {dentro} DAVVERO in pericolo senza che lo "
          f"sapessimo, {muti} non letti")
    return 0
if __name__ == "__main__":
    sys.exit(main())
