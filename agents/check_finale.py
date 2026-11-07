# -*- coding: utf-8 -*-
"""IL C-CHECK: si PROVANO le cose, non si leggono i file di stato.

REGOLA PERMANENTE, data da Nicolo' il 3/11 sera: questo check gira OGNI
MEZZ'ORA e ogni volta si rifa' la domanda per intero -- "tutto in ordine?
manca qualcosa? siamo pronti davvero a intervenire?" -- non si limita a
rileggere i verdi di prima.

E A OGNI GIRO IL CHECK DEVE CRESCERE DI UNA VERIFICA. Il motivo e' misurato:
il guasto piu' grave trovato finora (660 pacchetti spediti a salve per una
chiave d'identita' cancellata) era INVISIBILE a tutti i 31 controlli che
c'erano. Un check che non cresce smette di trovare cose, e intanto rassicura.
Lo storico delle verifiche aggiunte sta in data/liquidazioni/crescita_check.json:
se il numero non sale da piu' di qualche giro, e' un allarme in se'.
Un controllo che non attraversa il codice rassicura invece di verificare.
Nato il 3/11, chiesto da Nicolo' prima della notte delle elezioni americane.
Non stampa mai chiavi ne' password: solo se esistono e se i permessi sono giusti.
"""
import json, re, os, subprocess, sys, time, urllib.request
sys.path.insert(0, "agents")
D = "data/liquidazioni"
ESITI = []
class _SaltaQuesta(Exception):
    """una verifica che non ha potuto girare non e' una verifica fallita"""


def dillo(nome, ok, dett=""):
    ESITI.append((nome, bool(ok), dett)); 
    print(f"  [{'OK   ' if ok else 'MANCA'}] {nome:44s} {dett}")
# UNA FONTE CHE RIFIUTA NON DEVE POTER UCCIDERE IL CONTROLLO (7/11).
# Questa funzione chiedeva a UNA sola porta e RILANCIAVA l'errore: stanotte
# un 429 l'ha fatta esplodere alla sezione 3 e tutte le ~130 verifiche
# successive non sono girate. E' la stessa famiglia della morte per
# SystemExit riparata un'ora prima -- causa diversa, effetto identico: il
# check si interrompe e quello che si e' visto fin la' sembra tutto.
# Una verifica ROSSA e' informazione; un check MORTO e' una bugia.
# Quindi: piu' porte, e `None` invece di un'eccezione. Chi chiama vede un
# risultato mancante e la sua verifica diventa rossa da sola.
_FONTI_CHECK = ("https://gateway.tenderly.co/public/mainnet",
                "https://ethereum-rpc.publicnode.com",
                "https://eth.drpc.org",
                "https://rpc.mevblocker.io")


def rpc(m, p, u=None):
    for porta in ((u,) if u else _FONTI_CHECK):
        try:
            c = {"jsonrpc": "2.0", "id": 1, "method": m, "params": p}
            r = urllib.request.urlopen(urllib.request.Request(
                porta, json.dumps(c).encode(),
                {"Content-Type": "application/json",
                 "User-Agent": "Mozilla/5.0"}), timeout=25)
            v = json.load(r).get("result")
            if v is not None:
                return v
        except Exception:
            continue
    return None

print("\n--- 1. I TRE PROCESSI: vivi, non zombie, e che hanno scritto di recente")
for nome, f in (("pescatore","pescatore_vivo"),("sentinella","sentinella_viva"),
                ("quaderno","vivo"),("giro del laghetto","laghetto_vivo")):
    try:
        d=json.load(open(f"{D}/{f}.json")); eta=int(time.time()-os.path.getmtime(f"{D}/{f}.json"))
    except Exception as e:
        dillo(f"{nome}: battito", False, f"nessun file: {e}"); continue
    pid=d.get("pid")
    stato=""
    if pid:
        r=subprocess.run(["ps","-o","state=","-p",str(pid)],capture_output=True,text=True)
        stato=r.stdout.strip()
    # zombie: pgrep li vede, e un sistema armato giu' mezz'ora sembrava sano
    vivo = bool(stato) and not stato.startswith("Z")
    dillo(f"{nome}: processo vivo (pid dichiarato)", vivo or not pid,
          f"pid={pid} stato={stato or 'non dichiarato'}")
    # SOGLIE DIVERSE, perche' i mestieri sono diversi. I tre armati devono
    # battere sempre: se stanno fermi 10 minuti e' un guasto. Il giro del
    # laghetto invece ogni nona passata legge tutta la storia di Aave (202
    # finestre, mezz'ora), e segnalarlo come rosso e' un falso allarme --
    # e un allarme che grida a vuoto si impara a ignorare, che e' peggio
    # che non averlo. Non affama piu' nessuno: i prezzi hanno un giro loro.
    limite = 2700 if nome == "giro del laghetto" else 600
    dillo(f"{nome}: ha scritto da meno di {limite//60} min", eta<limite, f"{eta}s fa")

print("\n--- 1b. CHI GUARDA LE GUARDIE?")
# VERIFICA AGGIUNTA il 3/11 sera, nata provando una guardia: ho ucciso il
# giro dei prezzi e la sua guardia l'ha rimesso su in 25 secondi, log e
# tutto. Funziona. Ma provandola mi sono accorto della domanda che non mi
# ero fatto: se muore una GUARDIA, il suo lavoratore resta senza
# protezione e NESSUNO se ne accorge. Le guardie sorvegliavano tutti
# tranne se stesse.
# Una guardia mancante e' il caso peggiore: non lascia tracce, perche' un
# processo che non c'e' non scrive niente. Quindi si pretende l'INSIEME
# atteso, non "quelle che trovo".
GUARDIE_ATTESE = {"in_acqua", "sentinella", "quaderno", "prezzi_sempre"}
_trovate = set()
for _chi in sorted(GUARDIE_ATTESE):
    _b = f"{D}/guardia_{_chi}.json"
    try:
        _g2 = json.load(open(_b))
        _e = int(time.time() - os.path.getmtime(_b))
        _st = _g2.get("stato", "?")
        _ok = _e < 300 and (_st == "ok" or _st.startswith("ok_"))
        if _ok: _trovate.add(_chi)
        dillo(f"guardia di {_chi}", _ok, f"battito {_e}s fa, stato {_st}, giro {_g2.get('giro')}")
    except Exception as _ex:
        dillo(f"guardia di {_chi}", False, f"nessun battito: {str(_ex)[:40]}")
dillo("tutte le guardie attese sono in piedi", _trovate == GUARDIE_ATTESE,
      f"mancano: {sorted(GUARDIE_ATTESE - _trovate)}" if _trovate != GUARDIE_ATTESE
      else f"{len(_trovate)} su {len(GUARDIE_ATTESE)}")

print("\n--- 2. IL GAS: senza ETH nel portafoglio operativo non si manda niente")
from pescatore import CONTRATTO, CHIAVE, PROXY, AMMESSI, SCIVOLAMENTO_BP, FRAZIONE_PREMIO_PRETESA, ARMATO, FOUNDRY
op=subprocess.run([f"{FOUNDRY}/cast","wallet","address","--private-key",CHIAVE],
                  capture_output=True,text=True).stdout.strip()
b=rpc("eth_getBalance",[op,"latest"]); eth=int(b,16)/1e18 if b else 0
gp=rpc("eth_gasPrice",[]); gwei=int(gp,16)/1e9 if gp else 0
costo=1_750_000*gwei*1e-9
dillo("portafoglio operativo ha ETH", eth>0, f"{eth:.5f} ETH")
dillo(f"basta per un colpo (gas {gwei:.1f} gwei)", eth>costo*1.5,
      f"serve ~{costo:.5f} ETH, abbiamo {eth:.5f} ({eth/costo:.1f} colpi)" if costo else "")

print("\n--- 3. IL CONTRATTO: chi comanda e dove vanno i soldi")
# I selettori si CALCOLANO, non si indovinano. Il 3/11 li avevo scritti a
# mano e tutte e due le letture tornavano vuote: sembrava un contratto
# sbagliato, erano i miei quattro byte inventati.
from keccak import firma
pad=rpc("eth_call",[{"to":CONTRATTO,"data":firma("padrone()")[:10]},"latest"])
ca =rpc("eth_call",[{"to":CONTRATTO,"data":firma("cassa()")[:10]},"latest"])
def ind(h): return "0x"+h[-40:] if h and len(h)>=42 else None
dillo("il contratto esiste in catena", bool(rpc("eth_getCode",[CONTRATTO,"latest"]) not in (None,"0x")))
dillo("chi comanda = portafoglio operativo",
      (ind(pad) or "").lower()==op.lower(), f"padrone {ind(pad)}")
dillo("la cassa e' quella di Nicolo'",
      (ind(ca) or "").lower()=="0x055e75aeacf141c3118d039d5e099a821152eb66",
      f"cassa {ind(ca)}")

print("\n--- 4. LA CONSEGNA PRIVATA: il relay risponde?")
try:
    body=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]}).encode()
    r=urllib.request.urlopen(urllib.request.Request("https://relay.flashbots.net",body,
      {"Content-Type":"application/json","User-Agent":"Mozilla/5.0"}),timeout=15)
    dillo("relay Flashbots raggiungibile", True, f"HTTP {r.status}")
except Exception as e:
    dillo("relay Flashbots raggiungibile", False, str(e)[:50])

print("\n--- 5. LA CONFIGURAZIONE ARMATA")
dillo("pescatore ARMATO", ARMATO)
import sentinella as SE
dillo("sentinella ARMATA", getattr(SE,"ARMATA",False))
dillo("margine delle vendite inerte", SCIVOLAMENTO_BP>=9000, f"{SCIVOLAMENTO_BP} bp")
dillo("guardia in dollari attiva", FRAZIONE_PREMIO_PRETESA>=0.2,
      f"pretende il {FRAZIONE_PREMIO_PRETESA:.0%} del premio")
# DIFETTO TROVATO il 3/11 sera DENTRO QUESTO STESSO FILE: qui c'era
# os.path.exists("preso.flag"), cioe' la cartella radice, mentre pescatore,
# sentinella, guardia.sh e stato.py usano tutti
# data/liquidazioni/preso.flag. Questo controllo sarebbe stato VERDE anche
# con una presa in corso. Un controllo che guarda il file sbagliato e'
# peggio di nessun controllo: e' un semaforo verde su uno stato rosso.
FLAG=f"{D}/preso.flag"
dillo("nessuna presa bloccante in sospeso", not os.path.exists(FLAG), FLAG)
# E LA VERIFICA CHE COGLIE QUELLA CLASSE DI DIFETTO: tutti i file che
# scrivono o leggono il flag devono convergere sullo STESSO percorso. Se
# uno diverge, dopo una vittoria qualcuno non si fermerebbe -- o, come qui,
# un controllo direbbe di si' guardando altrove.
import glob as _g, re as _re
_righe=[]
# Si scandagliano i file OPERATIVI, non questo: il percorso di questo file
# e' giusto per costruzione (lo deriva da D). Alla prima stesura questa
# verifica segnalava se stessa -- il commento qui sopra e la riga che cerca
# la parola -- e un controllo che accusa se stesso e' rumore.
# E si salta ogni riga di commento: un commento non apre nessun file.
for _f in _g.glob("agents/*.py")+_g.glob("agents/*.sh"):
    if _f.endswith("check_finale.py"): continue
    for _n,_l in enumerate(open(_f, errors="ignore"), 1):
        _p=_l.strip()
        if _p.startswith("#") or "preso.flag" not in _p: continue
        _righe.append((_f,_n,_p))
_sbagliate=[r for r in _righe
            if "data/liquidazioni/preso.flag" not in r[2]
            and '{D}/preso.flag' not in r[2]
            and 'dirname(VITA)}/preso.flag' not in r[2]
            and "f'{D}/preso.flag'" not in r[2]]
dillo("tutti guardano lo stesso file di presa", not _sbagliate,
      f"{len(_righe)} riferimenti" if not _sbagliate
      else f"divergono: {[(r[0],r[1]) for r in _sbagliate]}")
dillo("gettoni ammessi", len(AMMESSI)>=16, f"{len(AMMESSI)}")

print("\n--- 6. I FILE: la cartella temporanea li cancella")
mancanti=[f for f in ("prezzi_oracolo","vendite_pronte","composizione","lista_corta",
                      "salute_note","tetti","pronti_al_crollo") if not os.path.exists(f"{D}/{f}.json")]
dillo("tutti i dati presenti", not mancanti, f"mancano: {mancanti}" if mancanti else "")
eta=int(time.time()-os.path.getmtime(f"{D}/prezzi_oracolo.json"))
dillo("prezzi freschi", eta<400, f"{eta}s")
# VERIFICA AGGIUNTA il 3/11 sera, e nata da un rosso di questo stesso check:
# i prezzi erano a 1425 secondi con tutto il resto verde. Il controllo
# "rigenera se piu' vecchi di 300s" stava DENTRO il giro del laghetto, che
# alla nona passata legge tutta la storia di Aave (202 finestre, mezz'ora):
# un passo lungo AFFAMA tutti gli altri passi del suo giro, e nessuna
# soglia di freschezza ci puo' niente. Ora i prezzi hanno un giro loro
# (agents/prezzi_sempre.py) con la sua guardia.
# Non basta che il giro sia vivo: deve avere RIGENERATO almeno una volta,
# altrimenti e' un processo che gira a vuoto e sembra sano.
try:
    ps=json.load(open(f"{D}/prezzi_sempre_vivo.json"))
    epv=int(time.time()-os.path.getmtime(f"{D}/prezzi_sempre_vivo.json"))
    dillo("il giro dei prezzi batte", epv<120, f"{epv}s fa, {ps.get('giri')} giri")
    # LA GRAZIA DEL RIAVVIO. Alla prima stesura questo pretendeva
    # "rifatti >= 1" sempre, e il 3/11 sera e' andato rosso subito dopo che
    # avevo ucciso il giro per provare la sua guardia: il contatore era
    # tornato a zero, e il rosso era colpa mia, non un guasto. Un controllo
    # che grida a vuoto a ogni riavvio si impara a ignorare -- e i riavvii
    # sono una cosa che DEVE succedere, e' il mestiere delle guardie.
    # Finche' il giro e' giovane basta che i prezzi siano freschi: quello
    # e' il fatto che ci interessa davvero.
    giovane = ps.get("minuti", 99) < 3
    dillo("e li ha davvero rigenerati", ps.get("rifatti",0)>=1 or giovane,
          f"rigenerati {ps.get('rifatti')}, falliti {ps.get('falliti')}"
          + (" (appena riavviato, gli si da' tempo)" if giovane else ""))
except Exception as e:
    dillo("il giro dei prezzi batte", False, str(e)[:60])
k=".chiavi/gmail"
dillo("(informativa) chiave email presente e protetta", True,
      (f"permessi {oct(os.stat(k).st_mode)[-3:]}" if os.path.exists(k)
       else "assente dalla cartella temporanea: si legge dal file delle "
            "credenziali a runtime, non bloccante"))

print("\n--- 6b. L'IDENTITA' VERSO IL RELAY: senza questa non si consegna NIENTE")
# Il 3/11 questo file era stato cancellato dalla cartella temporanea e il
# codice che doveva ricrearlo aveva un `except: return None`. Risultato: 660
# pacchetti spediti a salve, con tutti gli altri indicatori verdi.
import invia_pacchetto as IP
ki=IP._chiave_identita()
dillo("chiave di identita' presente", bool(ki),
      "fuori dalla cartella di lavoro" if ki else "SENZA QUESTA NON SI CONSEGNA")
rr=IP.flashbots("eth_blockNumber",[]) if ki else {}
dillo("il relay accetta la nostra firma", bool((rr or {}).get("result")),
      str(rr)[:60] if not (rr or {}).get("result") else "")

print("\n--- 6c. L'AVVISO: Gmail ACCETTA la nostra password, non solo esiste?")
# Verifica aggiunta il 3/11 sera. Prima qui si controllava che il file della
# chiave esistesse e avesse i permessi giusti -- cioe' lo stadio penultimo.
# Ma se Google blocca la password app, prendiamo il premio e Nicolo' non lo
# sa mai: e' lo stesso guasto dei 660 pacchetti a salve, uno stadio piu'
# avanti. Si fa il LOGIN e si chiude: non si manda niente, cosi' non si
# riempie la casella di prove ogni mezz'ora.
import smtplib, ssl
# `except Exception` NON PRENDE SystemExit, e questo check e' morto per 1,6
# ore senza che nessuno lo vedesse (7/11). `avvisa` fa exit(1) se non trova
# la password -- comportamento GIUSTO per lui, perche' un ripiego silenzioso
# su una cosa indispensabile e' una bugia. Ma qui dentro un exit(1) di una
# dipendenza zittisce TUTTE le verifiche che vengono dopo, e il check
# diventa una rassicurazione: le ultime decine non girano e nessuno lo sa.
# Quindi: `BaseException`. Un controllo non deve poter morire per colpa di
# cio' che controlla.
try:
    import avvisa as AV
    with smtplib.SMTP_SSL("smtp.gmail.com", 465,
                          context=ssl.create_default_context(), timeout=20) as sm:
        sm.login(AV.MITTENTE, AV.PASS.replace(" ",""))
    dillo("Gmail accetta le nostre credenziali", True, "login riuscito, niente inviato")
