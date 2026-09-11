#!/usr/bin/env python3
"""
ACQUISTI_NON_CONTATI — quanti token avremmo comprato, e non compaiono nel rendimento?

Mossa 1 della consulenza esterna dell'08/09, e nasce da un numero del nostro stesso fascicolo:

    «Su Base ci sono 7 token giudicabili su 1.463 nati dopo il sigillo: lo 0,48%.
     State assumendo che diventare giudicabile sia indipendente dall'esito economico.»

E' l'assunzione piu' pericolosa che ci fosse rimasta, e non la vedevamo. Un token che muore subito
non arriva mai ad avere abbastanza candele per essere valutato: quindi esce dal conto. Non perche'
abbiamo deciso di escluderlo — perche' non ha fatto in tempo a entrarci.
Il risultato e' che il "rendimento della strategia" potrebbe essere il rendimento dei SOPRAVVISSUTI.

L'aritmetica che rende urgente la verifica: anche concedendo +8% a ciascuno di sette acquisti, un
ottavo acquisto sparito e perso interamente porta la media a -5,5%. Sette buoni e uno svanito, e
il segno si rovescia.

COSA FA QUI:
  1. ricostruisce chi era ACQUISTABILE al momento dell'ingresso, usando solo cio' che si sapeva
     allora (filtri di volume, eta', rapporto vendite) e col ritardo reale di osservazione
  2. guarda quanti di quelli sono poi finiti nel rendimento pubblicato
  3. e per i mancanti dice PERCHE': troppo poche candele, sparito, potato da noi

Distingue "mai acquistabile" da "acquistato e poi sparito": il primo non e' una perdita, il secondo
si'. Non conta ogni lapide come -100%: sarebbe l'errore opposto, e altrettanto sbagliato.

Scrive ACQUISTI_NON_CONTATI.md. Sola lettura, non tocca la validazione. €0.
"""
import json, os, glob, gzip, time, sys
sys.path.insert(0, "agents")
import multichain_brain as B

CHAIN = os.environ.get("CHAIN", "base")
ENTRY_H = 3                 # si entra 3 ore dopo il listing
MIN_VOL = 3000              # gli stessi filtri della strategia
MIN_CANDELE_ESITO = 12      # sotto questo il token non produce un rendimento valutabile
now = int(time.time())


def ritardo(chain):
    """Il ritardo di QUESTA chain, non il peggiore di tutte: applicare a Base il ritardo di Solana
    e' lo stesso errore del costo trasferito fra chain."""
    try:
        d = json.load(open("data/ritardo_reale.json")).get("ritardi") or {}
        x = d.get(chain) or {}
        return x.get("tipico_s") or 0
    except Exception:
        return 0


