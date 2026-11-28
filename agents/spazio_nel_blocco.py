# -*- coding: utf-8 -*-
"""LO SPAZIO NEL BLOCCO: arriviamo a chi costruisce i blocchi che contano?

PERCHE' ESISTE (4/11 sera). I cinque blocchi misuravano la macchina; il
tabellone misurava il mondo. Mancava il MERCATO in mezzo: lo spazio nel
blocco. Lo hanno indicato entrambi i revisori esterni, e la misura gli ha
dato ragione in modo brutale.

MISURATO sulle 42 liquidazioni sopra i $500 degli ultimi 30 giorni, chi ha
costruito quei blocchi:
    beaverbuild  29 blocchi  $654.891 di premio  75,5%
    BuilderNet   12 blocchi  $153.360            17,7%
    un terzo      1 blocco    $58.682             6,8%
Tre costruttori, e beaverbuild da solo tre quarti del mercato.

E noi mandavamo i pacchetti a UNA porta sola, quella di Flashbots. Quindi
su tre quarti del mercato non abbiamo mai avuto una possibilita' -- ed e'
quasi certamente il motivo per cui 12.000 pacchetti ACCETTATI hanno
prodotto ZERO inclusioni.
LA DISTINZIONE CHE CI MANCAVA: "accettato dal relay" non e' "arrivato a chi
costruisce quel blocco". Contavamo la prima e credevamo di contare la
seconda.

Provato: beaverbuild, BuilderNet e Titan accettano i nostri pacchetti
direttamente, e sono PIU' VELOCI del relay di Flashbots (171, 129 e 114 ms
contro 373). Ora si consegna a tutte in parallelo.

Cosa misura questo agente:
  - quali costruttori fanno i blocchi dove avvengono le liquidazioni che
    valgono, e la loro quota di premio
  - a quali di quelli consegniamo davvero
  - la QUOTA DI MERCATO COPERTA: la somma del premio dei costruttori che
    riceviamo. E' il numero che dice quanto del mercato possiamo vincere.
"""
import json, os, sys, time, collections
sys.path.insert(0, "agents")
from keccak import firma
import vendita_curve as VC
D = "data/liquidazioni"
FUORI = f"{D}/spazio_nel_blocco.json"
POOL = "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
EV = firma("LiquidationCall(address,address,address,uint256,uint256,address,bool)")
PASSO = 40000
GIORNI = int(os.environ.get("GIORNI", "30"))
MINIMO = float(os.environ.get("MINIMO", "500"))
# chi sta dietro a un indirizzo di coinbase, e se gli consegniamo
COSTRUTTORI = {
 "0x4838b106fce9647bdf1e7877bf73ce8b0bad5f97": ("beaverbuild", "beaverbuild"),
 "0x95222290dd7278aa3ddd389cc1e1d165cc4bafe5": ("beaverbuild", "beaverbuild"),
 "0xdadb0d80178819f2319190d340ce9a924f783711": ("BuilderNet", "buildernet"),
 "0xaab27b150451726ec7738aa1d0a94505c8729bd1": ("Titan", "titan"),
 "0x1f9090aae28b8a3dceadf281b0f12828e676c326": ("rsync-builder", None),
 "0xd87f3d6c5624e8d5e8f1d2a5cbbf0dd3f1ba9a48": ("non identificato", None),
}
def main():
    from invia_pacchetto import PORTE
    nostre = {n for n, _ in PORTE}
    PR = json.load(open(f"{D}/prezzi_oracolo.json"))
    testa = VC._rpc("eth_blockNumber", [])
    if not testa: print("   la catena non risponde"); return 1
    t = int(testa, 16)
    grosse = []
    for i in range(int(GIORNI*7200/PASSO)+1):
        log = VC._rpc("eth_getLogs", [{"address": POOL, "topics": [EV],
               "fromBlock": hex(t-(i+1)*PASSO), "toBlock": hex(t-i*PASSO)}]) or []
        for l in log:
            tp = l.get("topics") or []; d = l.get("data", "0x")[2:]
            if len(tp) < 4 or len(d) < 192: continue
            gar = ("0x"+tp[1][-40:]).lower(); deb = ("0x"+tp[2][-40:]).lower()
            pd, pg = PR.get(deb), PR.get(gar)
            if not pd or not pg: continue
            du = int(d[0:64],16)/10**pd["decimali"]*pd["prezzo_usd"]
            gu = int(d[64:128],16)/10**pg["decimali"]*pg["prezzo_usd"]
            if gu-du >= MINIMO: grosse.append((int(l["blockNumber"],16), gu-du))
    if len(grosse) < 5:
        print(f"   solo {len(grosse)} liquidazioni sopra ${MINIMO:,.0f}: non concludo")
        return 1
    quante = collections.Counter(); soldi = collections.Counter()
    for b, prem in grosse:
        bl = VC._rpc("eth_getBlockByNumber", [hex(b), False]) or {}
        m = (bl.get("miner") or "").lower()
        quante[m] += 1; soldi[m] += prem
    tot = sum(soldi.values())
    righe, coperto = [], 0.0
    for m, n in quante.most_common():
        nome, porta = COSTRUTTORI.get(m, ("ignoto "+m[:10], None))
        ok = bool(porta and porta in nostre)
        if ok: coperto += soldi[m]
        righe.append({"coinbase": m, "chi": nome, "porta": porta,
                      "gli_consegniamo": ok, "blocchi": n,
                      "premio": round(soldi[m], 2),
                      "quota": round(100*soldi[m]/tot, 1)})
    quota_coperta = round(100*coperto/tot, 1)
    print(f"   {len(grosse)} liquidazioni sopra ${MINIMO:,.0f} in {GIORNI} giorni, "
          f"${tot:,.0f} di premio")
    print(f"   {'chi costruisce':20s} {'blocchi':>8s} {'premio':>12s} {'quota':>7s}  gli consegniamo?")
    for r in righe:
        print(f"   {r['chi']:20s} {r['blocchi']:8d} {r['premio']:12,.0f} "
              f"{r['quota']:6.1f}%  {'SI' if r['gli_consegniamo'] else 'NO'}")
    print(f"\n   QUOTA DI MERCATO CHE POSSIAMO VINCERE: {quota_coperta}%")
    if quota_coperta < 90:
        manca = [r for r in righe if not r["gli_consegniamo"]]
        print(f"   ci manca: " + ", ".join(f"{r['chi']} ({r['quota']}%)" for r in manca))
    json.dump({"quando": time.time(), "giorni": GIORNI, "minimo": MINIMO,
               "liquidazioni": len(grosse), "premio_totale": round(tot, 2),
               "quota_coperta": quota_coperta, "porte_nostre": sorted(nostre),
               "costruttori": righe}, open(FUORI, "w"), indent=2)
    return 0
if __name__ == "__main__":
    sys.exit(main())