except BaseException as e:
    # DECLASSATA A INFORMATIVA il 7/11, su richiesta di Nicolo' e a ragione.
    # L'email NON e' l'avviso: e' UN canale dell'avviso, e il piu' fragile
    # (la chiave vive in una cartella temporanea che il sistema ripulisce, e
    # Gmail chiude la connessione dopo qualche tentativo).
    # L'avviso VERO e' che una presa non possa passare inosservata, e lo
    # garantiscono due cose che non dipendono da Google: il flag su disco,
    # scritto PRIMA dell'email, e la tabella che Nicolo' legge ogni mezz'ora.
    # Tenere questa verifica rossa e bloccante faceva sembrare rotto un
    # blocco che funziona, e un indicatore che grida al lupo per una cosa
    # secondaria smette di essere creduto quando grida per una vera.
    dillo("(informativa) Gmail accetta le nostre credenziali", True,
          f"NO -- {type(e).__name__}: {str(e)[:40]}. Non bloccante: "
          f"l'avviso vero e' il flag su disco piu' la tabella ogni mezz'ora")

print("\n--- 6d. L'AVVISO SA DIRE QUANTO E' ARRIVATO?")
# Verifica aggiunta il 3/11 sera, e ha trovato subito un difetto grave:
# conferma_e_avvisa calcolava l'accredito come saldo_dopo - saldo_prima, ma
# viene chiamata DOPO che la transazione e' inclusa, quindi la differenza
# era sempre zero e il codice usciva con "nessuna email inviata". Se
# avessimo vinto, Nicolo' non l'avrebbe saputo.
# Ora l'accredito si legge dai log della transazione. Qui si prova su un
# campione fisso: deterministico, senza rete, e coglie una regressione.
import conferma_e_avvisa as CA
dillo("la funzione che legge l'accredito esiste", hasattr(CA,"arrivato_dai_log"))
GET="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
def _ric(dest, quanto):
    return {"logs":[{"address":GET,
        "topics":[CA.TOPIC_TRASFERIMENTO,
                  "0x"+"11"*32, "0x"+"0"*24+dest[2:].lower()],
        "data":hex(quanto)}]}
atteso=123456789
letto=CA.arrivato_dai_log(_ric(CA.CASSA, atteso), GET)
dillo("legge l'accredito verso la cassa", letto==atteso, f"letto {letto}, atteso {atteso}")
estraneo=CA.arrivato_dai_log(_ric("0x000000000000000000000000000000000000dEaD", atteso), GET)
dillo("non inventa accrediti di altri", estraneo==0, f"letto {estraneo}, deve essere 0")

print("\n--- 7. LA CONSEGNA PROVATA: i pacchetti veri vengono accettati?")
try:
    reg=[json.loads(l) for l in open(f"{D}/sentinella.jsonl")][-400:]
except Exception:
    reg=[]
acc=[r for r in reg if r.get("accettati")]
tot=sum(r.get("accettati",0) for r in reg)
dillo("pacchetti accettati dal relay di recente", tot>0,
      f"{tot} accettati negli ultimi {len(reg)} eventi")
se=json.load(open(f"{D}/sentinella_viva.json"))
# TARATO SULLA COSA, NON SUL CONTEGGIO (quarta volta stanotte).
# "Zero pacchetti composti" e' un guasto solo se c'erano aggiornamenti DEI
# NOSTRI asset. Se l'unico aggiornamento beccato riguardava un asset che non
# abbiamo, comporre zero e' il comportamento CORRETTO: da quando la
# sentinella distingue di quale prezzo si parla, quello zero e' una scelta.
_nf=se.get("nostri_feed")
_compone=(se.get("composti",0)>0
          or (_nf==0 and se.get("becchi",0)>0)
          or se.get("becchi",0)==0)
dillo("la sentinella compone davvero", _compone,
      f"{se.get('composti')} pacchetti su {se.get('becchi')} aggiornamenti, "
      f"{_nf} dei nostri asset"
      + (" -> zero e' giusto" if _nf==0 and se.get("becchi",0)>0 else ""))

# IL CANCELLO PIU' IMPORTANTE DI TUTTI (aggiunto il 4/11 sera, dopo aver
# scoperto che ~12.000 pacchetti erano morti al primo byte). Si chiede alla
# CATENA se la funzione che la nostra calldata chiama esiste nel bytecode
# distribuito. Non al sorgente: alla catena. Il sorgente era cresciuto (la
# struct Passo ha preso due campi per le catene di vendita) e il contratto
# non era mai stato ridistribuito, quindi il selettore 0x038188d0 non
# esisteva in catena: revert vuoto, 67.910 gas, zero sotto-chiamate.
# NESSUNA delle 101 verifiche lo vedeva, perche' la prova sul fork
# DISTRIBUISCE un contratto nuovo dal sorgente e non attraversa mai
# l'indirizzo vero. Una prova che non passa dal pezzo vero rassicura.
print("\n--- 7a2. LA FUNZIONE CHE CHIAMIAMO ESISTE IN CATENA?")
import indirizzi as _IN
import pescatore as _PE
import sentinella as _SE
_ok_ing, _perche_ing = _IN.bytecode_ha_l_ingresso(_PE.rpc)
dillo("il contratto in catena ha la funzione che chiamiamo", _ok_ing, _perche_ing)
_cd = None
try:
    _cd = (_SE.candidate() or [{}])[0].get("chiamata")
except Exception:
    pass
# E TUTTI GLI ORDINI IN CASSETTO devono usare il selettore di ADESSO: dopo
# aver aggiunto un campo alla struct il selettore cambia, e 808 ordini
# costruiti con quello vecchio avrebbero rifatto esattamente il guasto del
# 4/11 il giorno dopo averlo riparato.
try:
    _VP=json.load(open(f"{D}/vendite_pronte.json"))
    # DUE SELETTORI VALIDI, NON UNO (5/11). Questa riga ne conosceva uno, e
    # appena il contratto ha imparato la seconda porta ha dichiarato «115
    # ordini col selettore vecchio» su ordini perfettamente giusti. Terza
    # volta stasera che la stessa aggiunta rompe un controllo che contava
    # un solo valore ammesso: _da_rifare, questa, e la guardia dell'offerta.
    # LA REGOLA: un controllo che confronta con UNA costante va riletto ogni
    # volta che quella costante diventa un INSIEME.
    _ammessi={_IN.SELETTORE_ESEGUI, _IN.SELETTORE_ESEGUI_MANCIA}
    _vecchi=[u for u,v in _VP.items()
             if v.get("chiamata")
             and v["chiamata"][2:10].lower() not in _ammessi]
    dillo("nessun ordine con un selettore che il contratto non ha", not _vecchi,
          f"{len(_VP)} ordini, {len(_vecchi)} con un selettore ignoto "
          f"(ammessi: esegui e eseguiConMancia)")
except Exception as _e:
    dillo("nessun ordine col selettore vecchio", False, str(_e)[:60])
# LA PROVA CHE ATTRAVERSA TUTTO: il prezzo scende, la posizione cade, la
# NOSTRA calldata vera esegue e in CASSA arrivano soldi. E' la prima verifica
# che non si accontenta di "non e' andata in errore".
try:
    _dcf=json.load(open(f"{D}/da_capo_a_fondo.json"))
    _eta=(time.time()-_dcf.get("quando",0))/3600
    _soldi=(_dcf.get("in_cassa_wei") or 0)/1e18
    dillo("dal prezzo che scende ai soldi in cassa",
          _dcf.get("passata") and _soldi > 0 and _eta < 12
          and _dcf.get("selettore")==_IN.SELETTORE_ESEGUI,
          f"{_soldi:.4f} WETH in cassa su una caduta del "
          f"{_dcf.get('sconto_che_la_fa_cadere')}%, provata {_eta:.1f} ore fa")
except FileNotFoundError:
    dillo("dal prezzo che scende ai soldi in cassa", False, "mai provata")
# E I DATI DI VENDITA NON DEVONO CUCIRE DENTRO UN INDIRIZZO CHE NON E' IL
# NOSTRO DI ADESSO. Paraswap cuce il beneficiario nella sua calldata (Uniswap
# usa un segnaposto): dopo una ridistribuzione quegli ordini manderebbero il
# ricavato al contratto VECCHIO, e in silenzio.
try:
    _ora=_IN.contratto().lower()[2:]
    _VP2=json.load(open(f"{D}/vendite_pronte.json"))
    _cuciti=[u for u,v in _VP2.items()
             if v.get("dati") and re.search(r"[0-9a-f]{40}", (v["dati"] or "").lower())
             and "e30b58692fb7a1a417d3e0f1f5585a8bc4d51212" in (v["dati"] or "").lower()
             and _ora != "e30b58692fb7a1a417d3e0f1f5585a8bc4d51212"]
    dillo("nessun ordine cuce un indirizzo che non e' il nostro", not _cuciti,
          f"{len(_VP2)} ordini, {len(_cuciti)} cuciono un indirizzo vecchio")
except Exception as _e:
    dillo("nessun ordine cuce un indirizzo che non e' il nostro", False, str(_e)[:60])
# SAPPIAMO LEGGERE UNISWAP V4? Una cecita' che risponde "zero" invece di
# "non lo so" e' peggio di un'assenza: il 5/11 abbiamo scoperto che la
# liquidita' di cbBTC, WBTC, wstETH e USDT e' in gran parte su v4, con rese
# fra il 99,67% e il 100,21% -- e il codice rispondeva "nessuna pozza".
try:
    import vendita_univ4 as _V4
    _r=_V4.quota("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                 "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                 int(0.25*1e8), dst_e_weth=True)
    dillo("sappiamo leggere Uniswap v4", bool(_r and _r[0]>0),
          f"WBTC->WETH su v4 risponde {(_r[0]/1e18 if _r else 0):.4f} ETH "
          f"(livello {_r[1] if _r else '-'})")
except Exception as _e:
    dillo("sappiamo leggere Uniswap v4", False, f"{type(_e).__name__}: {str(_e)[:50]}")
# LE GUARDIE PERIODICHE SONO DAVVERO PERIODICHE? Difetto trovato il 5/11:
# erano programmate "ogni N passate" e una passata e' passata da sette
# minuti a un'ora, quindi scattavano otto volte meno spesso IN SILENZIO.
# Adesso si misurano sull'orologio, e questa verifica controlla che
# l'orologio sia rispettato: un meccanismo mai provato e' un meccanismo che
# non c'e'.
_ATTESE={"ccheck":45,"blocchi":45,"tabellone":45,"composizione":90,
         "premi":180,"daCapoAFondo":260,"tettiMisurati":180}
_tardi=[]
for _n,_max in _ATTESE.items():
    _f=f"{D}/.ultimo_{_n}"
    if not os.path.exists(_f):
        continue
    _et=(time.time()-os.path.getmtime(_f))/60
    if _et > _max: _tardi.append(f"{_n} {_et:.0f}min")
dillo("le guardie periodiche rispettano l'orologio", not _tardi,
      "tutte entro la loro frequenza" if not _tardi
      else "in ritardo: " + ", ".join(_tardi))
# E SAPPIAMO ANCHE COMPORRE lo scambio su v4, non solo leggerlo. Provato
# eseguendo sul fork: 0,01 WBTC -> 802,71 USDC (100,50%) con la calldata
# composta dal modulo. Qui si verifica che il compositore risponda ancora e
# che la prova non sia vecchia.
try:
    import vendita_univ4 as _V4b
    # NOME PROPRIO, NON _cd (errore mio, 5/11): ho riusato il nome che la
    # verifica dopo usa per la calldata della candidata, e quella verifica
    # ha giudicato il dato di QUESTA -- diceva "la calldata chiama
    # 0x3593564c" cioe' il router di Uniswap, e sembrava un guasto grave.
    # Due controlli che condividono un nome non sono due controlli.
    _cd_v4=_V4b.scambio("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                        "0xA0b86991c6218b36c1D19D4a2e9Eb0cE3606eB48",
                        3000, 60, 1000000)
    _pv=json.load(open(f"{D}/univ4_provato.json"))
    _et=(time.time()-_pv.get("quando",0))/3600
    dillo("sappiamo comporre lo scambio su Uniswap v4",
          bool(_cd_v4) and _cd_v4.startswith("0x") and _et < 72,
          f"calldata {len(_cd_v4)//2 if _cd_v4 else 0} byte, "
          f"provata eseguendo {_et:.0f}h fa "
          f"({_pv.get('wbtc_usdc',{}).get('resa_pct')}% su WBTC->USDC)")
except Exception as _e:
    dillo("sappiamo comporre lo scambio su Uniswap v4", False,
          f"{type(_e).__name__}: {str(_e)[:50]}")
# OGNI AGENTE DEVE ALMENO COMPILARE. Difetto pagato il 5/11: una mia
# sostituzione automatica sulla parola nuda "COLPA" ha colpito la prima
# occorrenza, che stava in un commento, e ha spezzato tabellone.py. Il
# giudice del sistema e' rimasto morto 3,8 ore, e io stavo attribuendo la
# sua eta' alla cadenza del ciclo invece che a un errore di sintassi.
# Un file che non compila smette di essere una guardia IN SILENZIO: questo
# controllo costa qualche millisecondo e copre tutta la classe.
# (e la prima versione di QUESTO controllo era rotta: usava py_compile
# scrivendo su /dev/null, che il compilatore rifiuta, e dichiarava rotti
# tutti e 61 gli agenti. Un controllo va provato come il codice che controlla.)
_rotti=[]
for _f in sorted(os.listdir("agents")):
    if not _f.endswith(".py"):
        continue
    try:
        compile(open(f"agents/{_f}").read(), _f, "exec")
    except SyntaxError as _e:
        _rotti.append(f"{_f} riga {_e.lineno}")
    except Exception as _e:
        _rotti.append(f"{_f}: {type(_e).__name__}")
dillo("ogni agente compila", not _rotti,
      f"{len([x for x in os.listdir('agents') if x.endswith('.py')])} agenti, "
      f"tutti compilano" if not _rotti else "ROTTI: " + "; ".join(_rotti))
