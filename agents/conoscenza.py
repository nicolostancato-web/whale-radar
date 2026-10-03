#!/usr/bin/env python3
"""
CONOSCENZA — la memoria del team: non cronaca ("cosa è successo"), ma sapere ("cosa abbiamo imparato").

Buco che chiude: il ricercatore riprovava gli stessi segnali a ogni giro senza ricordare che l'ultima volta
non funzionavano, e l'esploratore ripercorreva strade già battute. Un team che non ricorda non impara: ripete.

Qui ogni ruolo scrive gli esiti di ciò che prova, e prima di riprovare CHIEDE. Una cosa bocciata più volte
non si ripete... ma non viene condannata per sempre: quando i dati raddoppiano si ri-apre il caso, perché con
più dati la stessa idea può passare (è successo con l'insider).
Usato come libreria dagli altri ruoli + scrive CONOSCENZA.md. €0.
"""
import json, os, time

ARCHIVIO = "data/conoscenza.json"
BOCCIATURE = 3          # dopo 3 bocciature non si riprova...
RIAPRI_SE_DATI_X = 1.25 # ...finché i dati non crescono di un quarto...
RIAPRI_DOPO_ORE = 12    # ...oppure finché non passano 12 ore.
# Perche' due condizioni e non una: col solo criterio "i dati devono RADDOPPIARE" il ricercatore si e'
# trovato con 209 segnali su 209 archiviati e NIENTE da provare — puntuale e fermo (31/08). I dati crescono
# lentamente, il raddoppio sarebbe arrivato fra mesi. Il tempo e' l'altra porta: dopo mezza giornata il
# mercato non e' piu' lo stesso, e una cosa bocciata ieri merita un altro tentativo. rispetto all'ultima prova


def _carica():
    if os.path.exists(ARCHIVIO):
        try: return json.load(open(ARCHIVIO))
        except Exception: pass
    return {"voci": {}}


def _salva(d):
    os.makedirs("data", exist_ok=True)
    json.dump(d, open(ARCHIVIO, "w"))


def ricorda(chiave, tipo, chain, promosso, guadagno, n_dati):
    """registra l'esito di una prova (un segnale, una strategia, un rimedio)."""
    d = _carica()
    v = d["voci"].setdefault(chiave, {"tipo": tipo, "chain": chain, "prove": 0, "bocciature": 0,
                                      "promozioni": 0, "miglior_guadagno": -999, "n_dati_ultima": 0})
    v["prove"] += 1
    v["n_dati_ultima"] = n_dati
    v["ts"] = int(time.time())
    v["miglior_guadagno"] = max(v["miglior_guadagno"], round(guadagno, 1))
    if promosso: v["promozioni"] += 1; v["bocciature"] = 0
    else: v["bocciature"] += 1
    _salva(d)


def da_riprovare(chiave, n_dati_ora):
    """(sì/no, motivo). Si evita di rifare ciò che ha già fallito, ma si ri-apre il caso quando i dati crescono."""
    v = _carica()["voci"].get(chiave)
    if not v: return True, "mai provato"
    if v["bocciature"] < BOCCIATURE: return True, f"bocciato {v['bocciature']} volte, si riprova"
    if n_dati_ora >= v["n_dati_ultima"] * RIAPRI_SE_DATI_X:
        return True, f"caso riaperto: i dati sono passati da {v['n_dati_ultima']} a {n_dati_ora}"
    ore = (time.time() - v.get("ts", 0)) / 3600
    if ore >= RIAPRI_DOPO_ORE:
        return True, f"caso riaperto: sono passate {ore:.0f} ore dall'ultimo tentativo"
    return False, (f"già bocciato {v['bocciature']} volte {ore:.0f}h fa "
                   f"(si riprova fra {RIAPRI_DOPO_ORE - ore:.0f}h o quando i dati crescono)")


def report():
    d = _carica()["voci"]
    if not d:
        open("CONOSCENZA.md", "w").write("# 🧠 CONOSCENZA\n\n*Il team non ha ancora imparato nulla: primo giro.*\n")
        return 0
    vinc = [(k, v) for k, v in d.items() if v.get("promozioni", 0) > 0]
    chiusi = [(k, v) for k, v in d.items() if v.get("bocciature", 0) >= BOCCIATURE]
    aperti = [(k, v) for k, v in d.items() if v.get("promozioni", 0) == 0 and v.get("bocciature", 0) < BOCCIATURE]
    L = ["# 🧠 CONOSCENZA — cosa ha imparato il team",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())} · {len(d)} idee messe alla prova finora*", "",
         "> Questa non è la cronaca di cosa è successo: è il sapere accumulato. Prima di riprovare una cosa,",
         "> il team guarda qui. Ciò che ha fallito 3 volte si mette da parte — ma il caso si RIAPRE quando i",
         "> dati raddoppiano, perché con più dati la stessa idea può passare (è successo con l'insider).", ""]
    if vinc:
        L += ["## ✅ Cosa funziona", "", "| idea | chain | volte promossa | miglior guadagno |", "|---|---|---|---|"]
        L += [f"| `{k}` | {v['chain']} | {v['promozioni']} | {v['miglior_guadagno']:+.0f} punti |"
              for k, v in sorted(vinc, key=lambda x: -x[1]["miglior_guadagno"])]
        L += [""]
    if chiusi:
        L += ["## ❌ Cosa NON funziona (archiviato, non si riprova finché i dati non raddoppiano)", "",
              "| idea | chain | bocciature | miglior risultato mai visto |", "|---|---|---|---|"]
        L += [f"| `{k}` | {v['chain']} | {v['bocciature']} | {v['miglior_guadagno']:+.0f} punti |"
              for k, v in sorted(chiusi, key=lambda x: -x[1]["miglior_guadagno"])[:20]]
        L += [""]
    if aperti:
        L += ["## 🔎 Ancora in prova", "",
              ", ".join(f"`{k}`" for k, _ in aperti[:25]), ""]
    L += ["> Il tempo che il team NON spende a rifare cose già bocciate è tempo speso a cercare altrove."]
    open("CONOSCENZA.md", "w").write("\n".join(L))
    return len(d)


if __name__ == "__main__":
    n = report()
    print(f"CONOSCENZA | {n} idee in archivio", flush=True)
