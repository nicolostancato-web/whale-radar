# -*- coding: utf-8 -*-
"""QUANTO SENTIAMO, col denominatore in catena e SENZA aprire finestre.

PERCHE' ESISTE (5/11). Avevamo 3.137 aggiornamenti dell'oracolo nel registro
e sembravano molti: il denominatore diceva 8 su 96 nei 41 blocchi del
grappolo, cioe' l'8%. Gli 8 che hanno fatto cadere le posizioni non li
avevamo visti. Lo stadio da contare non e' "quanti ne vedo" ma "quale
frazione di quelli che esistono", e quel denominatore sta solo in catena.

SECONDA LEZIONE, pagata due volte nella stessa sera: la prima versione di
questo agente apriva finestre PROPRIE sulle stesse porte della sentinella, e
publicnode e drpc ci hanno messo in castigo per troppe richieste -- gli
aggiornamenti sentiti sono crollati da 26 in 6 minuti a 7 in 7. La misura ha
GUASTATO la cosa che misurava, e intanto il numero che produceva era falso.
Ora legge il registro che la sentinella scrive comunque: zero connessioni in
piu', e misura il sistema vero invece di una sua copia.
"""
import sys, json, os, time
sys.path.insert(0, "agents")
import vendita_curve as VC
INOLTRA = "0x6fadcf72"
REG = "data/liquidazioni/sentinella.jsonl"
FUORI = "data/liquidazioni/quanto_sentiamo.json"
BLOCCHI = int(os.environ.get("BLOCCHI", "60"))
def main():
    if not os.path.exists(REG):
        print("   nessun registro della sentinella"); return 1
    # NON SI CONTANO LE RIGHE DEL REGISTRO (riparato il 6/11, e il numero
    # falso che produceva mi ha fatto inseguire un problema inesistente per
    # due giri).
    #
    # La sentinella scrive una riga SOLO quando l'aggiornamento tocca un
    # nostro asset: gli altri li conta in `non_nostri` e non li registra.
    # Misurato: 288 aggiornamenti SENTITI, 76 registrati -> il registro ne
    # contiene il 26%. Contando le righe dicevo «copertura 15,8%» mentre
    # l'orecchio vero stava all'82%.
    # TERZA volta nella stessa notte che misuro lo stadio sbagliato (le altre
    # due: la porta di tenderly provata sul saluto invece che sul volume, e
    # il premio valutato ai prezzi di oggi invece che del blocco).
    # LA REGOLA: prima di usare un contatore, chiedersi di QUALE stadio e'.
    # Un registro filtrato non e' un registro di cio' che e' passato.
    vivo = {}
    try:
        vivo = json.load(open("data/liquidazioni/sentinella_viva.json"))
    except Exception:
        pass
    sentiti = {}
    for l in open(REG):
        try: r = json.loads(l)
        except ValueError: continue
        if r.get("tx_oracolo"): sentiti[r["tx_oracolo"].lower()] = r.get("quando")
    testa = VC._rpc("eth_blockNumber", [])
    if not testa: print("   la catena non risponde"); return 1
    t = int(testa, 16)
    # si parte da un po' indietro: la sentinella scrive la riga DOPO aver
    # composto, quindi gli ultimissimi blocchi possono mancarle per tempo.
    fine = t - 3
    tot = 0; presi = 0; mancati = []
    for b in range(fine - BLOCCHI, fine):
        bl = VC._rpc("eth_getBlockByNumber", [hex(b), True]) or {}
        for x in (bl.get("transactions") or []):
            if (x.get("input") or "0x").startswith(INOLTRA):
                tot += 1
                if (x.get("hash") or "").lower() in sentiti: presi += 1
                else: mancati.append(b)
    quota = round(100 * presi / tot, 1) if tot else None
    print(f"   blocchi guardati: {BLOCCHI} (fino al {fine})")
    print(f"   aggiornamenti in catena: {tot}")
    print(f"   di cui REGISTRATI (toccano un nostro asset): {presi} "
          f"= {100*presi/max(tot,1):.1f}%  <- NON e' la copertura")
    # LA COPERTURA VERA: quanti ne SENTE, dal contatore `becchi` della
    # sentinella, rapportato agli aggiornamenti in catena nello stesso tempo.
    _b = vivo.get("becchi") or 0
    _min = vivo.get("minuti") or 0
    if _b and _min and tot:
        # gli aggiornamenti in catena al minuto, dalla finestra appena letta
        al_minuto = tot / (BLOCCHI / 5.0)       # ~5 blocchi al minuto
        attesi = al_minuto * _min
        print(f"   SENTITI in {_min:.0f} min: {_b} su ~{attesi:.0f} attesi "
              f"=> COPERTURA ~{100*_b/max(attesi,1):.0f}%")
    else:
        print("   copertura vera: non calcolabile (manca il contatore becchi)")
    if tot < 25:
        print(f"   NON CONCLUDO: {tot} osservazioni sono troppo poche")
    # NIENTE SECONDA RIGA COL NUMERO DELLE RIGHE REGISTRATE: stampava
    # «COPERTURA: 4,8%» subito sotto «COPERTURA ~81%» e si contraddiceva da
    # sola. Due numeri che si chiamano allo stesso modo e misurano stadi
    # diversi sono peggio di nessun numero -- chi legge prende quello
    # sbagliato, e chi l'aveva scritto ero io.
    _b = vivo.get("becchi") or 0; _min = vivo.get("minuti") or 0
    _attesi = (tot / (BLOCCHI/5.0)) * _min if (_min and tot) else 0
    json.dump({"quando": time.time(), "blocchi": BLOCCHI, "in_catena": tot,
               "registrati_nostri_asset": presi,
               "quota_registrata": quota,
               "sentiti": _b, "attesi_nello_stesso_tempo": round(_attesi),
               "copertura_vera": (round(100*_b/_attesi, 1) if _attesi else None),
               "concludo": tot >= 25},
              open(FUORI, "w"), indent=2)
    return 0
if __name__ == "__main__":
    sys.exit(main())
