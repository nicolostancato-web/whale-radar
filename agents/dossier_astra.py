#!/usr/bin/env python3
"""
DOSSIER_ASTRA — prepara il fascicolo per il consulente esterno, e non e' un riassunto.

Il problema che risolve (06/09): gli davo sempre lo stesso file e le stesse quattro domande. Dopo
tre giri avrebbe ripetuto se stesso — non per debolezza, ma perche' un consulente che non sa cosa e'
successo dopo i suoi consigli puo' solo ridire le stesse cose con parole diverse.

Un consulente vero segue il progetto. Quindi ogni volta riceve:
  1. COSA HA DETTO L'ULTIMA VOLTA e cosa ne abbiamo fatto — cosi' vede l'effetto delle sue idee
     invece di riproporle, e puo' dirci se abbiamo capito male
  2. I NUMERI FRESCHI, non il riassunto di ieri: la percentuale vera, gli esperimenti, cosa e' morto
  3. UN ANGOLO DIVERSO ogni volta, a rotazione: la stessa domanda ripetuta produce la stessa risposta
  4. IL CIMITERO delle idee gia' bocciate, per non farsele riproporre

Scrive DOSSIER_ASTRA.md, che poi astra_review.sh gli passa al posto del solo STATO.md. €0.
"""
import json, os, time, glob

now = int(time.time())
# gli angoli ruotano: uno diverso a ogni consulenza, cosi' non si scava sempre nello stesso punto
ANGOLI = [
    ("L'ANGOLO DI OGGI — IL DATO CHE NON GUARDIAMO",
     "Fra i dati che abbiamo, ce n'e' uno che stiamo raccogliendo e non usiamo per decidere niente? "
     "Spesso il segnale sta in un campo che qualcuno ha salvato e nessuno ha mai interrogato."),
    ("L'ANGOLO DI OGGI — CHI STA DALL'ALTRA PARTE",
     "Per ogni nostro trade c'e' qualcuno che prende la parte opposta. Chi e', perche' lo fa, e "
     "perche' dovrebbe perdere contro di noi? Se non sappiamo rispondere, non abbiamo una strategia."),
    ("L'ANGOLO DI OGGI — COSA SUCCEDE PRIMA",
     "Guardiamo sempre cosa succede DOPO un evento. Cosa succede PRIMA che valga la pena osservare? "
     "Chi si muove per primo, e cosa lo si vede fare?"),
    ("L'ANGOLO DI OGGI — IL VINCOLO CHE CI SIAMO DATI",
     "Quale vincolo che ci siamo imposti da soli sta costando piu' di quanto protegge? "
     "Non i vincoli di realta': quelli che abbiamo scelto e che potremmo togliere."),
    ("L'ANGOLO DI OGGI — LA SCALA SBAGLIATA",
     "Stiamo guardando i token al minuto e all'ora. C'e' una scala temporale, o una dimensione di "
     "posizione, dove lo stesso fenomeno diventa sfruttabile e a cui non abbiamo mai guardato?"),
    ("L'ANGOLO DI OGGI — L'ESPERIMENTO DA UN GIORNO",
     "Se avessi 24 ore e la nostra macchina, quale singolo esperimento faresti che ci dice di piu' "
     "su dove sta il vantaggio? Uno solo, quello con il rapporto informazione/tempo migliore."),
]


def leggi(f, righe=None):
    try:
        t = open(f).read()
        return "\n".join(t.split("\n")[:righe]) if righe else t
    except Exception:
        return ""


def main():
    ang = ANGOLI[(now // 39600) % len(ANGOLI)]      # cambia a ogni consulenza (~11h)
    L = ["=" * 78, "FASCICOLO PER IL CONSULENTE ESTERNO",
         f"generato il {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime(now))}", "=" * 78, ""]

    prec = leggi("ASTRA_REVIEW.md")
    if prec:
        L += ["--- 1. COSA HAI DETTO L'ULTIMA VOLTA ---", "",
              "Rileggilo prima di rispondere. Non ripetere consigli gia' dati: dicci invece se cio' che",
              "abbiamo fatto corrisponde a cio' che intendevi, e cosa faresti di diverso adesso.", "",
              prec[-6000:], ""]

    L += ["--- 2. COSA ABBIAMO COSTRUITO DOPO IL TUO ULTIMO CONSIGLIO ---", "",
          leggi("DECISIONS.md", 60), ""]

    L += ["--- 3. I NUMERI DI ADESSO (non il riassunto di ieri) ---", ""]
    for f in ("PERCENTUALE.md", "SPERIMENTALE.md", "COSTO_MODELLO.md", "VERDETTO.md"):
        t = leggi(f, 45)
        if t: L += [f"### {f}", t, ""]

    L += ["--- 4. IL CIMITERO: idee gia' provate e MORTE, non riproporle ---", "",
          "- copy-trading (chi ha azzeccato 2 token): -46% lordo, peggio del caso",
          "- flusso di cluster indipendenti: era momentum, +307% PRIMA del segnale",
          "- reputazione del creator come cancello: 33 punti scesi a 8 al crescere dei dati",
          "- quattro segnali di domanda (accelerazione, ampiezza, squilibrio, facce nuove): "
          "media +70% ma mediana 0%, cioe' lotteria",
          "- il gemello sull'altra chain: -15% contro i controlli appaiati", "",
          "Se una tua idea assomiglia a una di queste, spiega cosa la rende diversa o passa oltre.", ""]

    L += ["--- 5. " + ang[0] + " ---", "", ang[1], "",
          "Questo angolo cambia a ogni consulenza: rispondi a QUESTO oltre alle domande fisse.",
          "La stessa domanda ripetuta produce la stessa risposta, e non e' per questo che ci sei.", ""]

    L += ["--- 6. LO STATO COMPLETO ---", "", leggi("STATO.md")]
    open("DOSSIER_ASTRA.md", "w").write("\n".join(L))
    testo = "\n".join(L)
    print(f"DOSSIER_ASTRA | angolo: {ang[0][19:]} | {len(testo)//1000}k caratteri", flush=True)


if __name__ == "__main__":
    main()
