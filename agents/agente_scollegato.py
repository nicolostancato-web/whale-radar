"""GLI AGENTI SCRITTI E MAI COLLEGATI A UNA CORSIA.

== PERCHE' ESISTE ==

Il 6/10/2026 ho scritto `storie_complete.py`, ne ho ricavato la misura piu' importante della
giornata, e NON l'ho collegato a nessuna corsia: sarebbe vissuto solo nel mio schermo e sarebbe
morto con la sessione. **E' la quinta volta in due giorni che scrivo un pezzo e non lo collego.**

Cinque volte significa che la regola («collega sempre») non funziona, perche' dipende dalla mia
attenzione nel momento in cui sono concentrato su altro. Allora serve un MECCANISMO che guardi al
posto mio — lo stesso motivo per cui esistono `corsia_non_vista.py` e `disco_e_copia.py`.

== PERCHE' UNA FOTOGRAFIA E NON UNA DATA ==

Alla prima prova ne ha segnalati 33, quasi tutti analisi di mesi fa gia' concluse: **una guardia
che grida al lupo 33 volte viene ignorata, ed e' peggio di non averla.**

Ho provato a filtrare per eta' e NON SI PUO': la copia di lavoro e' superficiale (un solo
commit), quindi ne' il disco ne' git conoscono la data vera di un file. Il disco dice la data del
clone, git dice la data dell'unico commit. **Due fonti, due bugie, la stessa bugia.**

Allora: si fotografa una volta l'insieme di quelli gia' scollegati (`data/scollegati_noti.json`,
con la data della fotografia) e si segnalano **solo i nuovi**. Se un vecchio viene collegato, esce
dalla fotografia da solo. E' il modo standard di far nascere un controllo su un sistema che ha gia'
del debito: non si pretende di ripulire il passato per poter sorvegliare il presente.

== COSA NON SEGNALA ==

Alla prima prova ne ha segnalati 33, e quasi tutti erano analisi di mesi fa che hanno gia'
prodotto il loro verdetto: finite, non dimenticate. **Una guardia che grida al lupo 33 volte viene
ignorata, ed e' peggio di non averla.** Quindi guarda solo gli agenti toccati negli ultimi
GIORNI giorni: quelli sono i miei, di adesso, e sono gli unici su cui posso ancora fare qualcosa.

== COSA NON SEGNALA ==

Gli agenti che per loro natura non girano in cielo, elencati qui sotto con il motivo. L'elenco e'
esplicito perche' un'eccezione non dichiarata diventa un buco: fra sei mesi nessuno ricorda
perche' un file era escluso.
"""
import json
import os
import re
import subprocess
import sys
import time

QUI = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GIORNI = float(os.environ.get('GIORNI_SCOLLEGATO', '2'))

# agente -> perche' NON deve stare in una corsia
A_MANO = {
    "consulta_grok": "il programma grok e' autenticato sul Mac di Nicolo: in cielo userebbe la "
                     "chiave a consumo, che e' l'errore da 77 euro di maggio",
    "ricerca_prelancio": "stessa ragione: passa da consulta_grok",
    "pubblica_file": "e' lo strumento con cui si pubblica, non un lavoro",
    "firma_evento": "libreria, non un agente",
    "a_fette": "libreria, non un agente",
    "verso": "libreria, non un agente",
    "curva_pons": "libreria usata da altri agenti, piu' le sue due corsie",
    "agente_scollegato": "sono io",
    "disco_e_copia": "gira da pubblica.sh, non da una corsia",
    "prova_a_secco": "gira da pubblica.sh",
    "corsia_non_vista": "gira da pubblica.sh",
    "corsia_vuota": "gira da pubblica.sh",
    "budget_e_tetto": "gira da pubblica.sh",
    "dal_di_fuori": "e' lo script che vive FUORI da GitHub, per disegno",
}


