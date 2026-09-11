#!/usr/bin/env python3
"""
VERDETTO — LOOP 1 e' riuscito, va avanti, o va chiuso?

Nato dal punto piu' importante della consulenza esterna del 03/09:

    «Il rischio piu' grande e' continuare ad aggiungere segnali, parametri e test finche' prima
     o poi qualcosa appare positivo. Definiamo PRIMA dei prossimi risultati cosa deve succedere
     perche' LOOP 1 sia riuscito e cosa perche' venga chiuso.»

E' l'unico agente che puo' dire "abbiamo finito" o "abbiamo fallito". I criteri stanno in
data/criteri.json, scritti il 03/09 PRIMA di vedere altri numeri, e il codice li legge da li':
se un giorno ci venisse la tentazione di abbassare l'asticella, la modifica sarebbe visibile
nel registro delle decisioni invece che nascosta in un ragionamento.

Una configurazione si CONGELA prima di guardare l'holdout, e l'holdout si legge UNA volta sola.
Non e' pignoleria: guardare, aggiustare e riguardare trasforma la prova in un allenamento, e a
quel punto il numero che esce non dice piu' niente sul futuro.

Scrive VERDETTO.md. Sola lettura. €0.
"""
import json, os, time, math

CRITERI = "data/criteri.json"
now = int(time.time())


def carica():
    try: return json.load(open(CRITERI))
    except Exception: return None


def t_stat(media, dev, n):
    if not n or not dev: return 0.0
    return media / (dev / math.sqrt(n))


def main():
    c = carica()
    if not c:
        print("VERDETTO | criteri mancanti: non si giudica senza regole scritte prima", flush=True); return
    S = c["successo"]; C = c["chiusura"]
    scad = time.mktime(time.strptime(C["scadenza"], "%Y-%m-%d"))
    giorni = int((scad - now) / 86400)

    L = ["# ⚖️ VERDETTO — LOOP 1 è riuscito, va avanti, o va chiuso?",
         f"*{time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))} · criteri scritti il {c['scritto']}, "
         f"**prima** di vedere questi risultati*", "",
         "> Questi criteri esistono per un motivo solo: rendere **impossibile spostare il traguardo.**",
         "> Il rischio più grande non è sbagliare una strategia — è continuare ad aggiungere segnali",
         "> finché qualcosa appare verde per caso.", "",
         "## Cosa serve per dire «riuscito»", "",
         f"| condizione | soglia |", "|---|---|",
         f"| rendimento netto | **≥ {S['rendimento_netto_minimo']*100:.0f}%** |",
         f"| significatività (t) | **≥ {S['t_stat_minimo']}** |",
         f"| **prove indipendenti** | **{S['prove_indipendenti_minime']}** (gruppi, non righe) |",
         f"| righe minime | {S.get('righe_minime', 250)} |",
         f"| configurazione | congelata **prima** di guardare |",
         f"| holdout | mai visto, **{S['letture_holdout_consentite']} sola lettura** |",
         f"| costi | {S['costi']} |", "",
         "## Cosa succede se non ci arriviamo", "",
         f"Scadenza: **{C['scadenza']}** (fra {giorni} giorni) oppure **{C['oppure_trade_accumulati']} trade** "
         f"accumulati in validazione, quello che viene prima.", "",
         f"> {C['cosa_significa']}", "",
         "## Perché le prove si contano a gruppi", "",
         f"> {S['come_si_contano_le_prove']}", "",
         f"> {S['perche_25']}", "",
         "> Esempio misurato: 200 righe raggruppate in 8 giornate danno **t = +0,58**. Contando le righe",
         "> lo stesso dato darebbe **t = +2,88** — cioè la differenza fra «non abbiamo trovato niente» e",
         "> «abbiamo trovato qualcosa». Cinque volte più generoso, e sempre nella direzione che ci fa",
         "> comodo.", "",
         "## Divieti in vigore", ""]
    L += [f"- {d}" for d in c["divieti"]]

    cong = c.get("congelate") or {}
    L += ["", "## Configurazioni congelate", ""]
    if not cong:
        L += ["*Nessuna ancora. Una configurazione si congela quando la si ritiene pronta: da quel",
              "momento non si tocca più, e l'holdout la giudica una volta sola.*"]
    else:
        L += ["| chain | congelata il | holdout già letto |", "|---|---|---|"]
        for ch, v in cong.items():
            L.append(f"| {ch} | {v.get('quando','?')} | {'sì' if v.get('letto') else 'no'} |")
    L += ["", "## Stato oggi", "",
          "> ⏸️ **Nessuna pista ha ancora una configurazione congelata**, quindi non c'è niente da",
          "> giudicare. La fascia di validazione è troppo giovane: il verdetto arriverà quando avrà",
          f"> abbastanza trade, non quando ci farà comodo guardarla."]
    open("VERDETTO.md", "w").write("\n".join(L))
    print(f"VERDETTO | criteri del {c['scritto']} | scadenza {C['scadenza']} fra {giorni} giorni | "
          f"congelate: {len(cong)}", flush=True)


if __name__ == "__main__":
    main()
