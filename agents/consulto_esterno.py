# -*- coding: utf-8 -*-
"""IL CONSULTO ESTERNO: Astra (GPT-5) e Grok, due volte al giorno.

PERCHE' ESISTE (4/11, direttiva di Nicolo'). Il 4/11 i cinque blocchi erano
al 100% mentre perdevamo $422.496 di premio in 24 ore: nessuna delle 90
verifiche guardava fuori. Chi ha trovato il buco e' stato Nicolo' con una
domanda. I revisori esterni fanno lo stesso mestiere: vedono i punti ciechi
che per definizione non possiamo vedere da dentro.
Esito del primo consulto: entrambi hanno detto che ci manca un blocco (il
mercato dello spazio nel blocco) e che dare la colpa a UN solo blocco ci
fa ottimizzare la cosa sbagliata. Due cose che non avevamo visto.

PRIORITA': dove Astra e Grok discordano, vale ASTRA (direttiva di Nicolo').

REGOLE DI SPESA (CFO mode, e il tetto e' nel codice non nelle intenzioni):
  - il credito e' PREPAGATO su CometAPI: non esistono sorprese in bolletta
  - costo misurato del primo consulto: ~0,15 USD per Astra, ~0,02 per Grok
  - tetto: TETTO_GIORNALIERO dollari al giorno, contati e salvati su file
  - se il tetto e' raggiunto si salta e si scrive perche'
  - MAI piu' di DUE consulti al giorno (uno la mattina, uno la sera)

LEZIONE DAL PRIMO CONSULTO, scritta qui perche' non si ripeta: avevo messo
nel prompt un fatto NON VERIFICATO (dicevo che un pagamento di 210 ETH nel
blocco era una mancia del vincitore; era il builder che pagava il
validatore, cosa che c'e' in quasi ogni blocco). Entrambi hanno costruito
la loro tesi centrale su quel fatto. **I revisori amplificano quello che
gli dai, compresi gli errori.** Prima di chiedere, si verifica cosa si sta
affermando: nel prompt vanno solo cose misurate, e quelle incerte vanno
dichiarate incerte.
"""
import json, os, sys, time, urllib.request
sys.path.insert(0, "agents")
D = "data/liquidazioni"
SPESA = f"{D}/spesa_consulti.json"
CARTELLA = "consulenze"
# Alzato da 0,60 a 2,00 il 6/11, insieme al passaggio ai modelli piu'
# potenti: un modello che ragiona costa di piu' per risposta, e il tetto
# serve a fermare una fuga, non a impedire le due consulenze del giorno.
# Due consulenze al giorno a 2 dollari fanno 60 dollari al mese nel caso
# peggiore: se la spesa reale si avvicina a quella cifra va rivista con
# Nicolo', perche' il valore di una consulenza si misura in riparazioni
# trovate e finora ne ha trovate tante.
TETTO_GIORNALIERO = float(os.environ.get("TETTO_CONSULTI", "2.00"))
# MASSIMI_AL_GIORNO esiste per non bruciare il budget da solo, e resta 2.
# Ma il limite VERO e' il denaro (TETTO_GIORNALIERO), e il conteggio ne e'
# solo un approssimativo. Quando Nicolo' autorizza ESPLICITAMENTE un consulto
# in piu', il conteggio non deve bloccarlo mentre la spesa e' a un sesto del
# tetto -- succede, ed e' il caso del 6/11: 2 consulti su 2 ma 0,10 $ su 0,60.
# Il tetto in DOLLARI non si scavalca mai: quello e' il guardiano vero.
MASSIMI_AL_GIORNO = int(os.environ.get("MASSIMI_CONSULTI", "2"))
# prezzi misurati il 4/11 su CometAPI, per mille token
# I MODELLI PIU' POTENTI DISPONIBILI (6/11, direttiva di Nicolo': «usa
# l'ultimo modello di Astra, il piu' potente, e anche di Grok. Sempre»).
#
# PROVATI uno per uno sul fornitore invece di indovinare dal nome:
#   gpt-6.1-terra              risponde (generazione 6.1, la piu' nuova)
#   gpt-6.1-sol                NON disponibile (400)
#   gpt-6-astra                risponde, ma e' la generazione precedente
#   grok-4.20-0309-reasoning   risponde e RAGIONA davvero: 753 token di
#                              risposta contro i 90 della variante fast che
#                              usavamo prima
# Prima usavamo gpt-5 e grok-4-1-fast-reasoning: il secondo era la variante
# «fast», cioe' esplicitamente non la piu' capace.
#
# NOTA CFO: il prezzo di questi due non lo conosco, quindi la stima qui sotto
# e' prudenziale e il costo registrato sara' approssimato finche' non lo
# misuro sul conto del fornitore. Per questo il guardiano vero resta il TETTO
# IN DOLLARI, non il conteggio dei consulti: se costano piu' del previsto, il
# tetto li ferma da solo.
PREZZI = {"gpt-6.1-terra": (0.01, 0.06), "grok-4.20-0309-reasoning": (0.001, 0.005),
          "gpt-5": (0.00125, 0.01), "grok-4-1-fast-reasoning": (0.0002, 0.0005)}