def main():
    R = ritardo(CHAIN)
    potati = set()
    try: potati = {k.lower() for k in json.load(open("data/potati.json"))}
    except Exception: pass

    files = glob.glob(f"data/multichain/{CHAIN}/candles/*.jsonl.gz")
    acquistabili = 0; con_esito = 0
    motivi = {"poche candele dopo l'ingresso": 0, "potato da noi": 0,
              "mai arrivato al volume minimo": 0, "sparito subito": 0}
    esiti_mancanti = []
    for f in files:
        pool = os.path.basename(f).replace(".jsonl.gz", "").lower()
        try:
            cs = []
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("cl"): cs.append((int(d["ts"]), float(d["cl"]), float(d.get("vol") or 0)))
        except Exception:
            continue
        if not cs: continue
        cs.sort()
        nasce = cs[0][0]
        # L'INGRESSO NON PUO' PRECEDERE I DATI (scoperto qui, 08/09).
        # La regola diceva "entra 3 ore dopo il listing", ma i dati ci arrivano con 3-7 ore di
        # ritardo: a +3h un bot vero non avrebbe in mano NIENTE, e infatti il primo censimento
        # trovava zero acquistabili su tutte e tre le chain. Non era un difetto del conteggio:
        # era la regola di ingresso che, applicata al mondo vero, non si puo' eseguire.
        # Qui si entra quando l'informazione esiste davvero: al piu' tardi fra la regola e il ritardo.
        ent = nasce + max(ENTRY_H * 3600, R + 3600)
        # cosa si sapeva all'ingresso, col ritardo con cui i dati ci arrivano davvero
        visto = [c for c in cs if c[0] <= ent - R]
        vol_noto = sum(c[2] for c in visto)
        if vol_noto < MIN_VOL:
            motivi["mai arrivato al volume minimo"] += 1
            continue
        acquistabili += 1
        dopo = [c for c in cs if c[0] >= ent]
        if len(dopo) >= MIN_CANDELE_ESITO:
            con_esito += 1
        else:
            if pool in potati: motivi["potato da noi"] += 1
            elif len(dopo) <= 2: motivi["sparito subito"] += 1
            else: motivi["poche candele dopo l'ingresso"] += 1
            if dopo and visto:
                p_ent = visto[-1][1]; p_fine = dopo[-1][1]
                if p_ent: esiti_mancanti.append(p_fine / p_ent - 1)

    persi = acquistabili - con_esito
    L = [f"# 🕳️ GLI ACQUISTI CHE IL RENDIMENTO NON CONTA ({CHAIN})",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · ritardo reale applicato: "
         f"{R//60} minuti · €0*", "",
         "> **La domanda**: un token che muore subito non arriva mai ad avere abbastanza candele per",
         "> essere valutato — quindi esce dal conto. Non perché lo escludiamo: perché non fa in tempo",
         "> a entrarci. Il «rendimento della strategia» rischia di essere il rendimento dei",
         "> **sopravvissuti**.", "",
         "> L'aritmetica che rende urgente saperlo: anche concedendo **+8% a ciascuno di sette",
         "> acquisti**, un ottavo sparito e perso interamente porta la media a **−5,5%**.", "",
         "| | token |", "|---|---|",
         f"| **acquistabili** all'ingresso (filtri passati con i dati di allora) | **{acquistabili}** |",
         f"| ...di cui **arrivati a un esito misurabile** | **{con_esito}** |",
         f"| ...**mancanti dal conto** | **{persi}** ({persi*100//max(acquistabili,1)}%) |", ""]
    if persi:
        L += ["**Perché mancano:**", ""] + [f"- {k}: {v}" for k, v in motivi.items() if v] + [""]
    if esiti_mancanti:
        import statistics as st
        m = st.mean(esiti_mancanti) * 100; med = st.median(esiti_mancanti) * 100
        L += ["## Cosa avrebbero reso, se li contassimo", "",
              f"Per {len(esiti_mancanti)} dei mancanti conosciamo comunque un prezzo di uscita:",
              f"rendimento medio **{m:+.0f}%**, mediano **{med:+.0f}%**.", "",
              "> Non sono un −100% automatico — sarebbe l'errore opposto, altrettanto sbagliato. Ma se",
              "> il loro rendimento è peggiore di quello dei token contati, allora il numero pubblicato",
              "> è **il rendimento dei sopravvissuti** e va corretto.", ""]
    L += ["## Verdetto", ""]
    quota = persi / max(acquistabili, 1)
    if quota < 0.1:
        L += [f"> ✅ Solo il **{quota*100:.0f}%** degli acquistabili esce dal conto: il rendimento",
              "> pubblicato non è distorto in modo apprezzabile da questa selezione."]
    else:
        L += [f"> ⚠️ **Il {quota*100:.0f}% degli acquisti che avremmo fatto non compare nel rendimento.**",
              "> Finché non sappiamo come sono andati, il numero pubblicato va letto come **rendimento",
              "> condizionato alla sopravvivenza**, non come rendimento della strategia."]
    open("ACQUISTI_NON_CONTATI.md", "w").write("\n".join(L))
    print(f"ACQUISTI_NON_CONTATI | {CHAIN} | acquistabili {acquistabili} | con esito {con_esito} | "
          f"mancanti {persi} ({quota*100:.0f}%)", flush=True)


if __name__ == "__main__":
    main()
