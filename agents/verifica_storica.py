"""VERIFICA STORICA — «quel token, quel giorno, e' partito davvero?»

A COSA SERVE. L'esperimento retrospettivo funziona cosi': si chiede a Grok cosa si vedeva su X in un
giorno passato, con la vista tappata a quel giorno, e poi si controlla sui dati di mercato se quei
token sono davvero partiti nelle ore successive. Questo e' il secondo pezzo: il giudice.

PERCHE' IL GIUDICE VA SCRITTO PRIMA DI GUARDARE LE RISPOSTE. Se lo scrivessi dopo aver visto cosa
ha detto Grok, sceglierei — anche senza volerlo — la soglia che fa sembrare buono il risultato.
«E' partito» qui vuol dire una cosa sola, decisa adesso: **il massimo nelle ore successive supera
del 50% il prezzo di riferimento**. Non e' una soglia sacra, e' una soglia DICHIARATA.

L'ORA DI RIFERIMENTO E' L'ULTIMA DEL GIORNO CHIESTO. Se chiediamo del 3 settembre, il prezzo di
partenza e' quello delle 23:00 UTC di quel giorno: e' l'ultimo istante in cui uno che leggeva X
quel giorno avrebbe potuto comprare. Prendere il prezzo del mattino sarebbe regalarci un vantaggio
che nessuno aveva.

I TOKEN MORTI CONTANO. Un token che sparisce, o il cui pool resta senza liquidita', non e' un dato
mancante: e' un esito, e va scritto. Buttare via i morti e' il modo piu' rapido per far sembrare
geniale qualunque selezione.
"""
import json
import os
import time
import urllib.request

GT = "https://api.geckoterminal.com/api/v2"
SOGLIA_PARTITO = float(os.environ.get("SOGLIA_PARTITO", 1.5))   # +50% = «partito»
FINESTRE_ORE = [6, 12, 24]