MODELLI = [("gpt-6.1-terra", "Astra"), ("grok-4.20-0309-reasoning", "Grok")]
def _chiave():
    import subprocess
    r = subprocess.run(["grep", "-i", "^Cometapi:",
                        os.path.expanduser("~/Documents/b2b-finder-credentials.txt")],
                       capture_output=True, text=True)
    riga = (r.stdout or "").strip()
    if not riga: return None
    return riga.split(":", 1)[1].strip()
def _spesa_oggi():
    oggi = time.strftime("%Y-%m-%d", time.gmtime())
    try: d = json.load(open(SPESA))
    except Exception: d = {}
    return oggi, d.get(oggi, {"dollari": 0.0, "consulti": 0}), d
def _registra(costo):
    oggi, _, d = _spesa_oggi()
    v = d.setdefault(oggi, {"dollari": 0.0, "consulti": 0})
    v["dollari"] = round(v["dollari"] + costo, 4)
    v["consulti"] += 1
    json.dump(d, open(SPESA, "w"), indent=1)
def chiedi(modello, domanda, tetto_token=16000):
    K = _chiave()
    if not K: return None, "nessuna chiave CometAPI"
    corpo = json.dumps({"model": modello,
                        "messages": [{"role": "user", "content": domanda}],
                        "max_tokens": tetto_token}).encode()
    t0 = time.time()
    try:
        r = urllib.request.urlopen(urllib.request.Request(
            "https://api.cometapi.com/v1/chat/completions", data=corpo,
            headers={"Authorization": f"Bearer {K}",
                     "Content-Type": "application/json"}), timeout=900)
        d = json.load(r)
        txt = d["choices"][0]["message"]["content"]
        u = d.get("usage") or {}
        pin, pout = PREZZI.get(modello, (0.001, 0.01))
        costo = (u.get("prompt_tokens", 0)/1000*pin
                 + u.get("completion_tokens", 0)/1000*pout)
        _registra(costo)
        return txt, {"secondi": int(time.time()-t0), "costo_usd": round(costo, 4),
                     "token_in": u.get("prompt_tokens"),
                     "token_out": u.get("completion_tokens")}
    except Exception as e:
        return None, str(e)[:160]
def main():
    if len(sys.argv) < 2:
        print("   uso: consulto_esterno.py <file_con_la_domanda> [etichetta]")
        return 2
    dom = open(sys.argv[1]).read()
    eti = sys.argv[2] if len(sys.argv) > 2 else "consulto"
    oggi, sp, _ = _spesa_oggi()
    if sp["consulti"] >= MASSIMI_AL_GIORNO:
        print(f"   oggi ho gia' fatto {sp['consulti']} consulti "
              f"(massimo {MASSIMI_AL_GIORNO}): salto"); return 0
    if sp["dollari"] >= TETTO_GIORNALIERO:
        print(f"   tetto di spesa raggiunto (${sp['dollari']:.2f} di "
              f"${TETTO_GIORNALIERO:.2f}): salto"); return 0
    os.makedirs(CARTELLA, exist_ok=True)
    fatti = []
    for modello, nome in MODELLI:
        txt, info = chiedi(modello, dom)
        if not txt:
            print(f"   {nome}: non ha risposto ({info})"); continue
        p = f"{CARTELLA}/CONSULENZA_{nome}_{eti}_{oggi}.md"
        open(p, "w").write(f"# {nome} ({modello}) — {eti} — {oggi}\n\n"
                           f"costo ${info['costo_usd']}, {info['secondi']}s, "
                           f"{info['token_out']} token di risposta\n\n---\n\n{txt}\n")
        print(f"   {nome}: {len(txt)} caratteri, ${info['costo_usd']}, "
              f"{info['secondi']}s -> {p}")
        fatti.append((nome, p))
    oggi, sp, _ = _spesa_oggi()
    print(f"   spesa di oggi: ${sp['dollari']:.3f} su un tetto di "
          f"${TETTO_GIORNALIERO:.2f} ({sp['consulti']} consulti)")
    print(f"   DOVE ASTRA E GROK DISCORDANO, VALE ASTRA (direttiva di Nicolo')")
    return 0
if __name__ == "__main__":
    sys.exit(main())
