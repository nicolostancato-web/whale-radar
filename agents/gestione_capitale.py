"""LA GESTIONE DEL CAPITALE: 100 euro, 10 per posizione, i profitti rientrano.

== L'IDEA (Nicolo', 9/10/2026) ==

«100 euro divisi in 10. Se apri 10 posizioni ti fermi e non vai avanti finche' non ne chiudi una.
E poi quando prendo i profitti io li rimetto dentro.»

E' una regola di gestione, non una strategia: non cambia se l'operazione sia buona, cambia **quante
operazioni puoi fare** e **quanto capitale resta bloccato**. Per questo va simulata con i TEMPI
veri, non con le medie: su questo mercato chi vince chiude in ~20 minuti e libera i soldi subito,
chi perde tiene i soldi bloccati fino all'orizzonte di 16,7 ore. Due posizioni col identico
rendimento ma durata diversa non valgono lo stesso.

== COSA MISURA, E COSA NON PUO' MISURARE ==

Misura: capitale impiegato nel tempo, profitto realizzato, occasioni **perse** perche' i soldi
erano tutti in gioco, e quanti giri completi fa il capitale.

Non misura: se la strategia guadagna. Quello dipende dal rendimento medio, che sul campione
casuale vero e' **fra -1,7% e -8,1% con l'intervallo che contiene lo zero**. Nessuna gestione del
capitale trasforma un'aspettativa negativa in positiva: moltiplicare per dieci un numero negativo
lo rende solo piu' negativo. La gestione serve a **sopravvivere** al caso, non a creare vantaggio.
"""
import json
import os
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

CHAIN = os.environ.get("CHAIN", "robinhood")
BASE = f"data/multichain/{CHAIN}"
CAPITALE = float(os.environ.get("CAPITALE", "100"))
PUNTATA = float(os.environ.get("PUNTATA", "10"))
ORIZZONTE_BLOCCHI = 600000      # 16,7 ore (NON 7 giorni: errore trovato il 9/10)


def simula(operazioni, capitale=CAPITALE, puntata=PUNTATA, racconta=True):
    """operazioni = [(blocco_entrata, blocco_uscita, rendimento)] in ordine di entrata."""
    cassa = capitale
    aperte = []            # (blocco_uscita, puntata, rendimento)
    persi = 0
    storia = []
    realizzato = 0.0
    giri = 0
    eventi = sorted(operazioni, key=lambda o: o[0])
    for b_in, b_out, r in eventi:
        # prima di aprire, incasso tutto cio' che si e' chiuso nel frattempo
        for a in [a for a in aperte if a[0] <= b_in]:
            cassa += a[1] * (1 + a[2])
            realizzato += a[1] * a[2]
            giri += 1
            aperte.remove(a)
        if cassa < puntata:
            persi += 1       # occasione persa: i soldi erano tutti in gioco
            continue
        cassa -= puntata
        aperte.append((b_out, puntata, r))
        storia.append((b_in, cassa, len(aperte)))
    # alla fine incasso quelle rimaste (nella realta' sono ancora aperte)
    bloccato = sum(a[1] for a in aperte)
    return {"cassa": round(cassa, 2), "bloccato_in_posizioni": round(bloccato, 2),
            "realizzato": round(realizzato, 2),
            "aperte_alla_fine": len(aperte), "chiusure": giri,
            "occasioni_perse": persi,
            "totale_se_le_aperte_valessero_zero": round(cassa, 2),
            "totale_se_le_aperte_tornassero_intere": round(cassa + bloccato, 2)}


def dalla_prova():
    d = json.load(open(f"{BASE}/prova_in_avanti.json"))
    ult = d["ultimo_blocco"]
    ops = []
    for tok, v in d["posizioni"].items():
        if v["stato"] == "chiusa":
            e = v["esito"]
            ops.append((v["primo_blocco"], e.get("blocco", ult), e.get("rendimento", 0.0)))
        elif v["stato"] == "aperta" and v.get("entrata"):
            # ancora aperta: la metto con uscita all'orizzonte e rendimento ignoto (0 per ora)
            ops.append((v["primo_blocco"], v["primo_blocco"] + ORIZZONTE_BLOCCHI, None))
    return ops, ult


def main():
    ops, ult = dalla_prova()
    chiuse = [(a, b, r) for a, b, r in ops if r is not None]
    aperte = [(a, b, r) for a, b, r in ops if r is None]
    print(f"CAPITALE | prova in avanti: {len(chiuse)} posizioni chiuse, {len(aperte)} aperte\n")
    print(f"con {CAPITALE:.0f} euro e {PUNTATA:.0f} euro per posizione:")
    impiegato = PUNTATA * len(ops)
    print(f"   impiegati finora      : {impiegato:.0f} euro su {len(ops)} posizioni")
    inc = sum(PUNTATA * (1 + r) for _, _, r in chiuse)
    pro = sum(PUNTATA * r for _, _, r in chiuse)
    print(f"   rientrati dalle chiuse: {inc:.2f} euro (profitto {pro:+.2f})")
    print(f"   ancora in gioco       : {PUNTATA*len(aperte):.0f} euro in {len(aperte)} posizioni")
    print(f"   cassa disponibile     : {CAPITALE - impiegato + inc:.2f} euro")
    print(f"\n   se le {len(aperte)} aperte andassero a ZERO: totale "
          f"{CAPITALE - impiegato + inc:.2f} euro ({100*((CAPITALE-impiegato+inc)/CAPITALE-1):+.1f}%)")
    print(f"   se tornassero intere              : totale "
          f"{CAPITALE - impiegato + inc + PUNTATA*len(aperte):.2f} euro "
          f"({100*((CAPITALE-impiegato+inc+PUNTATA*len(aperte))/CAPITALE-1):+.1f}%)")
    print(f"\n   (lo storico su campione pulito dice che circa 6 su 10 vanno quasi a zero:")
    print(f"    quindi il primo numero e' piu' vicino al vero del secondo)")

    # la stessa gestione sul campione STORICO, dove i rendimenti sono tutti noti
    p = f"{BASE}/tratti_campione_vero.jsonl"
    if os.path.exists(p):
        righe = [json.loads(l) for l in open(p) if l.strip()]
        righe.sort(key=lambda x: x["diploma"] if "diploma" in x else x["nato"])
        # durata: chi tocca il 2x chiude presto (stimo 30 minuti = 300 blocchi),
        # chi non lo tocca resta fino all'orizzonte. E' la differenza che conta.
        ops2 = []
        for i, x in enumerate(righe):
            b = x.get("diploma") or x["nato"]
            dur = 300 if x["tocca_2x"] else ORIZZONTE_BLOCCHI
            ops2.append((b, b + dur, x["rendimento"]))
        r2 = simula(ops2)
        print(f"\n--- la stessa gestione sulle {len(ops2)} posizioni dello STORICO pulito ---")
        print(f"   chiusure incassate     : {r2['chiusures'] if 'chiusures' in r2 else r2['chiusure']}")
        print(f"   occasioni PERSE perche' i soldi erano tutti in gioco: {r2['occasioni_perse']}")
        print(f"   profitto realizzato    : {r2['realizzato']:+.2f} euro su {CAPITALE:.0f}")
        print(f"   cassa finale           : {r2['cassa']:.2f} euro")
        print(f"   ancora bloccati        : {r2['bloccato_in_posizioni']:.2f} euro")
    return 0


if __name__ == "__main__":
    sys.exit(main())
