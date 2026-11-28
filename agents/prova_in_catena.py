# -*- coding: utf-8 -*-
"""L'ESECUZIONE VERA, su una copia della catena di ADESSO.

Perche' esiste (4/11). Il C-check era arrivato a coprire ogni stadio della
catena -- accorgersi, comporre, firmare, consegnare, verificare la cassa,
avvisare, fermarsi -- tranne UNO: l'esecuzione in catena, cioe' il momento
in cui i soldi si muovono davvero. Quello era provato una volta sola, la
mattina del 3/11, con i dati di allora. Ma la liquidita' cambia: una prova
di ieri dice che funzionava ieri.

Qui si prende una posizione VIVA vicina alla caduta, si rigenera l'ordine
con i prezzi di adesso, si biforca la catena al blocco corrente, si forza
un crollo e si esegue la nostra liquidazione per davvero sulla copia.
Costa zero (e' una copia locale) e dice se funzionerebbe ORA.

Lezione che gli sta dietro: una riproduzione locale su un caso vero uccide
un piano in una serata a costo zero. Vale anche al contrario -- lo conferma.
"""
import json, os, subprocess, sys, time
sys.path.insert(0, "agents")
D = "data/liquidazioni"
FUORI = f"{D}/prova_in_catena.json"
CALO = os.environ.get("CALO_MINIMO", "90")       # un dump del 9%
# Il guadagno preteso NON si passa piu' da fuori: lo calcola prepara_prova
# nella moneta del debito e lo scrive in p_guadagno.txt. Passarlo come
# numero grezzo era sbagliato per costruzione (un importo senza la sua
# moneta) e faceva fallire la prova su ogni debito a 6 decimali.
def scegli():
    """Una posizione viva, coppia DIVERSA (quelle che cadono nei dump),
    con garanzia ammessa e un premio che vale la prova."""
    from pescatore import AMMESSI
    import re
    from famiglie import famiglia as _fam_di, SCENDONO
    fam = _fam_di
    s = json.load(open(f"{D}/salute_note.json"))
    co = {k.lower(): v for k, v in json.load(open(f"{D}/composizione.json")).items()}
    cand = []
    for a, d in s.items():
        c = co.get(a)
        if not c: continue
        g = c["garanzia_principale"].lower()
        if g not in AMMESSI: continue
        if fam(g) == fam(c["debito_principale"]): continue      # coppia uguale
        if not (1.0 <= d["salute"] < 1.25): continue
        if d["debito"] * 0.5 * 0.07 < 2000: continue
        cand.append((d["salute"], a))
    cand.sort()
    return cand[0][1] if cand else None
def main():
    u = scegli()
    if not u:
        print("   nessuna posizione adatta alla prova"); return 2
    print(f"   provo sulla posizione viva {u[:14]}")
    r = subprocess.run([".venv_bot2/bin/python", "agents/prepara_prova.py", u],
                       capture_output=True, text=True, timeout=300)
    print("   " + "\n   ".join((r.stdout or "").strip().splitlines()[-3:]))
    if "dati scritti" not in (r.stdout or ""):
        # UN RIFIUTO DELLA FONTE NON E' UN GUASTO NOSTRO. Il 4/11 un 429 di
        # Paraswap (la prova competeva col giro del laghetto) sarebbe
        # apparso come "esecuzione in catena FALLITA" -- il falso allarme
        # peggiore, perche' avrebbe fatto cercare un guasto che non c'era.
        # Il verdetto precedente si TIENE: dire "non lo so adesso" e' molto
        # meglio che dire "e' rotto".
        rinviata = r.returncode == 3
        vecchio = {}
        try: vecchio = json.load(open(FUORI))
        except Exception: pass
        json.dump({"quando_tentato": time.time(),
                   "esito": "fonte occupata, prova rinviata" if rinviata
                            else "dati non preparati",
                   "rinviata": rinviata, "utente": u,
                   "quando": vecchio.get("quando"),
                   "passa": vecchio.get("passa"),
                   "verdetto_di": "prova precedente" if vecchio else None},
                  open(FUORI, "w"), indent=1)
        print("   prova RINVIATA (fonte occupata): tengo il verdetto precedente"
              if rinviata else "   dati di prova NON preparati")
        return 3 if rinviata else 1
    amb = dict(os.environ, CALO_MINIMO=CALO,
               RPC_ARCHIVIO="https://gateway.tenderly.co/public/mainnet")
    t = subprocess.run([os.path.expanduser("~/.foundry/bin/forge"), "test",
                        "--match-contract", "ProvaVera"],
                       cwd="liquidatore", capture_output=True, text=True,
                       env=amb, timeout=900)
    uscita = (t.stdout or "") + (t.stderr or "")
    passa = "[PASS]" in uscita
    motivo = ""
    if not passa:
        for riga in uscita.splitlines():
            if "[FAIL" in riga: motivo = riga.strip()[:160]; break
    json.dump({"quando": time.time(), "utente": u, "calo_forzato_decimi": CALO,
               "passa": passa,
               "motivo": motivo}, open(FUORI, "w"), indent=1)
    print(f"   ESECUZIONE SU COPIA DELLA CATENA DI ADESSO: "
          f"{'PASSA' if passa else 'FALLISCE — ' + motivo}")
    return 0 if passa else 1
if __name__ == "__main__":
    sys.exit(main())
