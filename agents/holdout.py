#!/usr/bin/env python3
"""
HOLDOUT — i tre livelli di dati, divisi nel TEMPO (rifatto 01/09 dopo la consulenza esterna).

Com'era: un token su quattro finiva in "cassaforte" in base all'hash del suo indirizzo. Due problemi, ed
erano gravi:
  1. l'hash non isola nulla nel tempo: lo stesso periodo di mercato — e spesso lo stesso deployer, gli
     stessi wallet, la stessa moda — finisce sia in ricerca sia in cassaforte. Non e' un test indipendente,
     e' lo stesso esame con i nomi mescolati.
  2. dopo sette verdetti con feedback, quella cassaforte era diventata di fatto un set di validazione:
     anche un semplice "bocciato" trasferisce informazione a chi continua a cercare.

Com'e' ora, tre livelli separati dal TEMPO:
  · RICERCA      — i token piu' vecchi. Gli esploratori ci lavorano liberamente.
  · VALIDAZIONE  — la fascia intermedia. Il giudice la consulta piu' volte (e si consuma, lo sappiamo).
  · CONFERMA     — tutto cio' che nasce DA ADESSO in poi. Sigillata: si apre una volta sola, quando questi
                   token avranno un esito, e quel giorno il verdetto vale davvero.

La divisione temporale e' l'unica che risponde alla domanda che conta: *funziona su un mercato che non
abbiamo mai visto?* — perche' il mercato cambia nel tempo, non nell'ordine alfabetico degli indirizzi.
"""
import json, os, time

CONFIG = "data/holdout_config.json"
QUOTA_VALIDAZIONE = 0.25      # l'ultimo quarto dello storico fa da validazione


def _config():
    """La frontiera temporale, decisa UNA volta e mai piu' toccata: se la spostassimo dopo aver visto i
    risultati, avremmo semplicemente scelto il test che ci fa comodo."""
    if os.path.exists(CONFIG):
        try: return json.load(open(CONFIG))
        except Exception: pass
    cfg = {"sigillo_conferma": int(time.time()), "confine_validazione": None, "creato": int(time.time())}
    os.makedirs("data", exist_ok=True)
    json.dump(cfg, open(CONFIG, "w"))
    return cfg


def imposta_confine(nascite):
    """fissa il confine ricerca/validazione al 75° percentile delle nascite note (una volta sola)."""
    cfg = _config()
    if cfg.get("confine_validazione") or not nascite: return cfg
    n = sorted(x for x in nascite if x)
    if len(n) < 50: return cfg
    cfg["confine_validazione"] = n[int(len(n) * (1 - QUOTA_VALIDAZIONE))]
    json.dump(cfg, open(CONFIG, "w"))
    return cfg


def livello(nato_ts):
    """'ricerca' | 'validazione' | 'conferma' — in base a QUANDO il token e' nato."""
    cfg = _config()
    if not nato_ts: return "ricerca"
    if nato_ts >= cfg["sigillo_conferma"]: return "conferma"
    conf = cfg.get("confine_validazione")
    if conf and nato_ts >= conf: return "validazione"
    return "ricerca"


# --- compatibilita' con il codice esistente: 'cassaforte' = tutto cio' che la ricerca non deve vedere ---
def in_cassaforte(addr, nato_ts=None):
    if nato_ts is None: return False          # senza data di nascita si resta in ricerca (nessun filtro cieco)
    return livello(nato_ts) != "ricerca"


def per_ricerca(items, chiave=lambda x: x):
    return [x for x in items if not in_cassaforte(chiave(x))]


def per_validazione(items, chiave=lambda x: x):
    return [x for x in items if in_cassaforte(chiave(x))]