def gt(percorso, tentativi=4):
    for k in range(tentativi):
        try:
            r = urllib.request.Request(f"{GT}{percorso}",
                                       headers={"Accept": "application/json",
                                                "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(r, timeout=30) as x:
                return json.load(x), None
        except Exception as e:
            if k < tentativi - 1:
                time.sleep(5 * (k + 1))
                continue
            return None, f"{type(e).__name__} {getattr(e, 'code', '')}"
    return None, "esauriti"


def pool_migliore(chain, contract):
    """Il pool con piu' liquidita' per quel token. Regola dichiarata, non scelta caso per caso."""
    d, err = gt(f"/networks/{chain}/tokens/{contract}/pools?page=1")
    if not d:
        return None, err
    migliore = None
    for p in d.get("data", []) or []:
        a = p.get("attributes") or {}
        try:
            liq = float(a.get("reserve_in_usd") or 0)
        except (TypeError, ValueError):
            liq = 0.0
        if migliore is None or liq > migliore[1]:
            migliore = (a.get("address"), liq, a.get("name"), a.get("pool_created_at"))
    if not migliore:
        return None, "nessun pool"
    return {"pool": migliore[0], "liquidita_oggi": migliore[1],
            "nome": migliore[2], "creato": migliore[3]}, None


def verifica(chain, contract, giorno):
    """giorno = 'YYYY-MM-DD'. Torna il verdetto, o il motivo per cui non si puo' dare."""
    esito = {"chain": chain, "contract": contract, "giorno": giorno,
             "soglia_dichiarata": SOGLIA_PARTITO}
    pm, err = pool_migliore(chain, contract)
    if not pm:
        esito.update({"verdetto": "NON VERIFICABILE", "motivo": f"pool non trovato ({err})"})
        return esito
    esito.update(pm)
    time.sleep(2)
    # si guardano le 36 ore che seguono la fine del giorno chiesto
    # UTC, NON L'ORA DEL MIO PORTATILE (16/09). Usavo time.mktime, che interpreta la data come ora
    # LOCALE: da Milano in ora legale sono due ore di sfasamento su OGNI misura. Non e' un errore
    # che si nota guardando i risultati — sposta tutto della stessa quantita', quindi i numeri
    # sembrano sensati e sono sbagliati insieme. Si e' visto solo perche' il verdetto stampava
    # «ora di riferimento 21:00» quando avevo chiesto le 23:00.
    # calendar.timegm legge la data come UTC, che e' l'unico fuso che esiste sulla catena.
    import calendar
    fine_giorno = calendar.timegm(time.strptime(giorno + " 23:00", "%Y-%m-%d %H:%M"))
    dopo = fine_giorno + 36 * 3600
    c, err = gt(f"/networks/{chain}/pools/{pm['pool']}/ohlcv/hour"
                f"?aggregate=1&before_timestamp={dopo}&limit=72")
    if not c:
        esito.update({"verdetto": "NON VERIFICABILE", "motivo": f"candele assenti ({err})"})
        return esito
    righe = sorted((c.get("data", {}).get("attributes", {}) or {}).get("ohlcv_list") or [])
    if not righe:
        esito.update({"verdetto": "NON VERIFICABILE", "motivo": "nessuna candela nel periodo"})
        return esito
    prima = [r for r in righe if r[0] <= fine_giorno]
    if not prima:
        esito.update({"verdetto": "NON VERIFICABILE",
                      "motivo": "nessuna candela entro la fine del giorno: il pool non esisteva "
                                "ancora, quindi quel giorno non era comprabile"})
        return esito
    base = prima[-1][4]          # chiusura dell'ultima ora del giorno chiesto
    esito["prezzo_riferimento"] = base
    esito["ora_riferimento"] = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(prima[-1][0]))
    if not base:
        esito.update({"verdetto": "NON VERIFICABILE", "motivo": "prezzo di riferimento nullo"})
        return esito
    for ore in FINESTRE_ORE:
        dentro = [r for r in righe if fine_giorno < r[0] <= fine_giorno + ore * 3600]
        if not dentro:
            esito[f"T+{ore}h"] = {"dato": "MANCANTE"}
            continue
        mx = max(r[2] for r in dentro)
        mn = min(r[3] for r in dentro)
        fin = dentro[-1][4]
        vol = sum(r[5] or 0 for r in dentro)
        esito[f"T+{ore}h"] = {
            "massimo_su_riferimento": round(mx / base, 3),
            "minimo_su_riferimento": round(mn / base, 3),
            "chiusura_su_riferimento": round(fin / base, 3),
            "volume": round(vol, 2),
            "candele": len(dentro),
        }
    sei = esito.get("T+6h", {})
    ventiquattro = esito.get("T+24h", {})
    picco = max([x.get("massimo_su_riferimento", 0) for x in (sei, ventiquattro)
                 if isinstance(x, dict) and "massimo_su_riferimento" in x] or [0])
    # IL PICCO DA SOLO E' UNA BUGIA GENTILE (16/09, imparato al primo caso vero). Il primo token
    # verificato, $USMS, ha fatto 2,26x nelle sei ore dopo — e nelle stesse sei ore e' andato a
    # ZERO. Il mio verdetto diceva «PARTITO», e chi avesse comprato e tenuto avrebbe perso tutto.
    # Un massimo si incassa solo se vendi esattamente li'; un minimo a zero lo subisci sempre.
    # Quindi il verdetto porta SEMPRE tutti e due, e distingue chi e' salito e ha tenuto da chi e'
    # salito ed e' collassato. E' la differenza fra un segnale e un miraggio.
    fondo = min([x.get("minimo_su_riferimento", 1) for x in (sei, ventiquattro)
                 if isinstance(x, dict) and "minimo_su_riferimento" in x] or [1])
    finale = None
    for k in ("T+24h", "T+12h", "T+6h"):
        v_ = esito.get(k)
        if isinstance(v_, dict) and "chiusura_su_riferimento" in v_:
            finale = v_["chiusura_su_riferimento"]
            break
    esito["picco"] = picco
    esito["fondo"] = fondo
    esito["chiusura"] = finale
    if picco == 0:
        esito["verdetto"] = "NON VERIFICABILE"
        esito["motivo"] = "nessuna finestra con dati"
    elif picco >= SOGLIA_PARTITO and (finale is not None and finale < 0.2):
        esito["verdetto"] = "PARTITO E CROLLATO"
        esito["nota"] = (f"massimo {picco}x ma chiusura a {finale}x del riferimento: "
                         f"incassabile solo vendendo sul picco")
    elif picco >= SOGLIA_PARTITO:
        esito["verdetto"] = "PARTITO"
    else:
        esito["verdetto"] = "non partito"
    return esito


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 4:
        print("uso: verifica_storica.py <chain> <contract> <YYYY-MM-DD>")
        raise SystemExit(1)
    print(json.dumps(verifica(sys.argv[1], sys.argv[2], sys.argv[3]),
                     ensure_ascii=False, indent=1))