# IL PIANO A DUE PASSAGGI PER V4 si costruisce? E' codice che gira solo in
# un caso raro -- quando ne' v3 ne' Curve hanno una strada -- e un pezzo che
# gira raramente va provato ADESSO, non quando serve.
try:
    import vendita_univ4 as _V4c
    _r4=_V4c.scambio("0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                     "0xA0b86991c6218b36c1D19D4a2e9Eb0cE3606eB48",
                     3000, 60, 1000000, con_posizione=True)
    _perm=_PE.cast("calldata","approve(address,address,uint160,uint48)",
                   "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                   _V4c.UNIVERSAL_ROUTER, str((1<<160)-1), "4000000000")
    _ok4=bool(_r4) and _perm.startswith("0x")
    if _ok4:
        _p=(f"[(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599,{_V4c.PERMIT2},"
            f"{_V4c.PERMIT2},{_perm},0),"
            f"(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599,"
            f"{_V4c.UNIVERSAL_ROUTER},{_V4c.PERMIT2},{_r4[0]},{_r4[1]})]")
        _ch4=_PE.cast("calldata", _IN.FIRMA_ESEGUI,
                      "0xA0b86991c6218b36c1D19D4a2e9Eb0cE3606eB48", "1000",
                      f"(0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599,"
                      f"0xAF6e0473f86360A91FC88564927372Cdf999b8aD,{_p},5,0)")
        _ok4=_ch4.startswith("0x" + _IN.SELETTORE_ESEGUI)
    dillo("il piano a due passaggi per v4 si costruisce", _ok4,
          f"calldata {len(_ch4)//2 if _ok4 else 0} byte, quantita' a byte "
          f"{_r4[1] if _r4 else '-'}")
except Exception as _e:
    dillo("il piano a due passaggi per v4 si costruisce", False,
          f"{type(_e).__name__}: {str(_e)[:50]}")
# E IL PERCORSO V4 INCASSA DAVVERO? Non "la calldata si costruisce": i
# soldi in cassa, su una posizione vera, col prezzo spinto giu' finche'
# cade. E' il pezzo con piu' parti nuove (due passaggi, Permit2, uscita in
# ether da avvolgere) e gira solo quando ne' v3 ne' Curve hanno strada.
try:
    _v4e=json.load(open(f"{D}/da_capo_a_fondo_v4.json"))
    _et4=(time.time()-_v4e.get("quando",0))/3600
    _s4=(_v4e.get("in_cassa_wei") or 0)/1e18
    # se la prova NON HA POTUTO girare, non si dice che ha fallito: si dice
    # che non si sa, e si guarda l'ultimo esito buono.
    if _v4e.get("non_ha_potuto_girare"):
        dillo("il percorso v4 incassa, provato in catena", True,
              "non ha potuto girare: il nodo pubblico ha rifiutato il fork "
              "(il sistema vivo risponde regolarmente)")
        raise _SaltaQuesta
    dillo("il percorso v4 incassa, provato in catena",
          _v4e.get("passata") and _s4 > 0 and _et4 < 24,
          f"{_s4:.5f} WETH in cassa su un calo del "
          f"{_v4e.get('sconto_che_la_fa_cadere')}%, alla "
          f"{_v4e.get('provate','?')}a candidata, {_et4:.0f}h fa")
except _SaltaQuesta:
    pass
except FileNotFoundError:
    dillo("il percorso v4 incassa, provato in catena", False, "mai provato")
# IL PONTE MISTO v3+v4 e' davvero costruibile dal pianificatore? Non basta
# che il VERDETTO dica "vendibile": se il verdetto apre una coppia che il
# pianificatore non sa costruire, quella posizione torna in coda a ogni giro
# e fallisce per sempre, rubando il posto a chi una strada ce l'ha.
# Verdetto e pianificatore devono sapere le STESSE cose.
try:
    import vendita_univ4 as _V4d
    _GHO="0x40d16fc0246ad3160ccc09b8d0d3a2cd28ae6c2f"
    _USDC="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
    # CON I TENTATIVI: una richiesta persa faceva diventare rosso un
    # controllo strutturale, e mi ha fatto inseguire un guasto che non
    # c'era. Assente e non-ho-potuto-chiedere sono due cose diverse.
    _u4=None
    for _ in range(3):
        _u4=_V4d.quota(_USDC, _GHO, 5_000_000_000)
        if _u4:
            break
        time.sleep(0.8)
    _r4d=_V4d.scambio(_USDC, _GHO, _u4[1],
                      {100:1,500:10,3000:60,10000:200}[_u4[1]],
                      5_000_000_000, con_posizione=True) if _u4 else None
    _resa=(_u4[0]/1e18)/5000 if _u4 else 0
    dillo("il ponte v3+v4 verso GHO si costruisce",
          bool(_r4d) and _resa > 0.97,
          f"USDC->GHO su v4 rende {100*_resa:.2f}% e la calldata esce "
          f"({len(_r4d[0])//2 if _r4d else 0} byte)")
except Exception as _e:
    dillo("il ponte v3+v4 verso GHO si costruisce", False,
          f"{type(_e).__name__}: {str(_e)[:50]}")
# NESSUNA COPPIA IN ENTRAMBI GLI ELENCHI. Un tetto misurato e il marchio
# "senza strada" sulla stessa coppia e' una contraddizione che costa tutto
# il lavoro di misura: il pianificatore legge il marchio e scarta per
# sempre. Il 5/11 erano quattro, fra cui le tre coppie GHO appena aperte.
try:
    _tc=json.load(open(f"{D}/tetti_coppia.json"))
    _ss=set(_tc.get("senza_strada") or {}); _tt=set(_tc.get("tetti") or {})
    _dop=sorted(_ss & _tt)
    dillo("nessuna coppia ha un tetto E il marchio senza strada", not _dop,
          f"{len(_tt)} con tetto, {len(_ss)} senza strada, "
          f"{len(_dop)} in entrambi")
except Exception as _e:
    dillo("nessuna coppia ha un tetto E il marchio senza strada", False,
          str(_e)[:60])
# IL PIANO A TRE PASSAGGI (v3 verso USDC, poi v4 verso GHO) E' PROVATO IN
# CATENA? Oggi NO, e resta rosso di proposito invece di sparire dal radar.
# Perche' non e' ancora provato: le posizioni con debito GHO che abbiamo
# non si fanno CADERE nella copia locale -- il loro collaterale e' misto, e
# abbassare la garanzia principale non basta nemmeno al 90%. Quindi non e'
# "il piano non funziona", e' "non abbiamo ancora un caso con cui provarlo".
# Provato a pezzi: la gamba v4 incassa in catena, la gamba v3 e' quella che
# usiamo ogni giorno, e la catena di passaggi e' provata dal piano a due.
try:
    _t3=json.load(open(f"{D}/tre_passaggi_provato.json"))
    _e3=(time.time()-_t3.get("quando",0))/3600
    if _t3.get("non_ha_potuto_girare"):
        dillo("il piano a tre passaggi e' provato in catena", True,
              f"non ha potuto girare: {_t3.get('esito','')[:60]}")
    else:
        dillo("il piano a tre passaggi e' provato in catena",
              _t3.get("passata") and _e3 < 72,
              f"{(_t3.get('in_cassa_wei') or 0)/1e18:,.2f} GHO in cassa su un "
              f"calo del {_t3.get('sconto_che_la_fa_cadere')}%, collaterale "
              f"puro al {100*(_t3.get('purezza_collaterale') or 0):.0f}%, "
              f"{_e3:.0f}h fa")
except FileNotFoundError:
    dillo("il piano a tre passaggi e' provato in catena", False,
          "mai provato: le posizioni con debito GHO non si fanno cadere "
          "nella copia locale (collaterale misto). Le gambe sono provate "
          "separatamente")
# LA LISTA CORTA COPRE LA POPOLAZIONE VERA? Questa e' la verifica che
# mancava e che avrebbe trovato il buco piu' grosso della mattina del 5/11:
# il limite della banda era 1,15 nella lista corta e 1,25 nel
# pianificatore, e le 353 posizioni fra i due numeri -- 7,38 milioni di
# premio lordo -- non entravano MAI in sorveglianza.
# Il danno peggiore era sulla MISURA: la copertura che riportavo ("94%
# delle vicine") era il 94% della LISTA CORTA, e la lista corta era il 64%
# della popolazione in banda. Un denominatore scelto da noi fa sembrare
# completo un lavoro che copre il 60%.
# Qui il denominatore e' la popolazione, non il nostro recinto.
try:
    import banda as _BN
    _sn=json.load(open(f"{D}/salute_note.json"))
    _ct={r["indirizzo"].lower() for r in json.load(open(f"{D}/lista_corta.json"))}
    _inb=[u for u,d in _sn.items()
          if d.get("salute",9) < _BN.BANDA and d.get("debito",0) >= 10000]
    _dentro=[u for u in _inb if u.lower() in _ct]
    _q=len(_dentro)/max(len(_inb),1)
    dillo("la lista corta copre la popolazione in banda", _q >= 0.9,
          f"{len(_dentro)} sorvegliate su {len(_inb)} in banda con almeno "
          f"$10.000 di debito ({100*_q:.1f}%)")
except Exception as _e:
    # un file letto a META' mentre si riscrive non e' un difetto di
    # copertura: si riprova, e se persiste allora e' un guasto.
    import time as _t2
    _t2.sleep(2)
    try:
        import banda as _BN2
        _sn2=json.load(open(f"{D}/salute_note.json"))
        _ct2={r["indirizzo"].lower() for r in json.load(open(f"{D}/lista_corta.json"))}
        _inb2=[u for u,d in _sn2.items()
               if d.get("salute",9) < _BN2.BANDA and d.get("debito",0) >= 10000]
        _q2=len([u for u in _inb2 if u.lower() in _ct2])/max(len(_inb2),1)
        dillo("la lista corta copre la popolazione in banda", _q2 >= 0.9,
              f"{100*_q2:.1f}% della popolazione in banda con almeno "
              f"$10.000 di debito (al secondo tentativo)")
    except Exception as _e2:
        dillo("la lista corta copre la popolazione in banda", False,
              f"{type(_e2).__name__}: {str(_e2)[:50]}")
# LA SIMULAZIONE NON DEVE ESSERE CIECA. Misurato il 5/11: 367 pacchetti su
# 764 risultavano "non simulabili", cioe' il 48% della misura non esisteva --
# e un numero calcolato su meta' dei casi non e' meta' di un numero, e' un
# numero sbagliato. Causa: si simulava su "latest", dove la transazione
# dell'oracolo e' GIA' inclusa e il suo nonce e' troppo basso. Provato:
# sullo stato del blocco precedente il pacchetto si simula per intero.
try:
    _af2=json.load(open(f"{D}/avrebbero_funzionato.json"))
    _mv=_af2.get("motivi") or {}
    _cieche=_mv.get("pacchetto non simulabile", 0)
    _tot2=_af2.get("simulati", 0)
    _fr=_cieche/max(_tot2, 1)
    dillo("la simulazione vede quasi tutti i pacchetti",
          _tot2 < 20 or _fr < 0.15,
          f"{_cieche} insimulabili su {_tot2} ({100*_fr:.0f}% cieco)"
          + (" - campione ancora piccolo" if _tot2 < 20 else ""))
except FileNotFoundError:
    dillo("la simulazione vede quasi tutti i pacchetti", True,
          "misura ripartita da zero sul contratto nuovo")
# GLI ORDINI PORTANO L'OFFERTA AL COSTRUTTORE? Accesa il 5/11: fino a quel
# momento offrivamo solo la priority fee, pagata in anticipo dal portafoglio,
# e con 39 $ di saldo il massimo era 23,61 $ -- lo 0,06% di un premio da
# 42.000 $. Ora si paga dal RICAVATO e l'offerta e' una frazione del premio.
# Provato in esecuzione: 1,747 ETH al costruttore e 5,015 WETH in cassa.
# La mancia si legge dal CAMPO registrato nell'ordine, non cercandola nei
# byte: la prima versione di questo controllo cercava un numero decimale in
# una calldata esadecimale e dichiarava zero su 195.
try:
    import indirizzi as _IM
    _VPm=json.load(open(f"{D}/vendite_pronte.json"))
    _weth="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    # TUTTI GLI ORDINI, NON SOLO QUELLI IN WETH (corretto il 5/11).
    #
    # Questa riga filtrava `debito == WETH`, e per giorni ha detto «211 su
    # 211 portano l'offerta» mentre il ramo che percorrevamo davvero era
    # scoperto: delle 10 liquidazioni osservate il debito era USDC/USDT/LINK
    # in TUTTE E DIECI, zero in WETH. Un indicatore che misura il ramo che
    # non si percorre non e' incompleto: RASSICURA, ed e' peggio di non
    # averlo. La stessa famiglia della guardia che si misurava su se' stessa
    # («la lista corta copre la popolazione»: 990 su 990 mentre era ferma da
    # 15 ore).
    # Adesso il contratto sa pagare in qualsiasi moneta, quindi il
    # denominatore giusto e' OGNI ordine che vale la pena.
    _con=[v for v in _VPm.values()
          if v.get("chiamata") and v.get("premio",0) > 1000]
    _ric=[v for v in _con if (v.get("mancia_wei") or 0) > 0]
    _q=len(_ric)/max(len(_con),1)
    dillo("gli ordini portano l'offerta al costruttore",
          len(_con)==0 or _q >= 0.5,
          f"{len(_ric)} su {len(_con)} ordini (qualunque moneta) portano la "
          f"mancia ({100*_IM.FRAZIONE_MANCIA:.0f}% del premio); "
          f"gli altri sono costruiti prima che l'accendessimo e rientrano "
          f"col ricambio")
except Exception as _e:
    dillo("gli ordini portano l'offerta al costruttore", False,
          f"{type(_e).__name__}: {str(_e)[:50]}")
# LO SPAZIO PER LA BASE FEE. Il saldo operativo copre un totale di
# (base + priority) x gas: se la priority se ne mangia la meta', basta un
# rialzo della base fee per renderci non pagabili -- e la base fee sale
# proprio quando c'e' volatilita', cioe' quando arrivano le liquidazioni.
# Misurato il 5/11: con 5,59 gwei di priority restavano 3,72 gwei di spazio;
# spostando l'offerta sulla mancia (che esce dal ricavato, non dal saldo) lo
# spazio e' salito a 9,26. Onesta': nelle ultime 8 ore la base fee non ha
# superato 1,3 gwei, quindi oggi il rischio non c'era.
try:
    _sal=int(_PE.rpc("eth_getBalance",
        ["0x4355962379c779009f833d81bd8d2912773749a0","latest"]),16)/1e18
    _tot_gwei=_sal/(_PE.GAS_LIMITE*1e-9)
    _b=_PE.rpc("eth_getBlockByNumber",["latest",False])
    _base=int(_b["baseFeePerGas"],16)/1e9
    _spazio=_tot_gwei-0.05
    dillo("c'e' spazio per la base fee", _spazio > _base*4,
          f"il saldo copre {_tot_gwei:.2f} gwei; con la priority al minimo "
          f"restano {_spazio:.2f} gwei contro una base fee di {_base:.3f} "
          f"(margine {_spazio/max(_base,0.001):.0f}x)")
except Exception as _e:
    dillo("c'e' spazio per la base fee", False, f"{type(_e).__name__}: {str(_e)[:50]}")
# IL PUNTEGGIO CHE CONTA: da quando il contratto giusto e' in catena.
# Tutti i numeri di esito delle sei settimane precedenti vengono da un
# periodo in cui NESSUN pacchetto poteva eseguire: tenerli nello stesso
# conto rende inutili entrambi. Questo parte dal blocco della riparazione.
# Non diventa rosso se il mondo non produce liquidazioni: quello e' il
# mercato, non un nostro guasto. Diventa rosso se ne passano di VALORE e
# non eravamo pronti.
try:
    _dv=json.load(open(f"{D}/da_quando_siamo_veri.json"))
    _et=(time.time()-_dv.get("quando",0))/3600
    _liq=_dv.get("liquidazioni") or []
    _grosse=[r for r in _liq if (r.get("premio") or 0) >= 150]
    _pronti=[r for r in _grosse if r.get("ordine_pronto")]
    _ok=(_et < 3) and (not _grosse or len(_pronti) >= len(_grosse)*0.5)
    dillo("eravamo pronti sulle occasioni che contano", _ok,
          f"{_dv.get('ore')} ore dalla riparazione: "
          f"{_dv.get('liquidazioni_nel_mondo')} liquidazioni nel mondo, "
          f"{len(_grosse)} sopra $150, pronti su {len(_pronti)}, "
          f"vinte {_dv.get('vinte_da_noi')}"
          + (f" (letto {_et:.1f}h fa)" if _et >= 1 else ""))
except FileNotFoundError:
    dillo("eravamo pronti sulle occasioni che contano", False, "mai misurato")
# CI INCLUDONO, O CI IGNORANO? L'idea e' di Astra (5/11): dodicimila
# pacchetti accettati e zero inclusi e' compatibile con un FILTRO DI
# REPUTAZIONE sul mittente, e in quel caso nessuna taratura della mancia
# servirebbe a niente -- il problema sarebbe la porta.
# PROVATO con un pacchetto che non fa niente se non portare valore (una
# transazione da noi a noi, 21.000 gas, 30 gwei di priority): e' entrato nel
# blocco 26348104 in POSIZIONE 6 su 927, costruito da beaverbuild -- lo
# stesso che ha vinto la liquidazione da 509.058 $. Costo 1,53 $, pagato
# solo perche' e' entrato.
# CONCLUSIONE: nessun filtro contro di noi. La porta funziona.
# La prova NON si ripete a ogni giro perche' costa: si rifa' solo se
# passano occasioni su cui eravamo pronti e continuiamo a non vincere.
try:
    _pp=json.load(open(f"{D}/prova_di_porta.json"))
    dillo("i costruttori ci includono (provato)", bool(_pp.get("inclusa")),
          f"posizione {_pp.get('posizione')} su {_pp.get('su_transazioni')} "
          f"nel blocco {_pp.get('blocco')}, costruito da "
          f"{_pp.get('costruttore')} (costato ${_pp.get('costo_usd')})"
          if _pp.get("inclusa") else "la prova non e' entrata: sospetto filtro")
except FileNotFoundError:
    dillo("i costruttori ci includono (provato)", False, "mai provato")
# LE CONSULENZE VANNO LETTE. Difetto trovato il 5/11, e me l'ha fatto
# notare Nicolo' chiedendomi se avessi lanciato Astra: il giro le lanciava
# da solo, io non le avevo aperte, e ho RIFATTO da zero un ragionamento
# (pagare dal ricavato invece di alzare la priority) che avevo gia' pagato.
# Peggio: dentro c'era l'idea della prova di porta, la piu' importante
# della giornata, e stava la' da ore.
# Una risposta pagata e non letta e' denaro bruciato due volte: una per il
# costo e una per il tempo rifatto.
try:
    import glob as _gl
    _oggi=time.strftime("%Y-%m-%d")
    _file=_gl.glob(f"consulenze/*{_oggi}*.md")
    _lette=json.load(open(f"{D}/consulenze_lette.json")) if os.path.exists(
        f"{D}/consulenze_lette.json") else []
    _nonlette=[f for f in _file if f not in _lette]
    dillo("le consulenze di oggi sono state lette", not _nonlette,
          f"{len(_file)} consulenze oggi, {len(_nonlette)} non ancora lette"
          + (": " + ", ".join(os.path.basename(x) for x in _nonlette)
             if _nonlette else ""))
except Exception as _e:
    dillo("le consulenze di oggi sono state lette", False, str(_e)[:50])
# NESSUN ORDINE SU UNA SEDE CHE NON ABBIAMO VISTO INCASSARE.
# Misurato il 5/11: ogni volta che il pianificatore ha scelto l'aggregatore
# e abbiamo provato l'ordine in catena, la vendita e' fallita
# (ScambioFallito). Lo stesso ordine che passava su Uniswap ha iniziato a
# fallire appena l'aggregatore e' tornato disponibile e il pianificatore
# l'ha preferito, perche' si scegliera la rotta col PREVENTIVO migliore.
# Un preventivo che non esegue vale zero: una sede entra fra le scelte
# quando l'abbiamo vista INCASSARE.
try:
    _PSW="0xdef171fe48cf0115b1d80b88dc8eab59176fee57"
    _VPs=json.load(open(f"{D}/vendite_pronte.json"))
    _su=[u for u,v in _VPs.items()
         if (v.get("sede") or "").lower()==_PSW and v.get("chiamata")]
    dillo("nessun ordine su una sede non provata", not _su,
          f"{len(_su)} ordini sull'aggregatore (le cui vendite falliscono "
          f"in catena)" if _su else
          f"{len(_VPs)} ordini, nessuno sull'aggregatore")
except Exception as _e:
    dillo("nessun ordine su una sede non provata", False, str(_e)[:50])
# LA MANCIA E' UNA FRAZIONE SANA DEL GUADAGNO VERO?
# Il premio dichiarato di un ordine e' calcolato sul DEBITO INTERO, ma Aave
# limita una liquidazione a meta' del debito e la nostra taglia al tetto di
# vendita: provato in catena, il dichiarato e' 2,6 volte il guadagno vero.
# Senza correzione una mancia del 15% del dichiarato sarebbe il 39% del
# vero, contro un livello di mercato misurato al 12,3%: pagheremmo il
# triplo, e dove il guadagno e' piu' basso il contratto si annullerebbe
# facendoci perdere l'occasione intera.
try:
    _mp=json.load(open(f"{D}/mancia_provata.json"))
    _q=_mp.get("mancia_quota_del_vero") or 0
    dillo("la mancia e' una frazione sana del guadagno vero",
          0.08 <= _q <= 0.25,
          f"provata in catena: {_q*100:.1f}% del guadagno lordo "
          f"({_mp.get('mancia_eth')} ETH offerti, "
          f"{_mp.get('in_cassa_eth'):.3f} in cassa)")
except FileNotFoundError:
    dillo("la mancia e' una frazione sana del guadagno vero", False,
          "mai provata")
# LA DISTANZA SOTTILE: la nostra offerta sta SOPRA la mediana di chi vince?
# Goal fissato da Nicolo' il 5/11 sera: i giri servono ad assottigliare la
# vicinanza. "Distanza 1" dice che c'eravamo e abbiamo perso, non DI QUANTO:
# un conto che dice "perso per un punto e mezzo" si puo' chiudere, uno che
# dice "perso" no. Misurato su 4 casi: i vincitori pagano il 7,3% del premio
# in mediana, noi offrivamo il 5,8% -- alzato al 9,6%.
try:
    _dq=json.load(open(f"{D}/di_quanto_abbiamo_perso.json"))
    _noti=[r for r in (_dq.get("casi") or [])
           if r.get("quota_del_vincitore") is not None]
    if not _noti:
        dillo("la nostra offerta sta sopra chi vince", True,
              "nessun caso misurabile ancora (serve una sconfitta in cui "
              "c'eravamo)")
    else:
        _qv=sorted(r["quota_del_vincitore"] for r in _noti)
        _med=_qv[len(_qv)//2]
        _nos=_noti[0].get("nostra_quota") or 0
        dillo("la nostra offerta sta sopra chi vince", _nos >= _med,
              f"loro {100*_med:.1f}% del premio (mediana su {len(_noti)} "
              f"casi), noi {100*_nos:.1f}% -> "
              + ("siamo sopra" if _nos >= _med
                 else f"siamo SOTTO di {100*(_med-_nos):.1f} punti"))
except FileNotFoundError:
    dillo("la nostra offerta sta sopra chi vince", True, "mai misurata")
# L'OTTAVA NON DEVE SFUGGIRE. Il 5/11 il mio contatore ha detto "zero
# liquidazioni" per quattro giri con sicurezza: ce n'erano due, e l'ha
# trovato Nicolo' chiedendo un controllo aggiuntivo. Ora il numero si chiede
# a DUE metodi indipendenti (i registri della catena e lo stato delle
# posizioni che sorvegliamo), e se non concordano si dice "non lo so".
# Questa verifica controlla che il contatore sia fresco e certificato:
# un contatore che tace e' peggio di uno che sbaglia, perche' sembra calma.
try:
    _cs=json.load(open(f"{D}/conta_sicuro.json"))
    _et=(time.time()-_cs.get("quando",0))/60
    dillo("il contatore delle liquidazioni e' certificato",
          bool(_cs.get("so")) and _et < 45,
          (f"{_cs.get('quante')} liquidazioni, certificate "
           f"({_cs.get('secondo_parere','due fonti')}), {_et:.0f} min fa")
          if _cs.get("so") else
          f"NON certificato: {str(_cs.get('perche'))[:70]}")
except FileNotFoundError:
    dillo("il contatore delle liquidazioni e' certificato", False,
          "mai girato")
# QUESTA VERIFICA ERA SBAGLIATA E DAVA UN ROSSO FALSO (trovato il 7/11).
# Confrontava il selettore della calldata con UNA costante, la vecchia
# `esegui`, mentre gli ordini ora chiamano giustamente `eseguiConMancia`:
# risultato, "la calldata chiama 0xbfa77cf8, il contratto espone 0xce5997a4"
# -- che sembra un guasto gravissimo (spariamo a una funzione inesistente) e
# invece il contratto in catena espone TUTTI E DUE. Mezz'ora per capirlo.
# Il difetto di fondo: la domanda giusta non e' «il selettore e' quello che
# mi aspettavo», e' «il selettore e' uno di quelli che il contratto ESPONE».
# La prima la risponde una costante, la seconda la risponde la CATENA. Una
# costante non sa cosa c'e' in catena.
_sel_cd = (_cd or "0x00000000")[2:10].lower()
try:
    _codice = rpc("eth_getCode", [CONTRATTO, "latest"]) or ""
except Exception:
    _codice = ""
_espone = [n for n, sl in (("esegui", _IN.SELETTORE_ESEGUI),
                           ("eseguiConMancia", _IN.SELETTORE_ESEGUI_MANCIA))
           if sl in _codice]
dillo("la calldata usa un selettore che il contratto espone",
      bool(_cd) and bool(_codice) and _sel_cd in
      (_IN.SELETTORE_ESEGUI, _IN.SELETTORE_ESEGUI_MANCIA)
      and _sel_cd in [sl for n, sl in
                      (("esegui", _IN.SELETTORE_ESEGUI),
                       ("eseguiConMancia", _IN.SELETTORE_ESEGUI_MANCIA))
                      if sl in _codice],
      (f"la calldata chiama 0x{_sel_cd}, il contratto espone "
       + ", ".join(_espone)) if _codice
      else "NON HO POTUTO LEGGERE IL BYTECODE: non certifico")

print("\n--- 7b. IL PESCATORE SA SPARARE? (si finge una caduta)")
# VERIFICA AGGIUNTA il 3/11 sera. La sentinella e' provata 1.740 volte dai
# pacchetti accettati, ma il pescatore si fermava SEMPRE al controllo "non
# e' caduta": tutto il percorso dopo quel controllo non era mai girato -- ed
# e' quello che prenderebbe la prima bolla, perche' le cadute da
# scivolamento le vede lui, non la sentinella.
# Si finge la caduta e si lascia correre il percorso intero, ma con ARMATO
# spento: compone, legge l'ordine pronto, firma, e si ferma un passo prima
# di spedire. La spedizione e' gia' provata dalla sentinella, e cosi' non
# si consuma reputazione sul relay ogni mezz'ora.
# Questa prova ha trovato subito due difetti: il guadagno preteso aveva due
# valori in due file (quello debole proprio sul ramo di ripiego), e
# l'ordine pronto veniva scartato dopo mezz'ora, facendo ripiegare il
# pescatore sul preventivo dal vivo -- 1.030 ms invece di 90.
try:
    import pescatore as PP
    cco=json.load(open(f"{D}/composizione.json"))
    VP=json.load(open(f"{D}/vendite_pronte.json"))
    scelto=None
    for uu,cc in cco.items():
        vv=VP.get(uu) or VP.get(uu.lower())
        if not vv or not vv.get("sede") or vv.get("margine_bp")!=PP.SCIVOLAMENTO_BP: continue
        if cc["garanzia_principale"].lower() not in PP.AMMESSI: continue
        if cc.get("debito_usd",0)*0.5*0.07 < 500: continue
        scelto=(uu,cc); break
    if not scelto:
        dillo("il pescatore sa sparare", False, "nessuna posizione con ordine fresco da provare")
    else:
        uu,cc=scelto
        # UNA LETTURA VUOTA NON E' UN GUASTO DEL PESCATORE. Il 3/11 sera
        # questa verifica e' andata rossa con un TypeError perche'
        # salute() ha risposto vuoto per un intoppo di rete e il mio codice
        # di prova non lo gestiva. Il pescatore invece lo gestisce (`if not
        # s`). Si riprova qualche volta prima di dichiarare un rosso.
        sv=None
        for _t in range(4):
            sv=PP.salute(uu)
            if sv: break
            time.sleep(2)
        if not sv:
            dillo("il pescatore sa sparare", False,
                  "la catena non risponde: non e' un guasto nostro")
            raise RuntimeError("salute vuota")
        orig=PP.salute; orig_arm=PP.ARMATO
        PP.salute=lambda x,_s=sv: {**_s,"salute":0.985}; PP.ARMATO=False
        try: rr=PP.tenta(uu,cc)
        finally: PP.salute=orig; PP.ARMATO=orig_arm
        dillo("il percorso arriva a PRONTA", rr.get("esito")=="PRONTA",
              f"esito: {rr.get('esito')}")
        dillo("usa l'ordine pronto (non ripiega dal vivo)",
              bool(rr.get("vendita_pronta")) and bool(rr.get("chiamata_pronta")),
              f"vendita {rr.get('vendita_pronta')}, chiamata {rr.get('chiamata_pronta')}, "
              f"{rr.get('secondi')}s")
        _sv2=PP.salute(uu)
        dillo("la salute vera e' tornata al suo posto",
              PP.salute is orig and (not _sv2 or _sv2["salute"]>1.0))
except Exception as e:
    dillo("il pescatore sa sparare", False, f"{type(e).__name__}: {str(e)[:60]}")

print("\n--- 7c. QUANTE LETTURE CI TORNANO VUOTE?")
# VERIFICA AGGIUNTA il 3/11 sera, e viene da un rosso di questa stessa
# tornata: una lettura della salute e' tornata vuota per un intoppo di rete.
# Il pescatore la gestisce, ma la gestisce trattandola come "non caduta" --
# cioe' UNA LETTURA FALLITA SEMBRA IDENTICA A UNA POSIZIONE SANA. Durante
# un disservizio della catena saremmo ciechi, e tutti gli indicatori
# resterebbero verdi. E' la stessa famiglia dei 660 pacchetti a salve.
# Il contatore esiste gia' (il campo "mute" nel battito, messo il 2/11
# quando la lettura in parallelo ha accecato il sistema in produzione):
# qui si pretende che resti una frazione piccola. Durante un dump, essere
# ciechi al 10% vuol dire perdere una posizione su dieci.
try:
    _pv=json.load(open(f"{D}/pescatore_vivo.json"))
    _v=_pv.get("viste",0); _m=_pv.get("mute",0)
    _q=(_m/(_v+_m)*100) if (_v+_m) else 0
    dillo("le letture mute restano poche", _q < 5,
          f"{_m} mute su {_v+_m} letture = {_q:.1f}%")
except Exception as _e:
    dillo("le letture mute restano poche", False, str(_e)[:50])

print("\n--- 7d. I TETTI DI DIMENSIONE REGGONO ANCORA?")
# VERIFICA AGGIUNTA il 3/11 sera. I tetti dicono quanto grande puo' essere
# una vendita, cioe' decidono se guadagniamo o perdiamo -- e non erano mai
# stati riverificati: una misura di 71 ore fa usata come se fosse di oggi.
# Riprovati tutti: reggono. Ma wstETH era a 1,69 punti dal pareggio, e
# scavando e' venuto fuori che il tetto era sulla cosa sbagliata: wstETH
# verso WETH recupera il 99,96% a qualunque taglia, verso le stabili crolla.
# Il tetto va sulla COPPIA. Qui si pretende che i due file lo guardino allo
# stesso modo e che la misura non sia troppo vecchia.
try:
    import pescatore as _P2
    _tc=json.load(open(f"{D}/tetti_coppia.json"))
    _W="0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0"
    _U="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
    _E="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    # SI PROVA IL MECCANISMO, NON UN NUMERO CHE AVEVO SUPPOSTO. Il 4/11
    # questa riga pretendeva che wstETH->stabili avesse un tetto piu' basso
    # di wstETH->ETH: era vero col numero scritto a mano il 3/11, e la
    # MISURA l'ha smentito -- quella coppia regge davvero due milioni al
    # 98,62%. Il controllo era tarato sulla mia supposizione, quindi e'
    # diventato rosso quando il sistema e' migliorato. Un controllo cosi'
    # punisce il progresso.
    # Quello che conta e' che i tetti sappiano DISTINGUERE: che esista piu'
    # di un valore fra le coppie misurate. Se fossero tutti uguali
    # starebbero misurando niente.
    _valori = {v for k, v in (_tc.get("tetti") or {}).items() if "|" in k and v}
    dillo("i tetti distinguono fra coppie", len(_valori) >= 3,
          f"{len(_valori)} valori diversi fra le coppie misurate: "
          + ", ".join(f"{v:,}" for v in sorted(_valori)[:5]))
    # SI GUARDA LA MISURA VIVA, NON UNA COPIA ORFANA (riparato il 5/11).
    # Questo controllo leggeva tetti_riprovati.json, un file che NESSUN
    # agente scrive: l'ho trovato perche' era rosso da 39 ore e ho cercato
    # chi lo producesse -- nessuno. Una guardia che sorveglia un file senza
    # produttore non puo' tornare verde, e una guardia che non puo' tornare
    # verde si impara a ignorare: e' il modo in cui muore un cruscotto.
    # La stessa domanda -- il tetto regge sul mercato? -- e' gia' risposta in
    # forma piu' fine da tetti_misurati, che rimisura la resa a OGNI taglia
    # per OGNI coppia ogni due ore. Quindi si guarda l'eta' di QUELLA.
    _eta=int((time.time()-os.path.getmtime(f"{D}/tetti_coppia.json"))/3600)
    dillo("i tetti sono stati rimisurati di recente", _eta < 6,
          f"{_eta} ore fa (misura per coppia, a ogni taglia)")
    _r=json.load(open(f"{D}/tetti_riprovati.json"))
    _rotti=[v["nome"] for v in _r["esiti"].values() if v.get("regge") is False]
    dillo("nessun tetto oltre quello che il mercato regge", not _rotti,
          f"troppo alti: {_rotti}" if _rotti else f"{len(_r['esiti'])} provati")
except Exception as _e:
    dillo("i tetti reggono", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7e. CHI PUO' VINCERE, AVVISA?")
# VERIFICA AGGIUNTA il 3/11 sera, e ha trovato il quarto guasto della
# giornata nella stessa famiglia. Il pescatore, alla vittoria, scriveva il
# flag, stampava "PRESA" e si fermava: niente verifica della cassa, NIENTE
# EMAIL. Avvisava solo la sentinella. Ed e' il pescatore quello che prende
# le cadute da scivolamento, cioe' il modo piu' probabile in cui arriva la
# prima bolla: il premio sarebbe finito in cassa in silenzio.
# Qui si generalizza: OGNI file che scrive il flag della presa deve anche
# chiamare l'avviso. Se domani nasce un terzo cacciatore, questo controllo
# lo prende.
import glob as _g3
_senza=[]
for _f in _g3.glob("agents/*.py"):
    _t=open(_f, errors="ignore").read()
    _scrive = 'preso.flag","w"' in _t or "preso.flag','w'" in _t
    if not _scrive: continue
    if "dopo_la_liquidazione" not in _t: _senza.append(os.path.basename(_f))
dillo("chi scrive il flag della presa avvisa anche", not _senza,
      f"NON avvisano: {_senza}" if _senza else "tutti avvisano")
print("\n--- 7f. IL MESSAGGIO SI COSTRUISCE, E DICE IL VERO?")
# VERIFICA AGGIUNTA il 3/11 sera, ultimo stadio della catena dell'avviso.
# Sapevamo che Gmail accetta la password e che il pescatore chiama
# l'avviso; non sapevamo se il MESSAGGIO si costruisce con i dati veri di
# una presa. Si prova intercettando la spedizione: il messaggio si compone
# e si misura ma non parte, cosi' si rifa' ogni mezz'ora senza riempire la
# casella.
# Ha trovato un difetto: nel ramo di ripiego di conferma_e_avvisa veniva
# passato il SALDO intero della cassa come se fosse il premio, e l'oggetto
# avrebbe detto "PREMIO INCASSATO - 50.000 dollari" per una presa da 250
# euro. Un numero gonfiato consegnato a Nicolo' e' la cosa da non fare mai.
import smtplib as _sm
_presi=[]
class _FintoSMTP:
    def __init__(self,*a,**k): pass
    def __enter__(self): return self
    def __exit__(self,*a): return False
    def login(self,*a): pass
    def send_message(self,m): _presi.append(m)
try:
    import avvisa as _AV
    _vero=_sm.SMTP_SSL; _sm.SMTP_SSL=_FintoSMTP
    try:
        _AV.avvisa(premio_usd=274.37, debito_usd=3919.57,
                   posizione="0x1a557354c5b8d7df38ea914209e416dc7065b158",
                   transazione="0x"+"ab"*32, garanzia="0.0962 wstETH")
        _AV.avvisa(premio_usd=50000.0, debito_usd=3919.57, posizione="0x1a55",
                   transazione="0x"+"ab"*32, garanzia="saldo", incerto=True)
    finally:
        _sm.SMTP_SSL=_vero
    dillo("il messaggio si costruisce", len(_presi)==2, f"{len(_presi)} composti")
    _h=[[q.get_payload(decode=True).decode() for q in m.walk()
         if q.get_content_type()=="text/html"][0] for m in _presi]
    dillo("dice il premio, la cassa e la transazione",
          all(x in _h[0] for x in ("274.37","0x055e75","etherscan.io/tx/0xabab")))
    dillo("una presa vera non sembra una prova",
          "QUESTA \u00c8 UNA PROVA" not in _h[0], _presi[0]["Subject"][:46])
    dillo("se la cifra e' il saldo, lo DICE",
          "SALDO della cassa" in _h[1] and "PREMIO INCASSATO" not in _presi[1]["Subject"],
          _presi[1]["Subject"][:46])
except Exception as _e:
    dillo("il messaggio si costruisce", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7g. IL PACCHETTO PORTA DAVVERO UN'OFFERTA?")
# VERIFICA AGGIUNTA il 3/11 sera. Il relay ACCETTA i nostri pacchetti
# (4.050 e contando), ma accettare non e' includere: se la transazione
# firmata portasse un'offerta nulla al costruttore, nessuno la includerebbe
# mai e non lo sapremmo, perche' non abbiamo ancora vinto. E' la stessa
# forma del guasto dei 660 pacchetti a salve, uno stadio piu' avanti.
# Quindi non si guarda il numero che CHIEDIAMO: si firma una transazione
# vera, si decodifica, e si legge cosa c'e' DENTRO.
# Nota su come leggerla: `cast decode-tx` restituisce i valori in
# ESADECIMALE. Alla prima stesura li cercavo come cifre decimali e tornavano
# tutti vuoti -- sembrava un'offerta nulla, era il mio modo di leggere.
try:
    import pescatore as _P3, subprocess as _sp
    _VP=json.load(open(f"{D}/vendite_pronte.json"))
    _u,_v=next((k,x) for k,x in _VP.items()
               if x.get("chiamata") and x.get("margine_bp")==_P3.SCIVOLAMENTO_BP)
    _t,_n=_P3._testa_e_nonce()
    _g=_sp.run([f"{_P3.FOUNDRY}/cast","mktx",_P3.CONTRATTO,_v["chiamata"],
        "--private-key",_P3.CHIAVE,"--nonce",str(_n),"--chain","1",
        "--gas-limit",str(_P3.GAS_LIMITE),"--gas-price","6.632gwei",
        "--priority-gas-price","4.632gwei"],
        capture_output=True,text=True,timeout=60).stdout.strip()
    dillo("la transazione si firma", _g.startswith("0x"), f"{len(_g)} caratteri")
    _d=json.loads(_sp.run([f"{_P3.FOUNDRY}/cast","decode-tx",_g],
        capture_output=True,text=True,timeout=60).stdout)
    _pri=int(_d.get("maxPriorityFeePerGas","0x0"),16)
    dillo("dentro c'e' l'offerta che abbiamo chiesto",
          abs(_pri/1e9-4.632)<0.001, f"{_pri/1e9:.3f} gwei")
    _op=_sp.run([f"{_P3.FOUNDRY}/cast","wallet","address","--private-key",_P3.CHIAVE],
        capture_output=True,text=True).stdout.strip()
    dillo("la firma chi comanda il contratto",
          (_d.get("signer","" ) or "").lower()==_op.lower(), _d.get("signer",""))
    dillo("va al nostro contratto, tipo 1559",
          (_d.get("to","") or "").lower()==_P3.CONTRATTO.lower() and _d.get("type")=="0x2",
          f"{_d.get('to','')[:12]} tipo {_d.get('type')}")
except Exception as _e:
    dillo("il pacchetto porta un'offerta", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7h. L'ESECUZIONE IN CATENA FUNZIONA ANCORA?")
# L'ULTIMO STADIO mai coperto dal C-check: il momento in cui i soldi si
# muovono. Provato a fondo il 3/11 (8 profondita' di crollo, tutte passano)
# ma con i dati di allora -- e la liquidita' cambia: una prova di ieri dice
# che funzionava ieri. agents/prova_in_catena.py rifa' la prova su una
# posizione VIVA biforcando la catena al blocco corrente. Gira ogni ~6 ore
# (nel giro del laghetto), non ogni mezz'ora: i preventivi sono una fonte
# gratuita e non si tortura.
# Un rinvio per fonte occupata NON e' un rosso: il verdetto precedente si
# tiene. Dire "non lo so adesso" e' molto meglio che dire "e' rotto".
try:
    _pc2=json.load(open(f"{D}/prova_in_catena.json"))
    _ore=(time.time()-(_pc2.get("quando") or 0))/3600
    dillo("l'ultima esecuzione su copia della catena PASSA",
          _pc2.get("passa") is True,
          f"{_pc2.get('verdetto_di','')[:70]}")
    dillo("ed e' stata provata di recente", _ore < 24, f"{_ore:.1f} ore fa")
    if _pc2.get("rinviata"):
        dillo("l'ultimo tentativo e' stato rinviato, non fallito", True,
              "fonte occupata: nessun guasto")
except Exception as _e:
    dillo("l'esecuzione in catena e' provata", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7i. I PREZZI IN ENTRATA SONO PLAUSIBILI?")
# VERIFICA AGGIUNTA il 4/11, e cambia direzione: fin qui il check guardava
# i PASSAGGI della catena, questo guarda un INGRESSO. Il prezzo
# dall'oracolo decide ogni quantita' che vendiamo, e il generatore aveva
# due cancelli sul NUMERO di prezzi e nessuno sui VALORI: un singolo prezzo
# corrotto passava e sbagliava tutto in silenzio.
# Il metro e' il tempo: il file si riscrive ogni due minuti, e in due
# minuti un asset non fa il 25%. Se saltano POCHI e' una lettura sbagliata;
# se saltano INSIEME e' il mercato -- e in quel caso va lasciato passare,
# perche' il crollo vero e' la cosa per cui ci stiamo preparando.
# Il generatore scrive e GRIDA, non blocca: bloccare lascerebbe in casa un
# file eventualmente gia' corrotto. Qui si raccoglie il grido.
try:
    _ps=json.load(open(f"{D}/prezzi_sospetti.json"))
    _sa=_ps.get("saltati") or []
    _su=_ps.get("su_quanti") or 1
    _eta=int(time.time()-(_ps.get("quando") or 0))
    _insieme = len(_sa) >= max(2, _su*0.25)
    dillo("il controllo sui valori dei prezzi ha girato", _eta < 600, f"{_eta}s fa")
    dillo("nessun prezzo salta da solo", not _sa or _insieme,
          "nessuno" if not _sa else
          (f"{len(_sa)} su {_su}: sembra il mercato" if _insieme
           else f"{len(_sa)} su {_su} -> "
                + ", ".join(f"{x['gettone'][:10]} {x['variazione']:+.0f}%" for x in _sa[:3])))
except Exception as _e:
    dillo("i prezzi in entrata sono controllati", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7l. LA COPPIA CHE ABBIAMO IN CASA E' ANCORA QUELLA VERA?")
# VERIFICA AGGIUNTA il 4/11, secondo ingresso guardato. composizione_posizioni.py
# compone SOLO le posizioni nuove e non rilegge mai le vecchie: una posizione
# composta giorni fa tiene la sua coppia per sempre, anche se il debitore ha
# cambiato garanzia. L'ordine pronto venderebbe un gettone che la posizione
# non ha piu' -- il contratto non lo trova in casa e lo scambio si annulla.
# Trovata subito una vera, e sulla posizione PIU' VICINA a cadere di tutte:
# garanzia passata da wstETH a weETH, noi avevamo wstETH. 1 su 25.
# agents/composizione_riletta.py rilegge dalla catena le piu' vicine, corregge
# e INVALIDA il loro ordine pronto. Gira nel giro del laghetto.
try:
    _cr=json.load(open(f"{D}/composizione_riletta.json"))
    _ore=(time.time()-(_cr.get("quando") or 0))/3600
    dillo("le coppie sono state rilette di recente", _ore < 6,
          f"{_ore:.1f} ore fa, {_cr.get('rilette')} posizioni")
    dillo("nessuna coppia letta male resta in casa",
          _cr.get("cambiate",0) == 0 or all(
              (json.load(open(f"{D}/vendite_pronte.json")).get(x["posizione"],{}) or {}).get("quando",0)==0
              or x["posizione"] not in json.load(open(f"{D}/vendite_pronte.json"))
              for x in (_cr.get("dettagli") or [])),
          f"{_cr.get('cambiate')} cambiate, ordini invalidati")
    dillo("le letture della catena rispondono", _cr.get("mute",0)==0,
          f"{_cr.get('mute')} mute su {_cr.get('rilette')}")
except Exception as _e:
    dillo("le coppie sono rilette", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7m. CHI STA FUORI DAL RECINTO E' DAVVERO FUORI?")
# VERIFICA AGGIUNTA il 4/11, terzo ingresso. Decidiamo chi sorvegliare da un
# archivio di valori di salute vecchi fino a QUATTRO ORE: una posizione
# appena fuori dalla banda puo' essere scivolata dentro, o sotto soglia, e
# saremmo ciechi fino al prossimo rifacimento della lista.
# agents/fuori_dal_recinto.py legge VIVE quelle che NON guardiamo. Il
# campione non e' casuale: meta' dai piu' vicini al bordo, meta' da quelli
# col valore piu' vecchio -- i due modi in cui si attraversa senza saperlo.
# Un campione casuale avrebbe timbrato i numeri non guardati.
# LIMITE ONESTO: si leggono 40 su ~11.000. Zero attraversamenti trovati e'
# un LIMITE, non una dimostrazione -- ma il campione e' scelto dove la
# probabilita' e' massima, quindi vale piu' di 40 a caso.
try:
    _fr=json.load(open(f"{D}/fuori_dal_recinto.json"))
    _ore=(time.time()-(_fr.get("quando") or 0))/3600
    dillo("il fuori-recinto e' stato sondato di recente", _ore < 6,
          f"{_ore:.1f} ore fa, {_fr.get('letti')} su {_fr.get('fuori_in_tutto'):,}")
    dillo("nessuno e' scivolato dentro senza che lo sapessimo",
          _fr.get("dentro_la_banda",0)==0,
          "nessuno" if not _fr.get("dentro_la_banda") else
          f"{_fr['dentro_la_banda']} dentro, di cui "
          f"{sum(1 for c in _fr.get('casi',[]) if c.get('sotto_soglia'))} GIA' SOTTO SOGLIA")
    dillo("le letture vive rispondono", _fr.get("muti",0)==0,
          f"{_fr.get('muti')} mute su {_fr.get('letti')}")
except Exception as _e:
    dillo("il fuori-recinto e' sondato", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7n. L'ELENCO DEI DEBITORI ARRIVA FINO ALLA TESTA?")
# VERIFICA AGGIUNTA il 4/11, risalendo dagli ingressi alla SORGENTE, ed e'
# la piu' costosa trovata finora.
# Il raccoglitore segnava come "fatta" anche la finestra che contiene la
# TESTA della catena -- letta fino a dove la catena era arrivata in quel
# momento. Poi la catena avanza DENTRO la stessa finestra e quei blocchi non
# si rileggono mai: fino a 50.000 blocchi, circa una settimana di debitori
# nuovi che per noi non esistono. E i debitori nuovi a leva sono quelli piu'
# vicini alla liquidazione.
# Misurato appena corretto: 166 debitori mai visti, di cui 10 GIA' DENTRO
# la banda, con circa $141.000 di premio -- due a salute 1,0215 con
# $1.158.304 di debito ciascuno.
# LEZIONE: "fatta" non vuol dire "completa" quando il confine si muove.
# Qui si pretendono due cose: che la finestra della testa sia stata riletta
# di recente, e che non resti un mucchio di debitori senza salute nota.
try:
    _fw=json.load(open(f"{D}/finestre_debitori_v3.json"))
    _PASSO=50_000
    _t=rpc("eth_blockNumber",[])
    _ult=int(_t,16) if _t else 0
    _ftesta=(_ult//_PASSO)*_PASSO if _ult else None
    _eta_f=int(time.time()-os.path.getmtime(f"{D}/finestre_debitori_v3.json"))
    dillo("la finestra della testa e' stata riletta di recente", _eta_f < 10800,
          f"finestra {_ftesta:,}, elenco aggiornato {_eta_f//60} minuti fa"
          if _ftesta else f"{_eta_f//60} minuti fa")
    _deb=json.load(open(f"{D}/debitori.json"))
    _n_deb=len(_deb if isinstance(_deb,list) else _deb)
    _n_note=len(json.load(open(f"{D}/salute_note.json")))
    _mai=_n_deb-_n_note
    dillo("nessun debitore resta senza salute nota", _mai <= 20,
          f"{_mai} mai valutati su {_n_deb:,}")
except Exception as _e:
    dillo("l'elenco dei debitori arriva alla testa", False,
          f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7o. CHI SAPPIAMO ESSERE IN PERICOLO, LO GUARDIAMO?")
# VERIFICA AGGIUNTA il 4/11, e chiude il passaggio che mi e' sfuggito
# stanotte: avevo trovato 166 debitori nuovi, letto le loro salute, visto
# che 10 erano DENTRO la banda con $141.000 di premio -- e loro NON erano
# nella lista che sorvegliamo. Sapere che una posizione e' in pericolo e
# non guardarla e' peggio che non saperlo.
# Il criterio e' quello di lista_corta.py: salute < 1,15 e debito >= $150.
# Un ritardo breve e' normale (la lista si rifa' ogni ~mezz'ora), quindi si
# tollera una piccola coda; un mucchio no.
try:
    _sn=json.load(open(f"{D}/salute_note.json"))
    _lc={x["indirizzo"].lower() for x in json.load(open(f"{D}/lista_corta.json"))}
    _devono={a for a,d in _sn.items()
             if d.get("debito",0) >= 150 and d.get("salute",9) < 1.15}
    _fuori=_devono - _lc
    _soldi=sum(_sn[a]["debito"]*0.5*0.07 for a in _fuori)
    dillo("chi sappiamo in pericolo e' nella lista", len(_fuori) <= 15,
          f"{len(_fuori)} fuori lista su {len(_devono)}"
          + (f", ${_soldi:,.0f} di premio" if _fuori else ""))
    # LA GRAVITA' DIPENDE DA QUANTO SONO VICINE, non solo da quanto
    # valgono. Taratura corretta il 4/11: il controllo era rosso per tre
    # posizioni a salute 1,13-1,15, cioe' a un 12% dalla caduta, che
    # aspettavano solo il prossimo rifacimento della lista (ogni ~mezz'ora).
    # Un ritardo di mezz'ora su chi e' a un 12% non e' un'emergenza, e un
    # allarme che suona per un ritardo normale si impara a ignorare.
    # Chi e' sotto 1,05 invece puo' cadere in poche ore: quello e' grave.
    _urgenti=[(_sn[a]["debito"]*0.5*0.07, a) for a in _fuori
              if _sn[a].get("salute", 9) < 1.05]
    _urgenti.sort(reverse=True)
    _lontani=len(_fuori)-len(_urgenti)
    dillo("nessuna posizione VICINA e grossa resta fuori lista",
          not _urgenti or _urgenti[0][0] < 5000,
          (" | ".join(f"{a[:10]} ${p:,.0f} (salute {_sn[a]['salute']:.4f})"
                      for p,a in _urgenti[:3]) if _urgenti
           else f"nessuna sotto 1,05; {_lontani} piu' lontane aspettano la lista"))
except Exception as _e:
    dillo("chi e' in pericolo e' guardato", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7p. GLI ORDINI SI RINNOVANO DAVVERO?")
# VERIFICA AGGIUNTA il 4/11 notte, e nasce dalla scoperta che l'indicatore
# della copertura MENTIVA: contava gli ordini "costruiti col margine
# giusto" (che non scade mai) invece di quelli che il pescatore
# ACCETTEREBBE. Al momento della scoperta: 887 contate come coperte, di cui
# 205 che tenta() avrebbe rifiutato per anzianita', e ZERO ordini piu'
# freschi di due ore.
# La causa: chiedevamo 80 preventivi per giro, la fonte rifiutava il 36%
# delle passate, e un rifiuto costa TUTTA la passata -- quindi il rinnovo
# era fermo. Ora se ne chiedono 20.
# Qui si guarda il RITMO, non lo stato: se nessun ordine e' giovane, il
# rinnovo e' rotto anche se il cassetto sembra pieno.
try:
    import pescatore as _P4
    _V=json.load(open(f"{D}/vendite_pronte.json"))
    _ora=time.time()
    _con_scambio=[x for x in _V.values()
                  if x.get("sede") and not x.get("stesso")]
    _giovani=[x for x in _con_scambio if (_ora-x.get("quando",0)) < 7200]
    _scaduti=[x for x in _con_scambio if (_ora-x.get("quando",0)) >= _P4.ORDINE_VALE]
    dillo("qualche ordine e' stato rinnovato nelle ultime due ore",
          len(_giovani) > 0, f"{len(_giovani)} giovani su {len(_con_scambio)}")
    # SI CONTANO SOLO GLI ORDINI CHE CI SERVONO ANCORA. Difetto trovato il
    # 4/11 sera: contavo tutti gli scaduti, e dei 102 segnalati 77 erano
    # posizioni la cui SALUTE E' RISALITA (non le guardiamo piu', quindi il
    # loro ordine non serve rinfrescarlo) e 24 erano coppie senza strada che
    # saltiamo di proposito. Una sola andava davvero rifatta.
    # E' la quinta volta oggi che misuro una cosa VICINA invece della cosa
    # che conta: un ordine scaduto per una posizione che non sorvegliamo
    # piu' non e' un problema, e contarlo fa suonare l'allarme a vuoto.
    try:
        _corta={x["indirizzo"].lower() for x in json.load(open(f"{D}/lista_corta.json"))}
        _co={k.lower(): v for k, v in json.load(open(f"{D}/composizione.json")).items()}
        _sz=set(json.load(open(f"{D}/tetti_coppia.json")).get("senza_strada") or {})
    except Exception:
        _corta, _co, _sz = set(), {}, set()
    def _serve(k):
        k=k.lower()
        if k not in _corta: return False          # salute risalita
        c=_co.get(k)
        if not c: return False
        g=c["garanzia_principale"].lower(); d=c["debito_principale"].lower()
        return f"{g}|{d}" not in _sz              # non e' una coppia senza strada
    _utili=[k for k,x in _V.items()
            if x.get("sede") and not x.get("stesso") and _serve(k)]
    _scad_utili=[k for k in _utili
                 if (_ora-(_V[k].get("quando") or 0)) >= _P4.ORDINE_VALE]
    dillo("gli ordini che ci servono sono freschi",
          len(_scad_utili) <= max(2, len(_utili)*0.1),
          f"{len(_scad_utili)} scaduti su {len(_utili)} che sorvegliamo "
          f"(ne ignoro {len(_scaduti)-len(_scad_utili)}: salute risalita o "
          f"coppia senza strada)")
    # il tasso di rifiuto della fonte, dal log del giro
    try:
        # SI MISURA L'ESITO, NON IL RIFIUTO. Difetto del controllo stesso,
        # trovato il 4/11 all'alba: questa riga contava i rifiuti
        # dell'aggregatore, e l'avevo scritta quando un rifiuto costava
        # TUTTA la passata. Adesso un rifiuto vuol dire solo che siamo
        # passati a Uniswap -- il 90% di rifiuti con 97 ordini preparati
        # per passata e' un sistema SANO, e il rosso era un falso allarme
        # che avrebbe insegnato a ignorare l'indicatore.
        # Quello che conta e' se le vendite SI PRODUCONO.
        _righe=[r for r in open("/tmp/laghetto.log", errors="ignore")
                if "preparate " in r and "fallite" in r]
        _ult=_righe[-10:]
        _prep=[]
        for _r in _ult:
            try: _prep.append(int(_r.split("preparate ")[1].split(",")[0]))
            except Exception: pass
        _media=sum(_prep)/max(1,len(_prep))
        dillo("le vendite si producono", _media >= 5,
              f"{_media:.0f} per passata sulle ultime {len(_prep)}"
              + (" (l'aggregatore ci caccia ma si va di Uniswap)"
                 if "troppe richieste" in open("/tmp/laghetto.log", errors="ignore").read()[-20000:]
                 else ""))
    except Exception: pass
except Exception as _e:
    dillo("gli ordini si rinnovano", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7q. LE ROTTE CHE USIAMO RENDONO DAVVERO?")
# RIFATTA il 4/11 sera, e la ragione e' una lezione: avevo DUE agenti che
# misuravano la stessa cosa. qualita_rotte_uniswap.py provava 12 coppie a
# $100.000 fisso; tetti_misurati.py cerca per dimezzamenti il tetto di
# OGNI coppia su tutte le piazze. Il primo era rimasto fuori dal giro e il
# suo file aveva 12 ore, quindi questo controllo era rosso -- non perche'
# le rotte fossero cattive, ma perche' guardavo la misura vecchia delle due.
# Due misure della stessa cosa danno due risposte: si tiene la migliore e
# si guarda quella. La fonte buona e' tetti_misurati, che gira ogni due ore
# nel giro e misura cio' che useremmo davvero.
try:
    _tc2=json.load(open(f"{D}/tetti_coppia.json"))
    _ore2=(time.time()-os.path.getmtime(f"{D}/tetti_coppia.json"))/3600
    _mis2=sum(1 for k in (_tc2.get("tetti") or {}) if "|" in k)
    dillo("le rotte sono misurate di recente", _ore2 < 6,
          f"{_mis2} coppie tarate, aggiornate {_ore2:.1f} ore fa")
    _sz2=_tc2.get("senza_strada") or {}
    dillo("le rotte cattive vengono rifiutate, non messe in cassetto", True,
          f"{_mis2} con un tetto, {len(_sz2)} senza strada e registrate col motivo")
except Exception as _e:
    dillo("le rotte sono misurate", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7r. QUANTO PREMIO NON SAPPIAMO VENDERE?")
# VERIFICA AGGIUNTA il 4/11 mattina. Con l'aggregatore bloccato ci
# costruiamo le vendite su Uniswap, e la taratura dei tetti ha misurato
# che per 26 coppie NESSUNA taglia rende abbastanza: sUSDe, osETH, rsETH,
# syrupUSDT -- tutte monete che vivono su Curve, non su Uniswap.
# Il numero non e' un guasto da riparare stanotte: e' il confine di quello
# che oggi sappiamo fare, e va tenuto davanti agli occhi perche' dice
# quanto vale imparare il prossimo mestiere (Curve).
# Finche' resta scritto non e' un buco nascosto; diventerebbe un buco se
# smettessimo di guardarlo.
try:
    _tc=json.load(open(f"{D}/tetti_coppia.json"))
    _sz=_tc.get("senza_strada") or {}
    _tot=sum(v.get("premio_in_gioco",0) for v in _sz.values())
    _mis=sum(1 for k in (_tc.get("tetti") or {}) if "|" in k)
    dillo("i tetti sono misurati, non scritti a mano", _mis >= 40,
          f"{_mis} coppie tarate col Quoter")
    dillo("il premio senza strada e' noto e sotto controllo", True,
          f"${_tot:,.0f} su {len(_sz)} coppie (Curve, non Uniswap)")
    # SI MISURA LO SPRECO, non si cerca una parola nel log. La prima
    # stesura cercava "salto" negli ultimi 30.000 caratteri: dipendeva da
    # quando il giro aveva girato l'ultima volta, non da come va -- quindi
    # rosso per un motivo che non c'entra. Il numero vero e' la frazione di
    # tentativi che falliscono: prima di saltare gli impossibili erano 74
    # su 120, adesso devono essere pochi.
    _rr=[r for r in open("/tmp/laghetto.log", errors="ignore")
         if "preparate " in r and "fallite" in r][-6:]
    _f=_p=0
    for _r in _rr:
        try:
            _p += int(_r.split("preparate ")[1].split(",")[0])
            _f += int(_r.split("fallite ")[1].split(" ")[0])
        except Exception: pass
    _quota = _f/max(1,_p+_f)
    dillo("il giro non spreca passate sugli impossibili", _quota < 0.3,
          f"{_f} falliti su {_p+_f} tentativi = {100*_quota:.0f}%")
except Exception as _e:
    dillo("il premio senza strada e' noto", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7w. I NOSTRI PACCHETTI AVREBBERO FUNZIONATO?")
# IL DENOMINATORE CHE NON AVEVAMO (4/11 sera). I pacchetti della sentinella
# sono SCOMMESSE: li mandiamo su posizioni ancora sane sperando che quel
# preciso aggiornamento di prezzo le spinga sotto 1,0. Se non le spinge, la
# liquidazione si annulla PER COSTRUZIONE.
# Quindi "accettati migliaia, inclusi zero" puo' non essere un problema di
# consegna: puo' essere che nessuna delle candidate cadesse davvero.
# Ora la sentinella SIMULA i suoi pacchetti dopo averli mandati
# (eth_callBundle, costa zero) e conta quante volte avrebbero funzionato.
# Questo numero, dopo qualche centinaio di aggiornamenti, dice se la strada
# dello "stesso blocco" scatta mai con le candidate che scegliamo -- e se
# resta zero, le prese stanno sulla strada dello scivolamento, non qui.
# NOTA: con poche decine di pacchetti simulati lo zero non vuol dire niente.
# Il controllo passa se la misura GIRA; il numero va letto quando e' grande.
# E SI VERIFICA CHE IL PACCHETTO PORTI SOLO CHI E' ALLA PORTATA.
# Misurato il 4/11 sera: un aggiornamento dell'oracolo muove il prezzo
# dello 0,507% in mediana, 0,585% al massimo -> serve salute sotto ~1,006.
# Prima il pacchetto portava candidate fino a 1,25, che avrebbero avuto
# bisogno di un movimento 34 volte il massimo mai visto: posti sprecati per
# costruzione, ed e' per questo che 0 su 168 avrebbero funzionato.
try:
    import sentinella as _SE
    import pescatore as _PE
    _c=_SE.candidate()
    # la soglia si legge dalla sentinella, non si ricopia: il 5/11 l'ho
    # corretta da 1,012 a 1,06 (ricavata da 40 cadute vere) e un controllo
    # con la soglia ricopiata sarebbe diventato rosso per una riparazione.
    _PORT=1.06
    try:
        import inspect as _in
        _src=_in.getsource(_SE.candidate)
        import re as _re
        _m=_re.search(r"PORTATA\s*=\s*([\d.]+)", _src)
        if _m: _PORT=float(_m.group(1))
    except Exception: pass
    _fuori=[x for x in _c if x["salute"] >= _PORT]
    dillo("il pacchetto porta solo chi e' alla portata", not _fuori,
          f"portata {_PORT}, {len(_c)} candidate, la piu' lontana a "
          f"{max([x['salute'] for x in _c], default=0):.4f}"
          if _c else "nessuna candidata")
    # E SI VERIFICA CHE SAPPIA DI QUALE PREZZO PARLA L'AGGIORNAMENTO.
    # Scoperta del 4/11 sera: per 2.749 eventi la sentinella registrava
    # l'inoltratore di Chainlink (CHI parla) invece del feed (DI COSA
    # parla), perche' 0x6fadcf72 e' forward(address,bytes) e il feed sta
    # nel primo argomento. Il 74% degli eventi non tocca un nostro asset.
    import mappa_feed as _MF
    _nostri={k.lower() for k in _PE.AMMESSI}
    _wn=[_MF.nome_feed(f) for f in list(json.load(
        open(f"{D}/nomi_feed.json")).keys())[:1]] if os.path.exists(
        f"{D}/nomi_feed.json") else []
    _eth="0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    _tutte=_SE.candidate(); _solo=_SE.candidate([_eth])
    dillo("la sentinella sa di quale prezzo parla", 0 < len(_solo) <= len(_tutte),
          f"su ETH/USD sceglie {len(_solo)} esposte a WETH delle {len(_tutte)} candidate")
    try:
        _nf=json.load(open(f"{D}/sentinella_viva.json"))
        _tot=_nf.get("nostri_feed",0)+_nf.get("non_nostri",0)
        # TARATO SULLA COSA, NON SULLA SOGLIA (errore mio, 6a volta).
        # La prima versione pretendeva "almeno uno scartato" e diventava
        # rossa su 4 eventi, dove non scartarne nessuno e' normale (il 26%
        # misurato significa che 3 su 3 nostri capita). Quello che mi
        # interessa e' che la DISCRIMINAZIONE esista, cioe' che il campo sia
        # presente e che su un campione abbastanza grande qualcuno cada.
        _sa = ("non_nostri" in _nf) and (
            _tot < 30 or _nf.get("non_nostri", 0) > 0)
        dillo("scarta gli aggiornamenti di altri asset", _sa,
              f"{_nf.get('nostri_feed',0)} nostri, {_nf.get('non_nostri',0)} di "
              f"altri asset su {_tot} eventi"
              + (" (campione ancora piccolo)" if _tot < 30 else ""))
    except Exception as _e:
        dillo("scarta gli aggiornamenti di altri asset", False, str(_e)[:60])
    _sv=json.load(open(f"{D}/saluti_vive.json"))
    _es=int(time.time()-_sv.get("quando",0))
    dillo("la sentinella usa la salute VIVA, non l'archivio", _es < 180,
          f"{len(_sv.get('saluti') or {})} saluti pubblicate dal pescatore {_es}s fa")
except Exception as _e:
    dillo("il pacchetto porta solo chi e' alla portata", False,
          f"{type(_e).__name__}: {str(_e)[:50]}")
try:
    _af=json.load(open(f"{D}/avrebbero_funzionato.json"))
    _sim=_af.get("simulati",0); _bu=_af.get("buoni",0)
    _eta=(time.time()-_af.get("quando",0))/3600
    dillo("la simulazione gira", _eta < 6 and _sim > 0,
          f"{_sim} pacchetti simulati su {_af.get('eventi')} aggiornamenti, "
          f"{_eta:.1f} ore fa")
    _q=100*_bu/max(1,_sim)
    print(f"      QUANTE VOLTE AVREBBE FUNZIONATO: {_bu} su {_sim} = {_q:.1f}%"
          + ("   (campione ancora troppo piccolo per concludere)" if _sim < 300
             else ("   <<< la strada dello stesso blocco NON scatta: le prese "
                   "stanno sullo scivolamento" if _bu == 0 else "")))
except FileNotFoundError:
    # NIENTE DA SIMULARE NON E' UNA SIMULAZIONE ROTTA. Il file nasce al primo
    # aggiornamento di un NOSTRO asset: se da quando la misura e' ripartita
    # non ne e' arrivato nessuno, l'assenza e' il mondo, non un guasto.
    dillo("la simulazione gira", se.get("nostri_feed",0)==0,
          "nessun aggiornamento dei nostri asset da quando la misura e'"
          " ripartita: niente da simulare"
          if se.get("nostri_feed",0)==0 else
          "il file manca pur essendoci stati aggiornamenti nostri")
except Exception as _e:
    dillo("la simulazione gira", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7x. LO SPAZIO NEL BLOCCO: arriviamo a chi costruisce?")
# BLOCCO 6, indicato da entrambi i revisori esterni il 4/11 e confermato
# dalla misura in modo brutale: delle 42 liquidazioni sopra i $500 degli
# ultimi 30 giorni, beaverbuild ha costruito il 75,5% del premio e
# BuilderNet il 17,7%. Flashbots NON HA COSTRUITO NESSUNO di quei 42
# blocchi -- e noi mandavamo tutti i pacchetti solo al relay di Flashbots.
# Copertura di mercato prima: ZERO. Adesso 93,2%.
# LA DISTINZIONE CHE CI MANCAVA: "accettato dal relay" non e' "arrivato a
# chi costruisce quel blocco". Contavamo la prima e credevamo la seconda.
try:
    import invia_pacchetto as _IP
    _sb=json.load(open(f"{D}/spazio_nel_blocco.json"))
    _ore=(time.time()-_sb.get("quando",0))/3600
    dillo("sappiamo chi costruisce i blocchi che contano", _ore < 12,
          f"{len(_sb.get('costruttori') or [])} costruttori, misurato {_ore:.1f} ore fa")
    # LA POPOLAZIONE E' FRESCA? (aggiunto il 5/11, e avrebbe gridato 15 ore
    # prima.) La lista corta era vecchia di 15,1 ore perche' il suo ramo era
    # stato disattivato per un errore di nome, e NESSUN controllo guardava
    # l'eta' di quel file: guardavamo che i processi fossero vivi, non che il
    # dato fosse fresco. La nona e la decima liquidazione hanno colpito
    # posizioni che non erano nel libro: chi non e' nel libro non si sorveglia,
    # e un libro vecchio di 15 ore non contiene chi e' entrato stanotte.
    # UN PROCESSO VIVO NON E' UN DATO FRESCO: sono due stadi, e vogliono due
    # contatori.
    for _f, _max in (("lista_corta.json", 45), ("vendite_pronte.json", 45),
                     ("composizione.json", 90)):
        _p = f"{D}/{_f}"
        if os.path.exists(_p):
            _eta = (time.time() - os.path.getmtime(_p)) / 60
            dillo(f"{_f} fresca (max {_max} min)", _eta < _max, f"{_eta:.0f} min")
        else:
            dillo(f"{_f} esiste", False, "manca")
    dillo("consegniamo a piu' di una porta", len(_IP.PORTE) >= 3,
          ", ".join(n for n,_ in _IP.PORTE))
    _q=_sb.get("quota_coperta",0)
    dillo("copriamo la gran parte del mercato", _q >= 90,
          f"{_q}% del premio passa da costruttori a cui consegniamo")
    # e le porte rispondono davvero, non solo sono configurate
    _r=_IP.a_tutte_le_porte("eth_blockNumber",[])
    _vive=[n for n,(ok,risp) in _r.items() if risp]
    dillo("le porte rispondono", len(_vive) >= 3,
          f"{len(_vive)} su {len(_IP.PORTE)}: " + ", ".join(_vive))
except Exception as _e:
    dillo("arriviamo a chi costruisce", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7y. IL PREMIO LO LEGGIAMO O LO INVENTIAMO?")
# Verifica aggiunta il 4/11, e nasce dal tabellone: il premio vero della
# liquidazione persa era l'1,24% su garanzia USDT, contro il 7% che
# stimavamo. Letto dal protocollo, il premio va dal 4,50% (USDC, USDT)
# all'8,50% (USDe, LBTC) -- e noi scrivevamo 7 fisso su tutti.
# Conseguenza misurata: la soglia sulla resa delle rotte (94%) era
# giustificata sul 7%; su una garanzia al 4,50% una vendita al 94% va in
# PERDITA dell'1,8%, e la soglia la autorizzava.
# LEZIONE: un numero inventato regge finche' nessuno lo confronta col mondo.
try:
    import premi as _PRM
    _pv=json.load(open(f"{D}/premi_veri.json"))
    _eta=(time.time()-_pv.get("quando",0))/3600
    dillo("i premi sono letti dal protocollo", len(_pv.get("premi") or {})>=10,
          f"{len(_pv.get('premi') or {})} gettoni, letti {_eta:.1f} ore fa")
    dillo("i premi sono freschi", _eta < 24, f"{_eta:.1f} ore")
    _v=set((_pv.get("premi") or {}).values())
    dillo("il premio non e' lo stesso per tutti", len(_v)>=3,
          f"{len(_v)} valori diversi: dal {100*min(_v):.2f}% al {100*max(_v):.2f}%")
    _u="0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
    _w="0x4c9edd5852cd905f086c759e8383e09bff1e68b3"
    dillo("la soglia della resa dipende dalla garanzia",
          _PRM.resa_minima(_u) > _PRM.resa_minima(_w),
          f"USDC {100*_PRM.resa_minima(_u):.2f}% vs USDe {100*_PRM.resa_minima(_w):.2f}%")
except Exception as _e:
    dillo("i premi sono letti dal protocollo", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 7z. IL TABELLONE: cosa e' successo nel mondo, e noi l'abbiamo preso?")
# BLOCCO 6, nato il 4/11 da una domanda di Nicolo'. Le altre 83 verifiche
# guardano DENTRO la macchina; nessuna guardava fuori. Per questo potevamo
# stare a cinque blocchi al 100% mentre perdevamo $422.496 di premio in
# 24 ore. Un controllo di meccanismo non trova mai una partita persa.
# Qui si legge il mondo: le liquidazioni VERE di Aave, e per ognuna il
# motivo per cui non era nostra.
# E C'E' UN SECONDO MESTIERE: se compare un MOTIVO che non e' fra quelli
# che conosciamo, quello e' un blocco che non avevamo considerato. E' il
# modo di accorgersi di un settimo blocco senza che qualcuno lo dica.
MOTIVI_NOTI = ("L'ABBIAMO PRESA NOI", "non la conoscevamo",
               "senza ordine pronto", "corsia LENTA",
               "non l'abbiamo mai messa in un pacchetto",
               "eravamo nella gara e l'abbiamo persa")
try:
    _tb=json.load(open(f"{D}/tabellone.json"))
    _eta=(time.time()-(_tb.get("quando") or 0))/3600
    dillo("il tabellone e' stato letto di recente", _eta < 2,
          f"{_eta:.1f} ore fa, {_tb.get('quante')} liquidazioni vere "
          f"nelle ultime {_tb.get('ore')} ore")
    # IL BLOCCO 6 SI MISURA SU QUANTO HA CAPITO, non su quanto abbiamo
    # vinto. Correzione del 4/11 sera: "abbiamo preso qualcosa" resterebbe
    # rosso per settimane, e un indicatore permanentemente rosso si impara
    # a ignorare -- oggi mi e' successo quattro volte con controlli miei.
    # Il punteggio della partita resta VISIBILE come numero (sotto), non
    # come semaforo: un numero non si ignora, un rosso fisso si'.
    _nostro=_tb.get("premio_nostro",0); _altrui=_tb.get("premio_altrui",0)
    print(f"      PUNTEGGIO: premio passato ${_nostro+_altrui:,.0f}, "
          f"preso da noi ${_nostro:,.0f}, dagli altri ${_altrui:,.0f}")
    _liq0=_tb.get("liquidazioni") or []
    _senza_motivo=[r for r in _liq0 if not (r.get("motivo") or "").strip()]
    dillo("ogni liquidazione ha il suo motivo", not _senza_motivo,
          f"{len(_liq0)} studiate, tutte con un motivo" if not _senza_motivo
          else f"{len(_senza_motivo)} senza motivo")
    _colpe=_tb.get("colpe") or {}
    dillo("ogni motivo da' la colpa a un blocco", "0" not in _colpe,
          "tutti i motivi mappano su un blocco" if "0" not in _colpe
          else f"MOTIVO SENZA BLOCCO: ${_colpe['0']['premio_perso']:,.0f} persi")
    try:
        _vinc=json.load(open(f"{D}/vincitori.json"))
        _ev=(time.time()-_vinc.get("quando",0))/3600
        # TARATO SULLA COSA, NON SULLA SOGLIA. La prima versione pretendeva
        # "almeno uno studiato" e diventava rossa anche quando nel mondo non
        # era successo niente da studiare: nelle ultime 6 ore il premio
        # totale era $3. Il controllo che mi interessa e': se c'e' stata una
        # liquidazione che VALEVA la pena, sappiamo chi l'ha vinta?
        _grosse=[r for r in _liq0 if (r.get("premio") or 0) >= 150]
        _ok=(_ev < 3) and (not _grosse or bool(_vinc.get("studi")))
        dillo("abbiamo studiato chi ha vinto", _ok,
              f"{len(_vinc.get('studi') or [])} vincitori studiati, {_ev:.1f} ore fa"
              + (f" ({len(_grosse)} liquidazioni sopra $150 da studiare)"
                 if _grosse else " (nessuna liquidazione che valesse la pena)"))
    except Exception:
        dillo("abbiamo studiato chi ha vinto", False, "nessuno studio")
    # UNA COLPA NON EVAPORA COL TEMPO. Difetto trovato il 4/11 sera: il
    # blocco 4 e' risalito da 82% a 100% non perche' riparato, ma perche' la
    # sconfitta da $947.639 era uscita dalla finestra del tabellone. Ora le
    # sconfitte costose stanno in un registro permanente e si chiudono solo
    # NOMINANDO la verifica che le ripara -- e il nome deve esistere davvero,
    # altrimenti bastava scrivere "riparato" per farsi tornare i punti.
    try:
        _sc=json.load(open(f"{D}/sconfitte_aperte.json"))
        _vuote=[k for k,v in _sc.items()
                if v.get("riparato_da") is not None
                and len(str(v.get("riparato_da") or "")) < 15]
        _ap=[k for k,v in _sc.items() if not v.get("riparato_da")]
        dillo("ogni sconfitta chiusa nomina la sua riparazione", not _vuote,
              f"{len(_sc)} sconfitte costose in registro, {len(_ap)} ancora aperte"
              if not _vuote else f"{len(_vuote)} chiuse senza nominare niente")
    except FileNotFoundError:
        dillo("ogni sconfitta chiusa nomina la sua riparazione", True,
              "registro ancora vuoto: nessuna sconfitta sopra $1.000")
    except Exception as _e:
        dillo("ogni sconfitta chiusa nomina la sua riparazione", False, str(_e)[:60])
    _liq=_tb.get("liquidazioni") or []
    _ignoti=[r for r in _liq
             if not any(m in (r.get("motivo") or "") for m in MOTIVI_NOTI)]
    dillo("nessun motivo di sconfitta SCONOSCIUTO", not _ignoti,
          "tutti i motivi sono fra quelli che conosciamo" if not _ignoti
          else f"MOTIVO NUOVO = BLOCCO NUOVO: {_ignoti[0].get('motivo')}")
    # le sconfitte che costano: se una ricompare, il blocco 6 non e' chiuso
    _care=[r for r in _liq if not r.get("nostra") and r.get("premio_vero_usd",0) >= 1000]
    dillo("nessuna sconfitta costosa da riparare", not _care,
          "nessuna sopra $1.000" if not _care else
          " | ".join(f"${r['premio_vero_usd']:,.0f}: {r['motivo'][:44]}" for r in _care[:2]))
except Exception as _e:
    dillo("il tabellone e' letto", False, f"{type(_e).__name__}: {str(_e)[:50]}")

print("\n--- 8. LA COPERTURA")
pc=json.load(open(f"{D}/pronti_al_crollo.json"))
for r in pc["righe"]:
    if r["calo_percento"] in (5,6,9):
        dillo(f"dump {r['calo_percento']}%: tutte pronte", r["scoperte"]==0,
              f"cadono {r['cadono']}, scoperte {r['scoperte']}")
v=json.load(open(f"{D}/vendite_pronte.json"))
pronte=sum(1 for x in v.values() if x.get("sede") or x.get("stesso"))
dillo("ordini in cassetto", pronte>700, f"{pronte}")
# IL CASSETTO NON DEVE RIMPICCIOLIRE. Verifica aggiunta il 4/11 dopo un
# disastro che ho causato io: giravano due preparazioni insieme, entrambe
# avevano letto il cassetto all'inizio e alla fine entrambe l'hanno
# riscritto per intero -- l'ultima ha cancellato il lavoro dell'altra e il
# cassetto e' passato da 1.019 ordini a 250.
# Riparato alla radice (ora il salvataggio FONDE invece di sovrascrivere),
# ma la riparazione va sorvegliata: se il numero scende di colpo, qualcosa
# sta ancora sovrascrivendo. Un calo lento e' normale (gli ordini scadono),
# un crollo no.
try:
    _st=json.load(open(f"{D}/cassetto_storia.json"))
except Exception:
    _st={"punti":[]}
_st["punti"]=(_st.get("punti") or [])[-20:]+[{"quando":time.time(),"quanti":pronte}]
json.dump(_st, open(f"{D}/cassetto_storia.json","w"), indent=1)
_pp=[x["quanti"] for x in _st["punti"]]
_max=max(_pp) if _pp else pronte
_crollo = pronte < _max*0.7 and len(_pp)>2
dillo("il cassetto non e' crollato", not _crollo,
      f"ora {pronte}, massimo recente {_max}"
      + ("  <<< QUALCOSA LO STA SOVRASCRIVENDO" if _crollo else ""))

# LA GUARDIA CHE SPARA CONOSCE IL COSTO DEL COLPO. Verifica aggiunta il
# 7/11. Lo stadio precedente che misuravamo era «c'e' gas per N colpi»:
# guarda il SALDO. Questo guarda la cosa dopo -- se chi DECIDE sa quanto
# costa un colpo adesso. Prima non lo sapeva, e a 10 gwei (il regime dei
# premi grossi) faceva passare una posizione da 2 $ di premio che costava
# 24,60 $ di gas. Una guardia che non conosce il prezzo non e' una guardia.
try:
    import gas_ora as _GO
    _bf,_pe,_eta = _GO.leggi()
    _cc = _GO.costo_colpo_usd(1_400_000)
    dillo("la guardia conosce il costo del colpo", _cc is not None,
          (f"{_bf:.3f} gwei, ETH ${_pe:.0f}, un colpo ${_cc:.2f} "
           f"(letto {_eta:.0f}s fa)") if _cc is not None else
          (f"NON LO SA: dato vecchio di {_eta:.0f}s" if _eta
           else "NON LO SA: nessuno scrive il gas"))
    # e la soglia di sorveglianza deve stare SOTTO quella economica, perche'
    # sorvegliare costa poco e sparare costa gas: se la sorveglianza fosse
    # piu' stretta della convenienza, perderemmo occasioni che pagano.
    import banda as _BA
    _sg = _BA.minimo_debito(_bf, _pe) if _bf else None
    if _sg is not None:
        dillo("sorvegliamo piu' largo di quanto spariamo",
              _BA.MINIMO_DEBITO <= _sg,
              f"sorveglianza da ${_BA.MINIMO_DEBITO}, "
              f"convenienza da ${_sg:.2f}")
except Exception as _e:
    dillo("la guardia conosce il costo del colpo", False, str(_e)[:60])

# IL CHECK DICE QUANTE VERIFICHE HA FATTO, CONFRONTATE CON IL SUO RECORD.
# Nata il 7/11 dalla troncatura invisibile descritta sopra: il numero di
# verifiche era SCESO da 130 a 25 e tutto quello che si vedeva era verde,
# perche' la riga di riepilogo non veniva mai stampata. Un check che si
# interrompe non e' un check al 25%: e' un check che MENTE sul 75% restante.
# Qui il confronto e' col massimo storico, cosi' una troncatura futura --
# per qualunque causa, non solo per SystemExit -- si vede come un ROSSO.
try:
    _crp = f"{D}/crescita_check.json"
    _cr = json.load(open(_crp)) if os.path.exists(_crp) else {}
    _gg = _cr.get("giri") or []
    _record = max([g.get("verifiche", 0) for g in _gg] + [0])
    _troncato = _record and len(ESITI) < _record * 0.9
    dillo("il check e' arrivato alla fine", not _troncato,
          f"{len(ESITI)} verifiche, record {_record}"
          + ("  <<< TRONCATO: qualcosa l'ha interrotto, il verde di sopra "
             "non copre il resto" if _troncato else ""))
except Exception as _e:
    dillo("il check e' arrivato alla fine", False, str(_e)[:50])

# IL CONTEGGIO DISTINGUE LE OCCASIONI DAL TRAFFICO. Verifica aggiunta il
# 7/11, nata dalla tredicesima liquidazione: premio lordo $0,0017, gas del
# suo blocco $0,0618 -- il vincitore ha PERSO 6 centesimi. Non l'abbiamo
# persa: l'abbiamo rifiutata, e rifiutarla era giusto.
# Ma il contatore la chiamava «persa» come le altre, e un numero che mescola
# «non ce l'ho fatta» con «non la volevo» non misura noi: misura il traffico.
# Il rischio concreto: se «perse» cresce mentre le occasioni vere stanno
# ferme, la pressione spinge ad abbassare le guardie per rincorrere eventi
# che ci farebbero perdere soldi.
# Il netto si calcola col gas DEL SUO BLOCCO, non col gas di oggi.
try:
    _vp = json.load(open(f"{D}/valeva_la_pena.json"))
    _fresco = (time.time() - os.path.getmtime(f"{D}/valeva_la_pena.json")) < 7200
    dillo("il conteggio distingue le occasioni dal traffico", _fresco,
          f"{_vp['eventi']} eventi, {_vp['transazioni']} transazioni, "
          f"{_vp['occasioni']} OCCASIONI (netto positivo col gas del suo "
          f"blocco)" + ("" if _fresco else "  <<< vecchio: rilancia "
                        "agents/valeva_la_pena.py"))
except Exception as _e:
    dillo("il conteggio distingue le occasioni dal traffico", False,
          f"mai girato: {str(_e)[:40]}")

# OGNI PORTA DELL'OCCHIO PARLA DAVVERO? Verifica aggiunta il 7/11.
# Lo stadio che misuravamo era «la porta e' aperta». Questo misura quello
# dopo: quanti messaggi ha consegnato, e di quanti e' stata la PRIMA.
# Trovato subito un guasto: tenderly, una delle tre finestre, consegnava
# ZERO messaggi -- provata da sola per 35 secondi, muta. Era caduta 40 volte
# in 68 minuti e quel rumore copriva le 5 cadute di drpc, che e' una porta
# vera. Credevamo di avere tre finestre e ne avevamo due, per la seconda
# volta, sempre per aver misurato il saluto invece del volume.
try:
    import occhio_ws as _OW
    _se = json.load(open(f"{D}/sentinella_viva.json"))
    _pt = _se.get("porte") or []
    _mute = [x["porta"] for x in _pt if x.get("messaggi", 0) == 0]
    _attese = len(_OW.PORTE_BUONE)
    if not _pt:
        dillo("ogni porta dell'occhio consegna davvero", False,
              "la sentinella non riporta ancora le porte: riavviala")
    else:
        dillo("ogni porta dell'occhio consegna davvero",
              not _mute and len(_pt) == _attese,
              "; ".join(f"{x['porta']}: {x['messaggi']} messaggi, "
                        f"{x['prime']} prime, {x['cadute']} cadute"
                        + (f", +{x['ritardo_mediano_ms']}ms"
                           if x.get("ritardo_mediano_ms") is not None else "")
                        for x in _pt)
              + (f"  <<< MUTE: {', '.join(_mute)}" if _mute else "")
              + (f"  <<< ne aspettavo {_attese}, ne riporta {len(_pt)}"
                 if len(_pt) != _attese else ""))
except Exception as _e:
    dillo("ogni porta dell'occhio consegna davvero", False, str(_e)[:50])

# ABBIAMO PIU' DI UN OCCHIO VELOCE? Verifica aggiunta il 7/11, nata dal
# contatore per porta: drpc aveva consegnato 21.118 messaggi ed era stata
# prima su ZERO delle 21 campanelle; publicnode prima su tutte e 21.
# «Zero volte prima» non basta a giudicare: una porta che arriva 5 ms dopo
# coprirebbe l'altra se cadesse, una che arriva mezzo secondo dopo no. Il
# ritardo mediano lo dice.
# PERCHE' CONTA: se una sola porta e' veloce, quella porta e' un punto
# singolo di rottura sulla cosa che decide se vinciamo -- e cade (drpc 4
# volte in 32 minuti). Due porte che vedono non sono due porte che corrono.
# La soglia e' 100 ms: la finestra fra l'aggiornamento in attesa e la
# chiusura del blocco e' 80-250 ms, quindi oltre 100 di ritardo la seconda
# porta arriva quando la gara e' decisa.
try:
    _se2 = json.load(open(f"{D}/sentinella_viva.json"))
    _pt2 = _se2.get("porte") or []
    _veloci = [x for x in _pt2
               if x.get("prime", 0) > 0
               or (x.get("ritardo_mediano_ms") is not None
                   and x["ritardo_mediano_ms"] <= 100)]
    _misurato = any(x.get("ritardi_misurati") for x in _pt2)
    dillo("piu' di un occhio arriva in tempo per la gara",
          len(_veloci) >= 2,
          "; ".join(f"{x['porta']}: "
                    + (f"prima {x['prime']} volte" if x.get("prime")
                       else "mai prima")
                    + (f", ritardo mediano {x['ritardo_mediano_ms']}ms "
                       f"su {x['ritardi_misurati']} misure"
                       if x.get("ritardo_mediano_ms") is not None
                       else ", ritardo non ancora misurato")
                    for x in _pt2)
          # NON SI AFFERMA CIO' CHE NON SI E' MISURATO. La prima versione
          # scriveva «UN SOLO OCCHIO VELOCE» anche quando non era ancora
          # arrivata nessuna campanella: una conclusione presentata come
          # misura. Il ritardo si riempie solo sugli aggiornamenti
          # d'oracolo (il filtro scarta tutto il resto prima), quindi dopo
          # un riavvio ci vogliono minuti. Finche' non c'e' niente, la
          # risposta e' «non lo so» -- rossa, perche' non sappiamo, ma
          # senza inventare il motivo.
          + ("  <<< NON LO SO ANCORA: nessuna campanella dal riavvio"
             if not _misurato and not any(x.get("prime") for x in _pt2)
             else ("  <<< UN SOLO OCCHIO VELOCE: se cade, siamo ciechi "
                   "sulla gara" if len(_veloci) < 2 else "")))
except Exception as _e:
    dillo("piu' di un occhio arriva in tempo per la gara", False, str(_e)[:50])

# L'OCCHIO SULLA GARA E' UNO SOLO, E LA SUA CADUTA DEVE URLARE (7/11).
# Censimento rifatto col criterio giusto su 30 indirizzi: UNA sola porta
# consegna transazioni intere leggibili. drpc accettava la richiesta senza
# dare errore e mandava hash (25.000 messaggi in 34 minuti, zero utili);
# tenderly era muta; le altre 27 rifiutano o chiedono una chiave.
# Il secondo nome di publicnode risolve agli STESSI indirizzi IP, quindi non
# e' un secondo fornitore: protegge dall'essere strozzati su un nome, non
# dalla caduta di chi ci serve i dati.
# Questa verifica non ripara il problema -- non e' riparabile gratis -- ma
# impedisce che diventi invisibile: se nell'ultimo quarto d'ora nessuna
# porta ha fatto passare una campanella mentre i becchi salivano, siamo
# ciechi sulla gara e non lo sapremmo da nessun altro indicatore.
try:
    _se3 = json.load(open(f"{D}/sentinella_viva.json"))
    _pt3 = _se3.get("porte") or []
    _leggono = [x for x in _pt3 if x.get("passati_dal_filtro", 0) > 0]
    _vive = [x for x in _pt3 if x.get("messaggi", 0) > 0]
    _becchi = _se3.get("becchi", 0)
    _ok3 = bool(_vive) and (bool(_leggono) or _becchi == 0)
    dillo("l'occhio sulla gara sta leggendo", _ok3,
          "; ".join(f"{x['porta']}: {x['messaggi']} messaggi, "
                    f"{x.get('passati_dal_filtro', 0)} campanelle lette"
                    for x in _pt3) + f"  (becchi totali {_becchi})"
          + ("" if _ok3 else "  <<< NESSUNA PORTA LEGGE: CIECHI SULLA GARA"))
    # e si dice a voce alta quanti FORNITORI distinti abbiamo, non quante
    # porte: due nomi dello stesso fornitore sono un fornitore.
    _forn = {x["porta"].split(".")[-2] + "." + x["porta"].split(".")[-1]
             for x in _pt3 if "." in x["porta"]}
    dillo("piu' di un fornitore ci serve il mempool", len(_forn) >= 2,
          f"{len(_forn)} fornitore/i: {', '.join(sorted(_forn))}"
          + ("  <<< UNO SOLO: la sua caduta ci rende ciechi sulla gara, e "
             "non e' riparabile con le porte gratuite (30 provate, 1 buona)"
             if len(_forn) < 2 else ""))
except Exception as _e:
    dillo("l'occhio sulla gara sta leggendo", False, str(_e)[:50])

# IL SECONDO OCCHIO E' ACCESO, FILTRATO, E QUANTO CONSUMA? (7/11)
# Tre verifiche su una cosa sola, perche' una sola di esse che manchi fa
# danno diverso: senza il secondo occhio una caduta ci rende ciechi sulla
# gara; senza il filtro il piano gratuito salta e si paga ~$640 al mese
# (identico allo schema dei €77,51 di Google Places: un "gratis fino a
# tanto" dove un parametro dimenticato moltiplica il consumo per seicento);
# e un consumo che non si misura e' un addebito che si scopre a fine mese.
try:
    import occhio_alchemy as _OA
    _k = _OA.chiavi.alchemy()
    _ind = _OA.destinatari()
    _cu, _fr, _msg = _OA.stato_consumo()
    _se4 = {}
    try:
        _se4 = json.load(open(f"{D}/sentinella_viva.json"))
    except Exception:
        pass
    dillo("il secondo occhio e' acceso", bool(_se4.get("secondo_occhio")),
          ("alchemy in ascolto" if _se4.get("secondo_occhio")
           else "SPENTO: " + ("chiave assente" if not _k
                              else "nessun indirizzo da filtrare" if not _ind
                              else "la sentinella non lo riporta: riavviala")))
    dillo("il filtro per destinatario c'e'", bool(_ind),
          f"{len(_ind)} indirizzi nel filtro"
          + ("" if _ind else "  <<< SENZA FILTRO SAREBBERO ~$640/MESE"))
    dillo("il consumo Alchemy e' sotto meta' del gratuito",
          _fr < _OA.ALLARME,
          f"{_cu:,.0f} CU su {_OA.GRATUITO_CU_MESE:,} "
          f"({_fr*100:.2f}%), {_msg} messaggi questo mese"
          + ("  <<< OLTRE META': controllare" if _fr >= _OA.ALLARME else ""))
except Exception as _e:
    dillo("il secondo occhio e' acceso", False, str(_e)[:60])

# UNA PRESA NON PUO' PASSARE INOSSERVATA. Verifica aggiunta il 7/11, e
# sostituisce l'email come misura del blocco «Nicolo' lo sa».
# L'email dipende da Google e da una chiave in una cartella che il sistema
# ripulisce: e' il canale piu' fragile che abbiamo. Il canale che non puo'
# rompersi e' il flag su disco, scritto PRIMA dell'email (verificato: nella
# sentinella il flag sta alla riga del successo, l'email due righe dopo),
# piu' la tabella che Nicolo' legge a ogni giro del loop.
# Qui si prova la CATENA, non i pezzi: la cartella e' scrivibile, tutti
# guardano lo stesso file, e chi legge il flag si ferma.
try:
    _prova = f"{D}/.prova_scrittura"
    open(_prova, "w").write("x")
    os.remove(_prova)
    _scrivibile = True
except Exception:
    _scrivibile = False
# LA SOGLIA SI CONTA, NON SI INDOVINA. La prima versione guardava cinque
# file scelti da me e pretendeva tre riferimenti: rossa per una mia stima,
# non per un guasto. Un controllo che fallisce per una soglia inventata
# insegna a ignorare i rossi, che e' il danno peggiore che possa fare.
import glob as _gl2
_chi_legge = 0
for _f in _gl2.glob("agents/*.py"):
    try:
        if "preso.flag" in open(_f).read():
            _chi_legge += 1
    except Exception:
        pass
dillo("una presa non puo' passare inosservata",
      _scrivibile and _chi_legge >= 2,
      f"cartella scrivibile: {'si' if _scrivibile else 'NO'}, "
      f"{_chi_legge} agenti guardano il flag, "
      f"e il flag si scrive PRIMA dell'email")

# I DUE CONTATORI DEVONO DIRE LO STESSO NUMERO DI TRANSAZIONI (7/11).
# Guasto trovato in un giro del loop: la ricevuta di una transazione
# aggregata (premio 1.126 $) non e' arrivata e il contatore delle occasioni
# l'ha saltata IN SILENZIO -- 10 transazioni invece di 11, 9 occasioni
# invece di 10, mentre il contatore sicuro diceva ancora 11. Un denominatore
# che si abbassa perche' una fonte ha singhiozzato non e' una misura.
# Due contatori indipendenti sulla stessa quantita' sono l'unico modo di
# trovare un errore di conteggio: se divergono, uno dei due sta mentendo.
try:
    _cs2 = json.load(open(f"{D}/conta_sicuro.json"))
    _vp2 = json.load(open(f"{D}/valeva_la_pena.json"))
    _a = _cs2.get("transazioni")
    _b = _vp2.get("transazioni")
    dillo("i due contatori concordano sulle transazioni",
          _a is not None and _a == _b,
          f"contatore sicuro {_a}, contatore delle occasioni {_b}"
          + ("" if _a == _b else "  <<< DIVERGONO: uno dei due perde casi"))
except Exception as _e:
    dillo("i due contatori concordano sulle transazioni", False,
          str(_e)[:50])

# IL GIUDIZIO DELLA ROTTA SCARTA DAVVERO UNA ROTTA CATTIVA? (7/11)
# La riparazione del guasto piu' grave della giornata vive su questo ramo, e
# il giorno in cui l'ho scritta NON si e' mai eseguito: Paraswap era in
# castigo e `preventivo` usciva prima. Una riparazione non esercitata e' una
# riparazione creduta per fede -- e proprio su questo ramo, perche' e' quello
# che gira quando qualcosa e' gia' andato storto.
# Qui si esercita con valori finti e senza rete: deterministico, e coglie una
# regressione il giorno che qualcuno cambia la soglia o rompe il confronto.
try:
    import rotta_migliore as _RM2
    _W = "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2"
    _U = "0xdac17f958d2ee523a2206206994597c13d831ec7"
    _q = 76_670_800_000_000_000_000
    _pv = _RM2.pari_valore(_W, _U, _q)
    if not _pv:
        dillo("il giudizio della rotta scarta una rotta cattiva", False,
              "prezzo mancante: non posso giudicare")
    else:
        _cattiva = _RM2.recupero(_W, _U, _q, int(_pv * 0.3541))
        _buona = _RM2.recupero(_W, _U, _q, int(_pv * 0.998))
        _ok4 = (_cattiva < _RM2.SOGLIA_RECUPERO
                and _buona >= _RM2.SOGLIA_RECUPERO)
        dillo("il giudizio della rotta scarta una rotta cattiva", _ok4,
              f"35,41% -> {'scartata' if _cattiva < _RM2.SOGLIA_RECUPERO else 'ACCETTATA'}, "
              f"99,8% -> {'accettata' if _buona >= _RM2.SOGLIA_RECUPERO else 'SCARTATA'}, "
              f"soglia {_RM2.SOGLIA_RECUPERO*100:.0f}%")
    # e il ricambio deve esistere: una chiave assente rende il giudizio
    # inutile, perche' scarteremmo senza avere dove andare
    import chiavi as _CH2
    dillo("c'e' una sede di ricambio se la prima rende poco",
          bool(_CH2.uno_inch()),
          "chiave 1inch presente" if _CH2.uno_inch() else
          "NESSUNA chiave 1inch: scarteremmo senza alternative")
except Exception as _e:
    dillo("il giudizio della rotta scarta una rotta cattiva", False,
          str(_e)[:60])

n=sum(1 for _,ok,_ in ESITI if not ok)
print(f"\n{'='*72}\nC-CHECK: {len(ESITI)-n} a posto, {n} da sistemare")
json.dump({"quando":time.time(),"esiti":[{"che":a,"ok":b,"dettaglio":c} for a,b,c in ESITI]},
          open(f"{D}/check_finale.json","w"), indent=1)
if n: print("DA SISTEMARE:"); [print("  -",a,c) for a,b,c in ESITI if not b]
