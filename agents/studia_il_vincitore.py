# -*- coding: utf-8 -*-
"""STUDIA CHI HA VINTO, e da come ha fatto capisci cosa ti manca.

PERCHE' ESISTE, e la direttiva e' di Nicolo' (4/11): il blocco 6 non deve
chiedersi "abbiamo vinto?" ma "CHI ha vinto e COME". Perche' finche' guardi
solo la tua macchina fai il tuo massimo e non sai cosa manca; appena guardi
la transazione di chi ha preso il premio, capisci dove hai sbagliato.
E i blocchi nuovi non si inventano: ESCONO da questo studio.

Cosa guarda, per ogni liquidazione che non e' nostra:
  - era una transazione PUBBLICA o un pacchetto privato?  (se vincono in
    pubblico a prezzo base, la nostra guerra dei pacchetti privati e' la
    guerra sbagliata)
  - quanto ha pagato di gas e quanta mancia al costruttore
  - in che posizione del blocco stava
  - ha usato un prestito lampo? di chi?
  - dove ha venduto la garanzia?
  - lo stesso indirizzo vince piu' volte? (e' un concorrente stabile o
    gente di passaggio?)

Ogni risposta e' una lezione su un blocco: se vince in pubblico, il blocco
2 (consegna) e' impostato male; se vince perche' guarda posizioni che noi
non guardiamo, e' il blocco 4; se vende dove noi non sappiamo vendere, e'
il blocco 5.
"""
import json, os, sys, time, collections
sys.path.insert(0, "agents")
import vendita_curve as VC
D = "data/liquidazioni"
FUORI = f"{D}/vincitori.json"
NOTI = {
 "0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2": "prestito lampo / pool Aave v3",
 "0x68b3465833fb72a70ecdf485e0e4c7bd8665fc45": "Uniswap v3 SwapRouter02",
 "0x000000000004444c5dc75cb358380d2e3de08a90": "Uniswap v4 PoolManager",
 "0x66a9893cc07d91d95644aedd05d03f95e1dba8af": "Uniswap v4 UniversalRouter",
 "0xdef171fe48cf0115b1d80b88dc8eab59176fee57": "Paraswap Augustus",
 "0x1111111254eeb25477b68fb85ed929f73a960582": "1inch",
 "0xba12222222228d8ba445958a75a0704d566bf2c8": "Balancer v2 (anche prestiti lampo)",
 "0xba1333333333a1ba1108e8412f11850a5c319ba9": "Balancer v3",
 "0x3fe6a2c4ae54e4a9f2c2b1a6f9cbbe6b5b4e9d1f": "?",
}
def studia(tx_hash, blocco):
    tx = VC._rpc("eth_getTransactionByHash", [tx_hash]) or {}
    ric = VC._rpc("eth_getTransactionReceipt", [tx_hash]) or {}
    bl = VC._rpc("eth_getBlockByNumber", [hex(blocco), False]) or {}
    base = int(bl.get("baseFeePerGas", "0x0"), 16)
    gas = int(ric.get("gasUsed", "0x0"), 16)
    eff = int(ric.get("effectiveGasPrice", "0x0"), 16)
    pos = int(ric.get("transactionIndex", "0x0"), 16)
    quante = len(bl.get("transactions") or [])
    PR = json.load(open(f"{D}/prezzi_oracolo.json"))
    peth = PR["0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"]["prezzo_usd"]
    # con chi ha parlato: i contratti che hanno emesso log nella sua tx
    toccati = collections.Counter()
    for l in (ric.get("logs") or []):
        toccati[(l.get("address") or "").lower()] += 1
    # PUBBLICA O PRIVATA? Un pacchetto privato di solito sta in cima al
    # blocco e paga una mancia; una transazione pubblica a prezzo base sta
    # dove capita. Non e' una prova, e' un indizio -- e si dichiara.
    mancia_gwei = (eff-base)/1e9
    indizio = ("sembra PUBBLICA a prezzo base (mancia zero)" if mancia_gwei < 0.01
               else ("sembra un pacchetto PRIVATO (in cima e con mancia)"
                     if pos <= 3 and mancia_gwei > 1 else "incerta"))
    return {"tx": tx_hash, "blocco": blocco,
            "da": (tx.get("from") or "").lower(),
            "a": (tx.get("to") or "").lower(),
            "gas_usato": gas,
            "base_gwei": round(base/1e9, 3),
            "pagato_gwei": round(eff/1e9, 3),
            "mancia_gwei": round(mancia_gwei, 3),
            "costo_usd": round(gas*eff/1e18*peth, 2),
            "mancia_usd": round(gas*(eff-base)/1e18*peth, 2),
            "posizione_nel_blocco": pos, "transazioni_nel_blocco": quante,
            "indizio_su_come": indizio,
            "contratti_toccati": [
               {"indirizzo": a, "chi_e": NOTI.get(a, "sconosciuto"), "log": n}
               for a, n in toccati.most_common(8)]}
