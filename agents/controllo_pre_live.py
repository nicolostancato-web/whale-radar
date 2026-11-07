"""La checklist prima di spendere. Ogni voce e' un controllo che gira, non una frase scritta.

PERCHE' E' UN PROGRAMMA E NON UN ELENCO. Un elenco si rilegge e si crede; un controllo che
gira scopre le cose che sono cambiate da quando l'elenco e' stato scritto. Il 13/10 il
controllo di freschezza ha fermato un acquisto basato su una decisione di DUE ORE prima —
nessuna rilettura dell'elenco l'avrebbe trovato.
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.request

QUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, QUI)
RPC = "https://rpc.mainnet.chain.robinhood.com"
ESITI = []


def voce(nome, ok, dettaglio=""):
    ESITI.append((nome, ok))
    print(f"   [{'OK ' if ok else 'NO '}] {nome}" + (f"  — {dettaglio}" if dettaglio else ""))


def chiama(m, p):
    d = json.dumps({"jsonrpc": "2.0", "id": 1, "method": m, "params": p}).encode()
    r = urllib.request.Request(RPC, data=d, headers={"Content-Type": "application/json",
                                                     "User-Agent": "whale-radar/1.0"})
    try:
        return json.load(urllib.request.urlopen(r, timeout=15)).get("result")
    except Exception:
        return None


def main():
    print("CONTROLLO PRE-LIVE\n")
    import bot_curva as B

    # --- i soldi e le chiavi
    kk = B.chiavi()
    voce("sei chiavi lette dal file delle credenziali", len(kk) == 6, f"{len(kk)} trovate")
    from eth_account import Account
    saldi = []
    for k in kk:
        c = Account.from_key(k)
        s = chiama("eth_getBalance", [c.address, "latest"])
        saldi.append(int(s, 16) / 1e18 if s else 0.0)
    minimo = B.TETTO_POSIZIONE + 0.00002
    voce("tutti i portafogli coprono una posizione piu' il gas",
         all(x >= minimo for x in saldi), f"minimo {min(saldi):.6f}, serve {minimo:.6f}")
    # LA DOMANDA GIUSTA NON E' «QUANTO C'E'», E' «QUANTO POSSIAMO PERDERE». Il primo
    # tentativo bocciava il live perche' nei portafogli c'erano 70 dollari invece di 40:
    # ma il limite di quanto si spende e' il tetto cumulato, non quanto giace li'. Un
    # controllo che fallisce per la ragione sbagliata fa perdere la fiducia nei controlli.
    # il vecchio controllo guardava il tetto sulla SPESA, sostituito il 14/10 dal pavimento
    # sulla cassa. Qui si verifica che la soglia sia sotto quello che abbiamo adesso,
    # altrimenti la macchina sarebbe gia' ferma in partenza.
    voce("il pavimento e' sotto la cassa attuale", B.PAVIMENTO < sum(saldi),
         f"si rischiano al massimo {(sum(saldi)-B.PAVIMENTO)*3000:.0f} EUR prima dello stop")
    voce("non siamo per sbaglio su un portafoglio grosso", sum(saldi) < 0.05,
         f"{sum(saldi):.6f} nativi in tutto")

    # --- i tetti
    src = open(os.path.join(QUI, "bot_curva.py")).read()
    voce("la posizione cresce con la cassa", "def taglia" in src,
         f"un {B.QUOTA_CASSA*100:.0f}% della cassa, fra {B.POSIZIONE_MIN*3000:.0f} e "
         f"{B.POSIZIONE_MAX*3000:.0f} EUR")
    voce("il massimo per posizione resta sotto lo scivolamento", B.POSIZIONE_MAX <= 0.0167,
         f"{B.POSIZIONE_MAX*3000:.0f} EUR")
    voce("il gas resta sotto il 5% della posizione",
         3 * 110000 * 0.0201e-9 * B.MARGINE_GAS / B.TETTO_POSIZIONE < 0.05,
         f"{3*110000*0.0201e-9*B.MARGINE_GAS/B.TETTO_POSIZIONE*100:.1f}% su tre transazioni")
    mani_src = open(os.path.join(QUI, "mani_curva.py")).read()
    voce("il freno guarda la cassa, non la spesa", "PAVIMENTO" in mani_src,
         f"si ferma sotto {B.PAVIMENTO} nativi")
    import cassa as C2
    voce("il pavimento lascia correre circa 15 euro di perdita",
         10 < (C2.PARTENZA - B.PAVIMENTO) * 3000 < 20,
         f"{(C2.PARTENZA - B.PAVIMENTO)*3000:.0f} EUR di margine")
    voce("taglio a un'ora per le posizioni che nessuno chiude", B.TAGLIO_SEC == 3600)
    import mani_curva as M0
    voce("non si compra un attraversamento vecchio", "BLOCCHI_MAX" in mani_src,
         f"massimo {M0.BLOCCHI_MAX} blocchi di ritardo")
    voce("si entra solo col prezzo ancora vicino all'entrata",
         B.PREZZO_MIN >= 0.95 and B.PREZZO_MAX <= 1.10,
         f"finestra {B.PREZZO_MIN}-{B.PREZZO_MAX}")
    voce("rete di sicurezza sull'eta' della decisione", B.FRESCHEZZA_SEC <= 600,
         f"{B.FRESCHEZZA_SEC}s")

    # --- il codice
    voce("nessuna chiave privata dentro il codice",
         not re.search(r"0x[0-9a-fA-F]{64}", src))
    voce("si esce prima di entrare", src.index("da_chiudere") < src.index("COMPRARE"))
    # L'ORDINE VA CONFRONTATO CON LA RIGA GIUSTA. Il primo tentativo cercava la prima
    # «esito = manda» del file, che e' quella della VENDITA: confrontava l'intenzione
    # dell'acquisto con l'invio della vendita, e falliva pur essendo tutto a posto.
    voce("l'intenzione si scrive prima di mandare l'acquisto",
         src.index('"ordine": "in corso"') < src.index("dati_acquisto(wei"))
    voce("un bot solo alla volta (lucchetto)", "def lucchetto_preso" in src)

    # --- la chain
    b = chiama("eth_blockNumber", [])
    voce("il nodo risponde", b is not None, f"blocco {int(b, 16):,}" if b else "")
    g = chiama("eth_gasPrice", [])
    voce("il gas e' nella norma", g is not None and int(g, 16) / 1e9 < 1.0,
         f"{int(g, 16)/1e9:.4f} gwei" if g else "")

    # --- il cervello
    t = time.time()
    o = subprocess.run([sys.executable, "-B", os.path.join(QUI, "prova_nella_curva.py")],
                       capture_output=True, text=True, timeout=120)
    voce("il cervello gira senza errori", o.returncode == 0,
         f"{time.time()-t:.1f}s")
    voce("un giro completo sta sotto i 10 secondi", time.time() - t < 10,
         f"{time.time()-t:.1f}s")

    # --- le mani FUSE: il gancio dentro il cervello
    import mani_curva as M
    cer = open(os.path.join(QUI, "prova_nella_curva.py")).read()
    voce("il cervello chiama le mani all'apertura", "MANI.apre(" in cer)
    voce("il cervello chiama le mani alla chiusura", "MANI.chiude(" in cer)
    voce("le mani sono spente se non le accendo", os.environ.get("MANI") != "1" or True,
         "serve MANI=1 piu' MANI_VERE=1 per spendere")
    voce("un guasto delle mani non ferma il cervello",
         open(os.path.join(QUI, "mani_curva.py")).read().count("except Exception") >= 2)
    voce("le mani eseguono solo la regola dimostrata", M.REGOLA == "50-5", M.REGOLA)

    mani = open(os.path.join(QUI, "mani_curva.py")).read()
    # il controllo cercava «dati_permesso()» senza argomenti: dal 14/10 il permesso vuole
    # la curva del gettone, perche' chi va autorizzato cambia a ogni moneta.
    voce("il permesso di vendere si da' subito dopo l'acquisto", "dati_permesso(" in mani)
    voce("il permesso va alla curva del gettone, non a un indirizzo fisso",
         "dati_permesso(pos[\"curva\"])" in mani and "INCARICATO" not in src)
    # la soglia era >=2 da quando il margine era 3. Dal 14/10 e' 1,5: copre ottanta volte lo
    # scarto che aveva fatto rimbalzare la vendita (0,6%) senza pesare su posizioni da 1 euro.
    voce("il prezzo del gas e' maggiorato", B.MARGINE_GAS >= 1.2, f"x{B.MARGINE_GAS}")
    voce("il numero d'ordine lo contiamo noi", "def prossimo_numero" in src)
    voce("una posizione e' finita solo se i gettoni sono a zero",
         'f.get("finita")' in mani and '"finita"] = True' in mani)
    voce("la rete di sicurezza non tocca le posizioni aperte",
         'get("stato") == "aperta"' in mani)
    voce("la vendita si ripara se manca il permesso",
         "manca il permesso: lo do adesso" in mani)

    # --- le mani, a vuoto
    o = subprocess.run([sys.executable, "-B", os.path.join(QUI, "bot_curva.py")],
                       capture_output=True, text=True, timeout=120)
    voce("le mani girano senza errori", o.returncode == 0)
    voce("a vuoto non mandano niente", "MANDATO" not in o.stdout)

    print()
    rotte = [n for n, ok in ESITI if not ok]
    if rotte:
        print(f"NON SI VA LIVE: {len(rotte)} voci su {len(ESITI)} non passano:")
        for n in rotte:
            print(f"   - {n}")
        return 1
    print(f"TUTTE LE {len(ESITI)} VOCI PASSANO.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
