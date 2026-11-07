# -*- coding: utf-8 -*-
"""PRONTI AL CROLLO: quante posizioni cadono a ogni profondita' di dump, e
quante di quelle hanno un ordine di vendita pronto e FRESCO.

Nato il 3/11, su domanda di Nicolo' per la notte delle elezioni americane:
"assicurati che anche con un dump forte, 5-6-9%, noi siamo pronti".

IL MODELLO DEL CROLLO, che e' il punto. La salute e' garanzia*soglia/debito:
si muove solo se garanzia e debito stanno in famiglie DIVERSE. In un dump
ETH e tutti i suoi derivati scendono insieme, le stabili restano. Quindi:
  garanzia ETH / debito stabile  -> la salute scende, CADE
Le famiglie che scendono sono ETH, BTC e VOL (LINK, AAVE: non sono
derivati di ETH ma in un dump scendono anche loro, e trattarle come
stabili diceva che quelle posizioni non cadono mai -- l'errore nella
direzione pericolosa).
  garanzia ETH / debito ETH      -> la salute non si muove, NON cade
  garanzia stabile / debito ETH  -> la salute SALE, diventa piu' sicura
Il 3/11 ho sbagliato questo conto una prima volta contando tutte le
posizioni sotto una soglia di salute, senza guardare le famiglie: dava 672
posizioni in caduta a un dump del 9% invece di 76. Quasi tutte le posizioni
a un soffio dalla soglia sono coppie UGUALI, e quelle non cadono mai per
un movimento di ETH.

"Ordine fresco" vuol dire costruito col margine SCIVOLAMENTO_BP attuale.
Un ordine col margine vecchio (1%) si annulla sul primo movimento di
prezzo, quindi conta come scoperto anche se c'e'.
"""
import json, re, sys, time, statistics
sys.path.insert(0, "agents")
from pescatore import SCIVOLAMENTO_BP, ORDINE_VALE
D = "data/liquidazioni"
def L(f, d=None):
    try: return json.load(open(f"{D}/{f}.json"))
    except Exception: return d if d is not None else {}
src = open("agents/prepara_vendite.py").read()
from famiglie import famiglia as _fam_di, SCENDONO
fam = _fam_di
s  = L("salute_note"); v = L("vendite_pronte")
try: SENZA = set((L("tetti_coppia") or {}).get("senza_strada") or {})
except Exception: SENZA = set()
co = {k.lower(): x for k, x in L("composizione").items()}
adesso = time.time()
PROFONDITA = (3, 5, 6, 9, 12, 15, 20)
righe = []
for calo in PROFONDITA:
    k = 1 - calo / 100.0
    cadono = []
    for a, d in s.items():
        if d.get("debito", 0) < 2000: continue
        c = co.get(a)
        if not c: continue
        kg = k if fam(c["garanzia_principale"]) in ("ETH", "BTC", "VOL") else 1.0
        kd = k if fam(c["debito_principale"])   in ("ETH", "BTC", "VOL") else 1.0
        if d["salute"] * kg / kd < 1.0: cadono.append((a, d))
    con = [a for a, d in cadono
           if (v.get(a) or {}).get("sede") or (v.get(a) or {}).get("stesso")]
    # "Fresco" = costruito col margine attuale, OPPURE senza nessuno scambio.
    # Il 3/11 questo conto sottostimava: quando garanzia e debito sono lo
    # stesso gettone il piano ha zero passi, quindi non c'e' nessun margine
    # che si possa annullare -- quelle posizioni sono pronte per sempre.
    # Contarle come scoperte faceva sembrare fragile cio' che non lo e'.
    # SI CONTA QUELLO CHE IL PESCATORE ACCETTEREBBE, non quello che e'
    # stato costruito bene. DIFETTO TROVATO il 4/11 notte, e questo
    # indicatore stava mentendo a me e a Nicolo' da tutta la notte:
    # contava "margine giusto", che non scade mai, mentre tenta() rifiuta
    # un ordine piu' vecchio di ORDINE_VALE e ripiega sul preventivo dal
    # vivo -- che e' rifiutato dalla fonte il 36% delle volte.
    # Misurato al momento della scoperta: 887 contate come coperte, di cui
    # 205 che il pescatore avrebbe rifiutato per anzianita'. Zero ordini
    # piu' freschi di due ore.
    # Un ordine senza scambio non scade: non c'e' niente da rifare.
    freschi = [a for a in con
               if v[a].get("stesso")
               or (v[a].get("margine_bp") == SCIVOLAMENTO_BP
                   and (adesso - v[a].get("quando", 0)) < ORDINE_VALE)]
    # SI SEPARA "LIMITE NOTO" DA "DA RIFARE". Difetto di misura trovato il
    # 4/11 sera, il quinto della stessa famiglia: contavo come "scoperte"
    # anche le coppie che la taratura ha dichiarato SENZA STRADA e che il
    # giro salta di proposito. Quelle non sono un lavoro arretrato, sono un
    # confine -- e mescolarle con gli ordini da rifare rende il numero
    # inutile: non si capisce se c'e' qualcosa da fare o no.
    mancanti = [a for a, _ in cadono if a not in freschi]
    senza_strada = [a for a in mancanti
                    if f"{(co.get(a) or {}).get('garanzia_principale','').lower()}"
                       f"|{(co.get(a) or {}).get('debito_principale','').lower()}" in SENZA]
    da_rifare = [a for a in mancanti if a not in senza_strada]
    pr = [d["debito"] * 0.5 * 0.07 for a, d in cadono]
    righe.append({"calo_percento": calo, "cadono": len(cadono),
                  "con_ordine": len(con), "ordine_fresco": len(freschi),
                  "scoperte": len(da_rifare),
                  "senza_strada_noto": len(senza_strada),
                  "premio_mediano": round(statistics.median(pr), 0) if pr else 0,
                  "premio_totale": round(sum(pr), 0)})
fuori = {"quando": time.time(), "margine_attuale_bp": SCIVOLAMENTO_BP,
         "righe": righe}
json.dump(fuori, open(f"{D}/pronti_al_crollo.json", "w"), indent=1)
print(f"   PRONTI AL CROLLO (margine {SCIVOLAMENTO_BP} bp)")
print(f"   {'dump ETH':9s} {'cadono':>7s} {'pronte':>7s} {'scoperte':>9s} "
      f"{'premio in gioco':>16s}")
for r in righe:
    allarme = "  <-- DA RIFARE" if r["scoperte"] > 0 else ""
    print(f"   {r['calo_percento']:6d}%  {r['cadono']:7d} {r['ordine_fresco']:7d} "
          f"{r['scoperte']:9d} {r['premio_totale']:16,.0f}"
          f"{'  (+'+str(r['senza_strada_noto'])+' senza strada)' if r.get('senza_strada_noto') else ''}{allarme}")