def main():
    try: tb = json.load(open(f"{D}/tabellone.json"))
    except Exception:
        print("   nessun tabellone da studiare: lancia prima agents/tabellone.py"); return 1
    liq = [r for r in (tb.get("liquidazioni") or [])
           if not r.get("nostra") and r.get("premio_vero_usd", 0) >= 50]
    liq.sort(key=lambda r: -r["premio_vero_usd"])
    print(f"   STUDIO DI CHI HA VINTO — {len(liq)} liquidazioni non nostre "
          f"sopra i 50 dollari di premio\n")
    studi, chi_vince = [], collections.Counter()
    for r in liq[:6]:
        s = studia(r["tx"], r["blocco"])
        s["premio_vero_usd"] = r["premio_vero_usd"]
        s["perche_non_nostra"] = r.get("motivo")
        studi.append(s); chi_vince[s["da"]] += 1
        print(f"   premio ${r['premio_vero_usd']:,.0f}")
        print(f"     chi: {s['da']}")
        print(f"     ha chiamato: {s['a']}  ({NOTI.get(s['a'],'sconosciuto')})")
        print(f"     gas ${s['costo_usd']:,.2f}  mancia ${s['mancia_usd']:,.2f}  "
              f"posizione {s['posizione_nel_blocco']}/{s['transazioni_nel_blocco']}")
        print(f"     {s['indizio_su_come']}")
        noti = [c for c in s["contratti_toccati"] if c["chi_e"] != "sconosciuto"]
        if noti:
            print(f"     ha usato: " + ", ".join(c["chi_e"] for c in noti[:4]))
        print(f"     noi: {s['perche_non_nostra']}")
        print()
    ripetuti = [(a, n) for a, n in chi_vince.most_common() if n > 1]
    print(f"   chi vince piu' di una volta: "
          + (", ".join(f"{a[:12]} ({n} volte)" for a, n in ripetuti)
             if ripetuti else "nessuno: sono tutti di passaggio"))
    json.dump({"quando": time.time(), "studi": studi,
               "vincitori_ripetuti": ripetuti}, open(FUORI, "w"), indent=1)
    return 0
if __name__ == "__main__":
    sys.exit(main())

# ============================================================
# COSA CI HA INSEGNATO IL PRIMO STUDIO (4/11)
#
# Due liquidazioni, due vincitori DIVERSI (nessuno vince due volte), e
# entrambi:
#   - mancia al costruttore ZERO
#   - uno in posizione 2 su 321, l'altro in posizione 45 SU 466
#   - prestito lampo Aave, come noi
#   - transazioni che sembrano pubbliche a prezzo base
#
# POSIZIONE 45 SU 466 CON MANCIA ZERO e' il dato che conta: non e' un posto
# privilegiato, e' un posto qualsiasi. Quindi quelle liquidazioni NON SONO
# CONTESE: non c'e' asta, non c'e' gara di millisecondi. Vince chi se ne
# accorge.
#
# CONSEGUENZE SUI BLOCCHI, ed e' questo il mestiere di questo agente:
#
# Blocco 2 (consegna privata nello stesso blocco dell'oracolo): e'
#   SOVRADIMENSIONATO per questo mercato. Risolve una gara che non c'e'.
#   Non va buttato -- servira' il giorno che una liquidazione e' contesa --
#   ma non e' li' che si vince oggi, e non meritava di essere la cosa piu'
#   curata del sistema.
#
# Blocco 4 (vedere): e' LI' che stanno i soldi. Abbiamo perso per MINUTI,
#   non per millisecondi, perche' la posizione stava in una corsia
#   controllata ogni quattro minuti.
#
# La lezione generale: avevamo scelto l'avversario sbagliato. Credevamo di
# correre contro professionisti con nodi dedicati, e corriamo contro gente
# di passaggio che guarda meglio di noi.
# ============================================================

# ============================================================
# CORREZIONE DEL PRIMO STUDIO (4/11 sera) — avevo concluso il contrario
#
# Avevo scritto: "mancia zero e posizione 45 su 466, quindi queste
# liquidazioni non sono contese, vince chi se ne accorge, e il blocco 2 e'
# sovradimensionato". ERA SBAGLIATO, e l'errore nasceva dal guardare un
# numero solo: la mancia.
#
# Guardando la STRUTTURA del blocco vincente (26.342.152):
#   posizione 0: una transazione a 15,476 gwei
#   posizione 1: L'AGGIORNAMENTO DI PREZZO DI CHAINLINK (0x5c026b7107)
#   posizione 2: LA LIQUIDAZIONE VINCENTE, mancia zero
#   posizione 3: 210 ETH verso 0xfeeeeee440 (indirizzo di pagamento di un
#                costruttore)
# Cioe' il vincitore sta IMMEDIATAMENTE DOPO l'aggiornamento dell'oracolo,
# con priorita' zero. Quella e' esattamente la struttura che costruiamo
# noi: [transazione dell'oracolo, nostra liquidazione] nello stesso blocco.
# La mancia zero non vuol dire "non ha pagato": i pacchetti pagano in altri
# modi, e un posto in cima a un blocco con priorita' zero non si ottiene
# mandando una transazione pubblica.
#
# E la prova definitiva: la posizione era a salute 1,0054 dodici secondi
# prima e 1,0050 per i quattro minuti precedenti -- MAI sotto 1,0 in
# nessun blocco. E' caduta ED e' stata presa nello STESSO blocco.
#
# QUINDI: la gara c'e', la nostra impostazione e' giusta, e il blocco 2 non
# e' sovradimensionato. Abbiamo perso DENTRO la gara.
#
# PERCHE' ABBIAMO PERSO, misurato: su 37 volte che abbiamo intercettato
# quell'oracolo, la posizione da $130.841 era nei nostri 30 pacchetti solo
# 15 VOLTE -- nelle altre 22 veniva scartata in favore di posizioni piu'
# vicine alla soglia ma da 200 dollari. Quando c'era offrivamo 5,601 gwei
# contro lo zero del vincitore, quindi non abbiamo perso sull'offerta.
#
# LA LEZIONE SULLO STUDIO STESSO: un solo numero (la mancia) mi ha fatto
# concludere l'opposto della verita'. La struttura del blocco -- chi sta
# prima e chi sta dopo -- diceva tutto, e non l'avevo guardata.
# Chi studia il vincitore deve guardare il BLOCCO, non solo la transazione.
# ============================================================