def _nato(p):
    """Quando il file e' stato scritto DAVVERO, chiesto a git e non al disco.

    La data del disco in una copia appena clonata e' la data del clone: il 6/10 questa guardia
    ha segnalato 33 agenti «scritti oggi» perche' la copia era stata rifatta quella mattina.
    **Una data presa dal filesystem di un clone fresco e' una bugia**, e una guardia che si basa
    su una bugia e' rumore.
    """
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%ct", "--", p],
                           cwd=QUI, capture_output=True, text=True, timeout=20)
        t = (r.stdout or "").strip()
        if t.isdigit():
            return int(t)
    except Exception:
        pass
    return os.path.getmtime(p)        # se git non sa dirlo, meglio il disco che niente


def main():
    corsie = ""
    d = os.path.join(QUI, ".github", "workflows")
    if not os.path.isdir(d):
        print("SCOLLEGATO | non trovo le corsie: non posso controllare")
        return 0
    for f in os.listdir(d):
        if f.endswith((".yml", ".yaml")):
            corsie += open(os.path.join(d, f), errors="ignore").read()
    # anche gli agenti chiamati da un altro agente contano come collegati
    codice = ""
    for f in os.listdir(os.path.join(QUI, "agents")):
        if f.endswith(".py"):
            codice += open(os.path.join(QUI, "agents", f), errors="ignore").read()

    soli, vecchi = [], []
    for f in sorted(os.listdir(os.path.join(QUI, "agents"))):
        if not f.endswith(".py"):
            continue
        nome = f[:-3]
        if nome in A_MANO:
            continue
        p = os.path.join(QUI, "agents", f)
        testo = open(p, errors="ignore").read()
        if "def main(" not in testo:
            continue                       # e' una libreria
        if f in corsie or nome in corsie:
            continue                       # chiamato da una corsia
        # chiamato da un altro agente?
        if re.search(rf'["\']{re.escape(f)}["\']', codice) or f'agents/{f}' in codice:
            continue
        soli.append(f)

    noti_p = os.path.join(QUI, "data", "scollegati_noti.json")
    noti = set()
    if os.path.exists(noti_p):
        try:
            noti = set(json.load(open(noti_p))["gia_scollegati"])
        except Exception:
            noti = set()
    else:
        # prima volta: si fotografa e si dichiara
        os.makedirs(os.path.dirname(noti_p), exist_ok=True)
        json.dump({"fotografia": int(time.time()),
                   "perche": ("insieme degli agenti gia' scollegati quando il controllo e' nato "
                              "(6/10/2026). Non e' un'assoluzione: e' il punto da cui si misura. "
                              "Se uno di questi viene collegato, esce da solo."),
                   "gia_scollegati": sorted(soli)}, open(noti_p, "w"), indent=1)
        print(f"SCOLLEGATO | prima volta: fotografati {len(soli)} agenti gia' scollegati in "
              f"{noti_p}. D'ora in poi segnalo solo i NUOVI.")
        return 0
    nuovi = [f for f in soli if f not in noti]
    rimasti = [f for f in soli if f in noti]
    if not nuovi:
        print(f"SCOLLEGATO | nessun agente NUOVO scollegato "
              f"({len(rimasti)} dalla fotografia del passato, {len(A_MANO)} esclusi col motivo)")
        return 0
    print(f"SCOLLEGATO | {len(nuovi)} agenti NUOVI scritti e mai collegati: vivrebbero solo "
          f"nella sessione che li ha scritti.")
    for f in nuovi:
        print(f"   agents/{f}")
    return 0

    if not soli:
        print(f"SCOLLEGATO | tutti gli agenti toccati negli ultimi {GIORNI:g} giorni sono "
              f"collegati a una corsia ({len(A_MANO)} esclusi di proposito col motivo scritto, "
              f"{len(vecchi)} piu' vecchi non guardati)")
        return 0
    print(f"SCOLLEGATO | {len(soli)} agenti scritti negli ultimi {GIORNI:g} giorni e MAI "
          f"collegati: vivrebbero solo nella sessione che li ha scritti.")
    for f in soli:
        print(f"   agents/{f}")
    return 0        # non blocca: un agente nuovo puo' essere collegato un minuto dopo


if __name__ == "__main__":
    sys.exit(main())
