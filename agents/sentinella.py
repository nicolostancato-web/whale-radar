# -*- coding: utf-8 -*-
"""LA SENTINELLA: vede l'aggiornamento di prezzo MENTRE E' ANCORA IN ATTESA
e spara un pacchetto che entra nello STESSO blocco.

E' il passo dal 40% al 100% dell'«accorgersi», l'unico punto in cui eravamo
dietro ai professionisti.

IL DISEGNO, e perche' e' piu' semplice di come avevo iniziato:
  1. Si guardano le transazioni ancora in attesa e si tiene solo quelle col
     selettore 0x6fadcf72 -- il transmit di Chainlink. Misurato: 0,5 al
     minuto, 720 al giorno. Poche: si puo' reagire a TUTTE.
  2. Si prendono i suoi byte firmati (publicnode li da' anche per le
     transazioni in attesa: provato 8 su 8).
  3. Si costruiscono K pacchetti, uno per ciascuna delle K posizioni piu'
     vicine alla soglia, ognuno fatto cosi':
          [ transazione dell'oracolo , nostra liquidazione ]
     Tutti con lo STESSO nonce: ne puo' entrare al massimo uno, e il
     costruttore includera' quello che NON si annulla. Gli altri non
     costano niente.
  4. NON SERVE SAPERE quale prezzo muove quell'aggiornamento. Se non fa
     cadere nessuna delle K, tutti i pacchetti si annullano e si paga ZERO.
     Sapere in anticipo quale asset e' toccato costerebbe tempo e non
     servirebbe: il mercato risponde da solo, gratis.

TRE VOLTE mi sono sbagliato prima di arrivare qui, tutte per DEDUZIONE
invece che per osservazione:
  - lista con tre INDIRIZZI DI GETTONE (RATIO_PROVIDER restituisce il token):
    in 27 minuti ha «beccato» 5 approve e depositi su Lido. Rumore.
  - lista coi contratti di PREZZO: ma gli aggiornamenti non arrivano li',
    arrivano a dei trasmettitori.
  - lista coi trasmettitori osservati: ma Chainlink li RUOTA (21 indirizzi
    diversi in 5 giorni, ognuno visto 1-2 volte), quindi il prossimo ci
    sfuggirebbe. Il selettore invece e' identico per tutti.
"""
import json, os, sys, threading, time, urllib.request
import concurrent.futures as cf
# NOTA: `threading` e' arrivato qui dopo, e la prima volta l'ho dimenticato.
# Il controllo della sintassi passava lo stesso -- un nome mancante e' un
# errore di ESECUZIONE -- e la sentinella sarebbe esplosa esattamente nel
# momento in cui vinceva. Secondo caso identico in un giorno (il primo fu
# blocco_ora in in_acqua.py). La verifica che lo prende non e' leggere il
# file: e' IMPORTARE il modulo e chiedergli se il nome c'e'.
sys.path.insert(0,"agents")
import pescatore as P
import mappa_feed as MF
import occhio_ws as OW
import grezzo_in_casa as GC
import prezzo_nuovo as PN
from invia_pacchetto import TEMPI as _IP_TEMPI
import queue
from invia_pacchetto import flashbots, cast
D="data/liquidazioni"
U="https://ethereum-rpc.publicnode.com"
SELETTORE="0x6fadcf72"          # transmit di Chainlink, osservato su 4 prezzi
# QUANTO OFFRIRE, con TRE tetti e una ragione per ognuno:
#  1. il 10% del premio -- piu' di quanto paga qualunque vincitore misurato
#  2. mai piu' di 45 dollari -- il massimo mai pagato da un vincitore sulle
#     grosse e' 42,88 (misurato sulle 14 piu' grandi degli 88 giorni)
#  3. mai piu' del 60% del saldo operativo -- il gas si paga in anticipo, e
#     su un premio da 413 dollari il 10% sono 41 dollari mentre il
#     portafoglio ne ha 38 in tutto: la transazione fallirebbe per fondi
#     insufficienti. Difetto trovato misurando, non ragionando.
FRAZIONE_PREMIO=0.10
TETTO_DOLLARI=45.0
FRAZIONE_SALDO=0.60
# DA 4 A 12 il 2/11, per la stessa ragione: la posizione caduta non era fra
# le quattro piu' vicine, quindi la sentinella non ha mai composto un
# pacchetto per lei. Comporre costa ~110 ms a testa e si fanno in parallelo:
# dodici pacchetti restano dentro il mezzo secondo. Un pacchetto che si
# annulla non si paga, quindi il solo costo di tenerne piu' e' il tempo.
QUANTE=150
# DA 30 A 150 (5/11). Il tetto di 30 esisteva perche' comporre costava tempo
# nel momento caldo, e costringeva a SCEGLIERE: 15 posti al valore, 15 alla
# vicinanza. Misurato ora: con la fascia a 1,10 le candidate in tutto sono
# 106 -- non migliaia -- e comporne 100 costa 305 ms. Quindi la scelta non
# serve: si portano TUTTE, e il premio in gioco passa da $87.653 a $1.408.284.
# E' la stessa lezione del valore contro la vicinanza, ma risolta meglio:
# invece di decidere QUALE meta' buttare, si smette di buttarne una.
# DA 12 A 30 il 2/11. Misurato: comporre 30 pacchetti costa 87 ms (in
# parallelo) e consegnarli 566 ms -- lo stesso tempo di consegnarne 12,
# perche' partono tutti insieme. Quindi coprire piu' candidate non costa
# tempo: costa solo richieste al relay, che le accetta tutte (12/12 e 30/30
# provati con una transazione VERA come primo elemento).
# NB sulla prova: la prima volta ho usato byte FINTI come transazione
# dell'oracolo e il relay ha rifiutato 0/30 -- stavo per concludere che ci
# limitava. Era la mia prova sbagliata: il relay valida le transazioni del
# pacchetto, quindi il primo elemento deve essere reale.
REG=f"{D}/sentinella.jsonl"
VITA=f"{D}/sentinella_viva.json"
LUCCHETTO=f"{D}/sentinella.lock"
# ARMATA l'1/11, dopo la prova completa su un momento VERO del passato
# (liquidatore/test/MomentoVero.t.sol, blocco 26302299):
#   prima:  ETH $2.202,84  salute 1,005  non liquidabile
#   eseguita la VERA transazione dell'oracolo di quel blocco
#   dopo:   ETH $2.183,54  salute 0,997  CADUTA
#   eseguita la nostra liquidazione -> $8.607 IN CASSA
# E' la prova che intercettare quella transazione e metterla davanti alla
# nostra produce l'incasso. Il vincitore vero prese $12.319; la differenza e'
# che nella prova ho usato uno scambio diretto senza protezione invece
# dell'aggregatore, che in produzione e' migliore.
ARMATA = True
# SI PUO' PROVARE IN SILENZIO. Serve per far attraversare al codice nuovo il
# ramo vero (occhio, grezzo, composizione) accanto alla sentinella armata che
# sta girando, senza il rischio di spedire due volte lo stesso pacchetto.
if os.environ.get("SILENZIOSA") == "1":
    ARMATA = False
def rpc(m,p,t=12):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    try:
        r=urllib.request.Request(U,data=c,headers={
            "content-type":"application/json","user-agent":"Mozilla/5.0"})
        return json.load(urllib.request.urlopen(r,timeout=t))
    except Exception: return None
def mazzo_tx(hashes):
    """I campi di piu' transazioni in una richiesta. ABBINA PER ID."""
    fuori={}
    for i in range(0,len(hashes),25):
        pezzo=hashes[i:i+25]
        corpo=[{"jsonrpc":"2.0","id":j,"method":"eth_getTransactionByHash",
                "params":[h]} for j,h in enumerate(pezzo)]
        try:
            c=json.dumps(corpo).encode()
            r=urllib.request.Request(U,data=c,headers={
                "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=12))
            if not isinstance(d,list): continue
            for e in d:
                j=e.get("id")
                if isinstance(j,int) and j<len(pezzo) and e.get("result"):
                    fuori[pezzo[j]]=e["result"]
        except Exception: pass
    return fuori
FAM={"0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"ETH","0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":"ETH",
"0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"ETH","0xae78736cd615f374d3085123a210448e74fc6393":"ETH",
"0xf1c9acdc66974dfb6decb12aa385b9cd01190e38":"ETH","0xbe9895146f7af43049ca1c1ae358b0541ea49704":"ETH",
"0xa35b1b31ce002fbf2058d22f30f95d405200a15b":"ETH","0xd9a442856c234a39a81a089c06451ebaa4306a72":"ETH",
"0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"BTC","0x8236a87084f8b84306f72007f36f2618a5634494":"BTC",
"0x18084fba666a33d37592fa2633fd49a74dd93a88":"BTC","0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"BTC"}
def _fam(a): return FAM.get((a or "").lower(),"USD")
def candidate(tocca=None):
    """Le K posizioni piu' vicine alla soglia, con la chiamata GIA' PRONTA.
    Senza chiamata pronta non ha senso metterle in un pacchetto: comporla
    costerebbe 90 ms per ciascuna, proprio nel momento in cui contano."""
    # le saluti VIVE pubblicate dal pescatore (se fresche)
    VIVE = {}
    try:
        _sv=json.load(open(f"{D}/saluti_vive.json"))
        if time.time()-_sv.get("quando",0) < 120:
            VIVE={k.lower(): v for k, v in (_sv.get("saluti") or {}).items()}
    except Exception: pass
    try:
        VP=json.load(open(f"{D}/vendite_pronte.json"))
        corta={x["indirizzo"].lower():x for x in json.load(open(f"{D}/lista_corta.json"))}
    except Exception: return []
    out=[]
    # IL CREDITO MORTO NON ENTRA FRA I CANDIDATI, NEANCHE QUI (7/11 sera).
    # Stamattina ho riparato questo nel PESCATORE: una posizione con garanzia
    # zero non e' un'occasione, perche' non c'e' niente da prendere. Ma la
    # sentinella costruisce i candidati per conto suo, dagli ordini pronti e
    # dalla lista corta, e NON guardava la garanzia: quindi continuava a
    # sparare al cadavere.
    # La prova: il motivo dominante delle simulazioni fallite e'
    # InvalidBurnAmount («garanzia da prendere ZERO»), e registrando CHI lo
    # produce e' uscito un solo indirizzo -- 0xae9f7554b9, garanzia $0,0000 e
    # debito $23,70, lo stesso che aveva gia' consumato 37 colpi.
    # Riparazione applicata a un percorso e non all'altro: e' la terza volta
    # oggi. Da ora, quando riparo una regola di SCELTA, cerco TUTTI i posti
    # che scelgono.
    try:
        _comp_g = json.load(open(f"{D}/composizione.json"))
    except Exception:
        _comp_g = {}
    _morti = 0
    for u,v in VP.items():
        if not v.get("chiamata"): continue
        s=corta.get(u.lower())
        if not s: continue
        _cg = _comp_g.get(u) or _comp_g.get(u.lower()) or {}
        if _cg and (_cg.get("garanzia_usd") or 0) < 1:
            _morti += 1
            continue
        # LA SALUTE VIVA, se il pescatore l'ha letta di recente.
        # L'archivio puo' essere vecchio di ore: sulla sconfitta da
        # $947.639 diceva 1,0217 mentre il vero era 1,0054 -- e la
        # differenza decide tutto, perche' un aggiornamento muove lo 0,5%.
        _sv = VIVE.get(u.lower())
        if _sv is not None:
            s = dict(s); s["salute"] = _sv
        # COPPIA UGUALE O DIVERSA: e' la cosa che decide se un movimento di
        # prezzo la fa cadere. Misurato: le coppie diverse cadono l'11,2% in
        # 9 giorni, le uguali lo 0,7%. Una coppia uguale a salute 1,0005 NON
        # cade quando ETH si muove, perche' garanzia e debito si muovono
        # insieme: metterla in un pacchetto speculativo e' un pacchetto
        # sprecato. Prima le DIVERSE, e solo dopo le uguali piu' malate.
        uguale = _fam(v.get("garanzia")) == _fam(v.get("debito"))
        out.append({"utente":u,"salute":s["salute"],"chiamata":v["chiamata"],
                    "premio":v.get("premio",0),"uguale":uguale,
                    "mancia_wei":v.get("mancia_wei") or 0,
                    "garanzia":(v.get("garanzia") or "").lower(),
                    "debito":(v.get("debito") or "").lower()})
    if _morti:
        print(f"   {_morti} posizioni escluse: credito morto, garanzia zero")
    # SOLO CHI E' ESPOSTO ALL'ASSET CHE STA CAMBIANDO PREZZO.
    #
    # SCOPERTA del 4/11 sera, e vale 2.749 eventi di lavoro buttato. Il
    # filtro in mempool prendeva le transazioni col selettore 0x6fadcf72 e
    # registrava `tx.to`: 41 indirizzi distinti, tutti con lo stesso codice.
    # Non erano feed di prezzo -- sono gli AuthorizedForwarder di Chainlink,
    # cioe' gli inoltratori dei singoli operatori, e 0x6fadcf72 e'
    # forward(address,bytes). Registravamo CHI PARLA invece di DI COSA PARLA,
    # e il feed vero stava nel primo argomento della chiamata.
    # Misurato su 120 eventi: solo il 26% tocca un nostro asset (ETH/USD 7
    # volte, AAVE 9, LINK 5, BTC 4, STETH 2). Sul 74% restante i pacchetti
    # non potevano funzionare in nessun caso.
    # Ma il guadagno vero non e' risparmiare pacchetti -- quelli non si
    # pagano se non entrano. E' che quando parla ETH/USD i 27 posti devono
    # andare alle posizioni esposte a ETH, non alle 27 globalmente piu'
    # vicine: altrimenti si manca l'unica che puo' davvero cadere.
    if tocca:
        t=set(tocca)
        esposte=[x for x in out if x["garanzia"] in t or x["debito"] in t]
        # e per queste la coppia "uguale" si rivaluta su cio' che si muove:
        # se cambia solo il prezzo della garanzia, la coppia NON si muove
        # insieme, quindi cade davvero.
        for x in esposte:
            x["uguale"]=(x["garanzia"] in t) and (x["debito"] in t)
        out=esposte
    # NOTA SUL CAMPO "premio": NON e' il valore della posizione, e' quanto
    # riusciamo a INCASSARE, tagliato dal tetto misurato della coppia.
    # Verificato il 4/11: 31 ordini portano premio 130.841,12 identico pur
    # avendo debiti veri da $6,1M a $25,3M -- sembrava una costante presa
    # per un dato di riga, ed e' invece il tetto di vendita di osETH->WETH.
    # E' il numero giusto per scegliere (non serve a niente puntare a un
    # premio che non possiamo vendere), ma fra premi PARI l'ordine lo deve
    # decidere la salute, perche' il valore non distingue piu'.
    # SI SCEGLIE PER VALORE, non solo per vicinanza.
    #
    # DIFETTO PAGATO il 4/11, ed e' la STESSA RADICE del difetto della
    # corsia del pescatore: due pezzi diversi che scelgono per prossimita'
    # e ignorano quanto vale. Ci sono costati la stessa liquidazione.
    # Misurato: su 37 volte che abbiamo intercettato l'oracolo del blocco
    # vincente, la posizione da $130.841 di premio era nei nostri 30
    # pacchetti solo 15 VOLTE. Nelle altre 22 veniva scartata in favore di
    # posizioni piu' vicine alla soglia ma da 200 dollari.
    # Quando c'era offrivamo 5,601 gwei e il vincitore ha pagato ZERO:
    # quindi non abbiamo perso sull'offerta, abbiamo perso perche' nel
    # pacchetto di quel momento non c'eravamo.
    #
    # LA REGOLA, e vale in tutto il sistema: un posto in una lista limitata
    # si assegna per quanto vale il caso, non per quanto e' vicino. La
    # vicinanza dice QUANDO, il valore dice QUANTO -- e con trenta posti su
    # mille candidate, scegliere il quando e buttare il quanto significa
    # riempire il pacchetto di spiccioli.
    #
    # Si tengono comunque le coppie diverse davanti a parita' di valore:
    # una coppia uguale non cade quando l'oracolo muove ETH, quindi in un
    # pacchetto speculativo e' un posto sprecato.
    # I PIU' PREZIOSI SEMPRE: i primi QUANTE_RICCHE posti vanno alle
    # candidate col premio piu' alto, qualunque sia la loro salute; il
    # resto si riempie come prima, per vicinanza.
    # DENTRO IL PACCHETTO SOLO CHI E' ALLA PORTATA DI UN AGGIORNAMENTO.
    # Misurato il 4/11: un aggiornamento muove lo 0,507% in mediana e lo
    # 0,585% al massimo, quindi serve salute sotto ~1,006. Si lascia un po'
    # di margine (1,012, il doppio del massimo visto) perche' due
    # aggiornamenti possono arrivare vicini, ma non oltre: una posizione a
    # 1,13 nel pacchetto e' un posto buttato.
    # LA PORTATA SI RICAVA DALLE CADUTE VERE, NON DA UN MODELLO.
    # (riparato il 5/11 dopo averla sbagliata io stesso)
    #
    # L'avevo messa a 1,012 ragionando cosi': un singolo aggiornamento muove
    # lo 0,507% in mediana, quindi puo' cadere solo chi sta sotto ~1,006. Il
    # ragionamento era giusto e la DOMANDA sbagliata: le posizioni non cadono
    # per un solo aggiornamento, cadono per movimenti accumulati, per gli
    # interessi che maturano e per piu' asset che si muovono insieme.
    #
    # Misurato su 40 liquidazioni VERE, salute registrata un'ora prima:
    #   mediana 1,0196 | 90esimo 1,0301 | massimo 1,0534
    #   portata 1,012 -> cattura il 32,5% delle cadute, il 24,4% del premio
    #   portata 1,030 -> 90,0% delle cadute, 84,3% del premio
    #   portata 1,060 -> 100% delle cadute, 100% del premio
    #
    # E LA PROVA CHE MI HA SMASCHERATO: la liquidazione da 509.058 $ del 4/11
    # -- l'unica che valesse qualcosa in 24 ore -- stava nei nostri pacchetti
    # 1.140 volte su 2.911, con salute fra 1,0153 e 1,0505. Col filtro a
    # 1,012 l'avremmo scartata 1.140 volte su 1.140.
    # Un modello che contraddice una caduta osservata ha torto il modello.
    # SECONDA CORREZIONE DELLA FASCIA (5/11), e sbaglio per la SECONDA volta
    # nella stessa direzione: troppo stretta.
    # Era 1,012, tarata su quanto muove UN aggiornamento (0,507% mediano): la
    # sconfitta da $947.639 stava a 1,0153-1,0505 e veniva esclusa. Portata a
    # 1,06 su 40 cadute vere. Ora le 8 cadute di cui conosciamo la salute
    # precedente dicono che 1,06 e' ancora stretta:
    #   1,0274  1,0395  1,0471  1,0557  1,0588  1,0632  1,0804  1,0821
    #   fascia 1,06 -> 5 cadute su 8 e $1.181 su $6.012: butta l'80% del premio
    #   fascia 1,09 -> 8 su 8 e tutto il premio
    # Due delle tre perse per distanza 2 ($2.700 e $1.005) erano a 1,0804 e
    # 1,0821: non sono state scartate nella scelta, non ci sono MAI ARRIVATE.
    # E intanto nel pacchetto stavano posizioni da $16.
    # Si prende 1,10 e non 1,09: fermarsi esatto sul massimo osservato e'
    # tararsi sul campione. Allargare non costa, un pacchetto che non entra
    # non si paga; costa POSTI, ed e' per questo che insieme sale QUANTE.
    # LA REGOLA, scritta per la seconda volta: un modello che contraddice una
    # caduta OSSERVATA e' sbagliato, e il verso dell'errore e' sempre lo
    # stesso -- dedurre il limite della realta' dal limite della mia misura.
    PORTATA = 1.10
    a_tiro = [x for x in out if x["salute"] < PORTATA]
    if a_tiro:
        out = a_tiro
    # TETTO PER COPPIA: nessuna coppia si prende piu' di TETTO_COPPIA posti.
    #
    # MISURATO SUL LIVE il 5/11, prima autopsia vera: delle 5 liquidazioni
    # avvenute da quando il contratto e' giusto, 3 (l'82% del premio) erano
    # a DISTANZA 2 -- avevamo l'ordine pronto e la posizione NON era fra le
    # 30 spedite. Guardando i 30 posti: 22 su 30 (il 73%) andavano a UNA
    # SOLA coppia, weETH->WETH, con premio tagliato dal tetto di vendita e
    # salute ferma da giorni senza cadere. Le 5 cadute vere stavano in
    # classifica al 295esimo, 375esimo, 399esimo, 550esimo e 560esimo posto.
    #
    # La causa e' che ordinare per PREMIO, quando il premio e' tagliato dal
    # tetto di vendita, mette in cima decine di posizioni col MEDESIMO
    # valore: non e' una classifica, e' un plateau che soffoca la coda utile.
    # (Astra e Grok, consultati sui dati, dicono la stessa cosa.)
    #
    # Il tetto per coppia e' la riparazione minima che tocca il fatto
    # misurato. La classifica per valore atteso -- premio reale per
    # probabilita' di cadere -- e' nel registro delle idee: vale di piu' ma
    # richiede una stima di probabilita' per asset che non ho ancora.
    # IL TETTO PER COPPIA SERVE SOLO SE I POSTI SONO SCARSI (5/11).
    # Con 30 posti e 106 candidate una coppia sola se ne prendeva 22 su 30, e
    # il tetto era la riparazione giusta. Con 150 posti e 106 candidate non
    # c'e' niente da spartire: il tetto escluderebbe posizioni senza che
    # nessun'altra ne guadagni un posto. Si applica solo quando stringe.
    TETTO_COPPIA = 6 if len(out) > QUANTE else 10**6
    QUANTE_RICCHE = max(8, QUANTE // 2)
    diverse = [x for x in out if not x["uguale"]]
    diverse.sort(key=lambda x: -x["premio"])
    quante_per_coppia = {}
    ricche = []
    for x in diverse:
        k = (x.get("garanzia"), x.get("debito"))
        if quante_per_coppia.get(k, 0) >= TETTO_COPPIA:
            continue
        quante_per_coppia[k] = quante_per_coppia.get(k, 0) + 1
        ricche.append(x)
        if len(ricche) >= QUANTE_RICCHE:
            break
    presi = {x["utente"] for x in ricche}
    resto = [x for x in out if x["utente"] not in presi]
    resto.sort(key=lambda x:(1 if x["uguale"] else 0, x["salute"]))
    # anche il resto rispetta il tetto, altrimenti la coppia dominante
    # rientra dalla porta della vicinanza
    scelte = list(ricche)
    for x in resto:
        if len(scelte) >= QUANTE:
            break
        k = (x.get("garanzia"), x.get("debito"))
        if quante_per_coppia.get(k, 0) >= TETTO_COPPIA:
            continue
        quante_per_coppia[k] = quante_per_coppia.get(k, 0) + 1
        scelte.append(x)
    return scelte[:QUANTE]
def saldo_operativo():
    """Quanto ETH ha il portafoglio che paga il gas. Si legge una volta."""
    try:
        ind=cast("wallet","address","--private-key",P.CHIAVE)
        d=rpc("eth_getBalance",[ind,"latest"])
        return int((d or {}).get("result","0x0"),16)/1e18
    except Exception: return None
SALDO_ETH=None
# IL MAGAZZINO DELLE FIRME PRONTE. Chiave: (utente, nonce, priority,
# calldata) -- se uno qualunque cambia, la firma vecchia non vale piu'.
_magazzino_firme = {}
# CHI HA GIA' FALLITO LA SIMULAZIONE, e quante volte (6/11).
#
# MISURATO: negli ultimi 40 colpi la posizione 0xaf6e0473f8 ($130.841, salute
# 1,000746) si e' presa il colpo 13 volte -- un terzo -- e la simulazione dice
# che NON FUNZIONA MAI (1.599 rifiuti HealthFactorNotBelowThreshold su 2.217
# pacchetti). E' una posizione DIFESA: sta a 1,0007 da giorni e chi la tiene
# la riaggiusta. La mia stima la dichiara caduta perche' e' lineare e lei e'
# multi-asset; la catena la rifiuta ogni volta.
# Da quando mandiamo UN SOLO pacchetto, una posizione cosi' monopolizza il
# colpo e lo spreca. E non serve indovinare: la prova e' nei NOSTRI dati, la
# simulazione la produce da ore e non la stavamo usando.
# Quindi: fra due candidate che la stima dichiara cadute, va davanti quella
# che NON ha una storia di rifiuti. Non si esclude nessuno per sempre -- se
# un giorno cade davvero la vogliamo -- si mette solo in fondo.
_CASTIGO = f"{D}/rifiuti_simulati.json"
try:
    _RIFIUTI_SIMULATI = {k: int(v) for k, v in json.load(open(_CASTIGO)).items()}
except Exception:
    _RIFIUTI_SIMULATI = {}
def _quanti_rifiuti(utente):
    return _RIFIUTI_SIMULATI.get((utente or "")[:12], 0)
def _salva_castigo():
    """IL CASTIGO SOPRAVVIVE AL RIAVVIO. Senza questo, ogni riaccensione
    ricomincia a sprecare colpi per reimparare la stessa cosa -- e la
    sentinella si riavvia spesso. Una lezione ricordata vale un giro solo;
    una lezione SCRITTA vale tutti quelli dopo."""
    try:
        t = _CASTIGO + ".tmp"
        with open(t, "w") as f: json.dump(_RIFIUTI_SIMULATI, f)
        os.replace(t, _CASTIGO)
    except OSError:
        pass
_usate_dal_magazzino = [0]
_firmate_al_volo = [0]
def riempi_magazzino(quante=40):
    """Firma in anticipo le candidate piu' ricche. Gira in sottofondo, fuori
    dalla finestra che conta. Ritorna quante firme ci sono in magazzino."""
    try:
        testa, nonce = P._testa_e_nonce()
        cands = candidate()
    except Exception:
        return len(_magazzino_firme)
    if nonce is None:
        return len(_magazzino_firme)
    # un nonce nuovo invalida TUTTO: le firme vecchie sono byte morti, ed e'
    # esattamente il tipo di cosa che un sistema «funzionante» spedisce in
    # silenzio (12.000 pacchetti col selettore sbagliato, 4/11).
    for k in [k for k in _magazzino_firme if k[1] != nonce]:
        del _magazzino_firme[k]
    cands = sorted(cands, key=lambda c: -(c.get("premio") or 0))[:quante]
    # SI POTANO LE CHIAVI SUPERATE (6/11). Gli ordini si rigenerano in
    # continuo -- 100 per passata -- e quando la calldata cambia la firma in
    # magazzino non combacia piu': misurato, il magazzino veniva usato 4
    # volte su 8 e le altre 4 si firmava al volo a 300-400 ms, cioe' il
    # guadagno spariva meta' delle volte. Le chiavi morte non servono a
    # niente e fanno credere che il magazzino sia pieno.
    _vive = {(c["utente"], nonce, int(0.05*1e9), c.get("chiamata"))
             for c in cands if c.get("mancia_wei")}
    for k in [k for k in _magazzino_firme if k not in _vive]:
        del _magazzino_firme[k]
    def una(c):
        pri_wei = int(0.05*1e9) if c.get("mancia_wei") else None
        if pri_wei is None:
            return None          # senza offerta la priority dipende dal premio
        k = (c["utente"], nonce, pri_wei, c.get("chiamata"))
        if k in _magazzino_firme: return None
        raw = cast("mktx", P.CONTRATTO, c["chiamata"], "--private-key", P.CHIAVE,
                   "--gas-limit", str(P.gas_per_piano(c.get("chiamata"))),
                   # LO STESSO TETTO ALTO del percorso diretto: se le due
                   # vie usassero tetti diversi, la firma pronta sarebbe
                   # inutilizzabile appena il gas sale -- due meccanismi
                   # giusti che insieme fanno un danno.
                   "--gas-price", str(max(pri_wei + int(2e9),
                       min(int((SALDO_ETH or 0.04)*1e18*0.85
                               / max(P.gas_per_piano(c.get("chiamata")),1)),
                           int(24e9)))),
                   "--priority-gas-price", str(pri_wei), "--nonce", str(nonce),
                   "--chain", "1")
        if raw.startswith("0x"): _magazzino_firme[k] = raw
        return None
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        list(ex.map(una, cands))
    return len(_magazzino_firme)
def pacchetto(oracolo_raw, cand, testa, nonce, prezzo_eth):
    """Un pacchetto: prima l'oracolo, poi la nostra liquidazione."""
    pri=P.GUADAGNO_MINIMO_USD  # segnaposto; la priorita' la calcola invia_pacchetto
    gwei=2.0
    # SE L'ORDINE PORTA LA MANCIA, LA PRIORITY SCENDE AL MINIMO.
    #
    # Misurato il 5/11: il saldo operativo (0,0163 ETH) copre 9,31 gwei in
    # tutto su 1.750.000 di gas. Spendendone 5,59 di priority restava spazio
    # per una base fee di soli 3,72 gwei, e la base fee sale proprio quando
    # c'e' volatilita', cioe' quando arrivano le liquidazioni: la nostra
    # prontezza crollava nel momento in cui serve.
    # E quella priority ora non compra NIENTE: chi costruisce guarda il
    # valore totale del blocco, e la mancia dal ricavato (4.244 $ su un
    # premio da 42.348) e' 180 volte la priority (23,69 $). Pagare due volte
    # la stessa cosa, una delle quali col denaro scarso, e' solo spreco.
    # ONESTA' SULLA MISURA: nelle ultime 8 ore la base fee non ha mai
    # superato 1,3 gwei, quindi oggi quel rischio NON c'era e il mio allarme
    # era esagerato. Ma il campione non conteneva nessun momento di stress,
    # cioe' proprio il caso temuto: non risponde alla domanda. La riparazione
    # resta giusta perche' togliere uno spreco e' giusto comunque.
    # Sui debiti NON in WETH la mancia non si puo' pagare, e li' la priority
    # resta l'unica offerta che abbiamo: per quelli non si cambia niente.
    if cand.get("mancia_wei"):
        gwei = 0.05                      # il minimo per essere accettati
    elif prezzo_eth and cand["premio"]:
        bersaglio=min(cand["premio"]*FRAZIONE_PREMIO, TETTO_DOLLARI)
        if SALDO_ETH: bersaglio=min(bersaglio, SALDO_ETH*FRAZIONE_SALDO*prezzo_eth)
        gwei=max(0.1, bersaglio/(P.gas_per_piano(cand.get("chiamata"))*1e-9*prezzo_eth))
    # IN WEI INTERI, non in gwei con la virgola. DIFETTO 1/11: l'offerta
    # calcolata dal premio veniva fuori "12.16gwei" e `cast` la rifiutava --
    # il comando falliva in 8 millisecondi e la sentinella componeva ZERO
    # pacchetti su 20 aggiornamenti beccati. Rilevava e non sparava, e il
    # campo "pacchetti: 0" nel registro e' l'unica cosa che l'ha rivelato.
    pri_wei=int(gwei*1e9)
    # IL TETTO SI ALZA QUANTO IL PORTAFOGLIO PERMETTE (6/11, difetto grave).
    #
    # Era FISSO a priority + 2 gwei = 2,05 gwei. La base fee stamattina e'
    # passata da 0,19 a 1,65 gwei in due ore: era gia' all'80% del nostro
    # tetto. Se raddoppiava ancora -- ed e' esattamente cio' che fa nei
    # grappoli, cioe' QUANDO ARRIVANO I SOLDI -- le nostre transazioni
    # diventavano INAMMISSIBILI: veloci, prezzate bene, e fuori gara in
    # silenzio nel momento che aspettiamo da 32 ore.
    #
    # E alzarlo non costa NIENTE: su Ethereum maxFeePerGas non e' quello che
    # paghi, e' il massimo che accetti di pagare. Si paga base fee +
    # priority. Il tetto serve solo a non farsi escludere.
    # L'unico vincolo vero e' che il portafoglio copra maxFee x gas, perche'
    # altrimenti la transazione non e' nemmeno valida. Con 0,0415 ETH e
    # 1.450.000 di gas il massimo possibile e' ~28 gwei: si usa l'85% di
    # quello, cosi' resta margine per piu' di un tentativo.
    # Cosi' il tetto e' FISSO e ALTO, quindi le firme si possono ancora
    # preparare in anticipo: niente da rifirmare quando il gas si muove.
    _gas = P.gas_per_piano(cand.get("chiamata"))
    _tetto_dal_saldo = int((SALDO_ETH or 0.04) * 1e18 * 0.85 / max(_gas, 1))
    max_wei = max(pri_wei + int(2e9), min(_tetto_dal_saldo, int(24e9)))
    # LA FIRMA SI CERCA PRIMA NEL MAGAZZINO (6/11).
    #
    # `cast mktx` e' un AVVIO DI PROCESSO, e misurato costa 346-901 ms per un
    # solo pacchetto. La finestra utile fra l'apparire dell'aggiornamento e
    # la chiusura del blocco e' 80-250 ms: la firma da sola la sforava.
    # Non si puo' firmare piu' in fretta, ma si puo' firmare PRIMA: i
    # parametri sono tutti noti in anticipo (la calldata sta nell'ordine, il
    # nonce e' lo stesso per tutte, e da quando l'offerta si paga dal
    # ricavato la priority e' fissa a 0,05 gwei). Un filo in sottofondo
    # riempie il magazzino; qui si prende e si spedisce.
    # Se il magazzino non ha quella firma -- ordine nuovo, nonce appena
    # cambiato -- si firma qui come prima: piu' lento, ma mai muti.
    nostra = _magazzino_firme.get((cand["utente"], nonce, pri_wei,
                                   cand.get("chiamata")))
    if nostra:
        _usate_dal_magazzino[0] += 1
    else:
        _firmate_al_volo[0] += 1
        nostra=cast("mktx",P.CONTRATTO,cand["chiamata"],"--private-key",P.CHIAVE,
                    "--gas-limit",str(P.gas_per_piano(cand.get("chiamata"))),
                    "--gas-price",str(max_wei),
                    "--priority-gas-price",str(pri_wei),"--nonce",str(nonce),
                    "--chain","1")
    if not nostra.startswith("0x"): return None
    # SU TRE BLOCCHI, NON UNO (5/11). Il pacchetto valeva solo per testa+1:
    # se l'aggiornamento dell'oracolo entrava un blocco dopo -- e il momento
    # in cui lo sentiamo non decide quando entra -- il nostro pacchetto era
    # gia' scaduto e perdevamo DOPO aver sentito la campanella. Mandarlo
    # anche per testa+2 e testa+3 non costa niente: se l'oracolo e' gia'
    # entrato il pacchetto e' semplicemente invalido e nessuno lo include.
    # Il pescatore lo faceva da sempre; la sentinella, che e' quella che
    # compete, no.
    corpi=[{"txs":[oracolo_raw,nostra],"blockNumber":hex(testa+k)}
           for k in (1,2,3)]
    return {"corpo":corpi[0],"corpi":corpi,
            "gwei":round(gwei,3),"utente":cand["utente"],
            "salute":cand["salute"],"premio":cand["premio"],
            "uguale":cand.get("uguale")}
def controlla_esito(pacchi):
    """Il pacchetto e' entrato nel blocco? E se si', AVVISA.

    Gira in un filo di fondo: non deve rallentare la consegna, ma deve
    esistere. L'hash di una transazione firmata e' keccak dei suoi byte,
    quindi si puo' calcolare senza chiedere niente a nessuno.

    Se una e' entrata: si verifica la cassa, si manda l'email e si scrive il
    flag della presa -- che e' quello che fa fermare sia la sentinella sia
    il pescatore. Prima si verifica, POI si avvisa: e' la regola di Nicolo'
    («non fammi prendere un colpo»), e vale anche qui.
    """
    import subprocess
    hash_di={}
    for p in pacchi:
        try:
            grezza=p["corpo"]["txs"][1]
            h=cast("keccak",grezza)
            if h.startswith("0x"): hash_di[h]=p
        except Exception: pass
    if not hash_di: return
    for _ in range(25):                       # ~75 secondi, 6 blocchi
        time.sleep(3)
        for h,p in list(hash_di.items()):
            rc=(rpc("eth_getTransactionReceipt",[h]) or {}).get("result")
            if not rc: continue
            riuscita = str(rc.get("status")) in ("0x1","1")
            print(f"   >>> PACCHETTO INCLUSO: {h[:14]} "
                  f"{'RIUSCITO' if riuscita else 'annullato'} <<<")
            if not riuscita:
                del hash_di[h]; continue
            try:
                with open(f"{D}/preso.flag","w") as g:
                    g.write(json.dumps({
                        "quando":time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()),
                        "chi":"sentinella","utente":p["utente"],
                        "transazione":h,"premio_atteso_usd":p["premio"]}))
            except OSError: pass
            try:
                from conferma_e_avvisa import dopo_la_liquidazione
                co=json.load(open(f"{D}/composizione.json"))
                c=co.get(p["utente"]) or {}
                dopo_la_liquidazione(c.get("debito_principale"), p["utente"], h,
                    p["premio"], p["premio"]/0.07,
                    garanzia=str(c.get("garanzia_principale"))[:10])
                print("   email mandata dopo aver verificato la cassa")
            except Exception as e:
                print(f"   AVVISO FALLITO: {str(e)[:120]}")
            return
    return
def main():
    # IL LUCCHETTO esiste perche' due sentinelle ARMATE spedirebbero lo stesso
    # pacchetto due volte (ne trovai quattro insieme il 4/11). Una prova in
    # SILENZIO non spedisce niente, quindi puo' convivere con quella armata --
    # ed e' il solo modo di far attraversare il codice nuovo al ramo vero
    # senza spegnere prima quello che sta sorvegliando.
    if os.path.exists(LUCCHETTO) and ARMATA:
        try:
            altro=int(open(LUCCHETTO).read().strip()); os.kill(altro,0)
            print(f"   un'altra sentinella e' viva (pid {altro}): non parto")
            return
        except Exception: pass
    try:
        if ARMATA: open(LUCCHETTO,"w").write(str(os.getpid()))
    except OSError: pass
    import atexit
    atexit.register(lambda: os.path.exists(LUCCHETTO) and os.remove(LUCCHETTO))
    MINUTI=float(sys.argv[1]) if len(sys.argv)>1 else 30
    print(f"   SENTINELLA — {'ARMATA' if ARMATA else 'SILENZIOSA: compone e simula, non spedisce'}")
    print(f"   cerco il selettore {SELETTORE} per {MINUTI} minuti\n")
    fid=(rpc("eth_newPendingTransactionFilter",[]) or {}).get("result")
    if not fid: print("   filtro non creato"); return
    pe=P.PR.get("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",{}).get("prezzo_usd")
    global SALDO_ETH
    SALDO_ETH=saldo_operativo()
    print(f"   saldo operativo {SALDO_ETH:.6f} ETH = ${(SALDO_ETH or 0)*(pe or 0):,.2f}"
          f" -> offerta massima ${min(TETTO_DOLLARI,(SALDO_ETH or 0)*FRAZIONE_SALDO*(pe or 0)):,.2f}")
    t0=time.time(); viste=0; giri=0; becchi=0; composti=0; utili=0; accettati_tot=0
    # UN CONTATORE PER OGNI STADIO, COL SUO NOME: un numero chiamato
    # "composti" mentre significava "accettati" ci ha fatto sembrare una
    # simulazione un guasto totale per 660 pacchetti.
    nostri_feed=0; non_nostri=0; senza_esposte=0
    NOSTRI={k.lower() for k in P.AMMESSI}
    try:
        for _x in json.load(open(f"{D}/vendite_pronte.json")).values():
            for _k in ("garanzia","debito"):
                if _x.get(_k): NOSTRI.add(_x[_k].lower())
    except Exception: pass
    MF.simboli(NOSTRI)
    # L'OCCHIO LARGO (5/11, dopo l'ottava liquidazione persa).
    #
    # MISURATO: il solo filtro HTTP sentiva l'8% degli aggiornamenti
    # dell'oracolo -- 8 su 96 nei 41 blocchi del grappolo -- e gli 8 che hanno
    # fatto cadere le posizioni non li ha sentiti NESSUNO. Il co-pacchetto
    # [oracolo, nostra liquidazione] era gia' costruito e giusto: si innescava
    # sull'8% sbagliato. Una posizione e' liquidabile solo nell'istante in cui
    # arriva il prezzo nuovo, e in un blocco c'e' UNA sola casella buona,
    # quella subito dopo quel prezzo: 8 vincitori su 8 stavano esattamente li'.
    # Non abbiamo perso la gara, non sapevamo che era iniziata.
    #
    # Il difetto sta nel MODO di guardare: eth_getFilterChanges restituisce
    # solo cio' che e' passato fra due interrogazioni e perde il resto. Ora si
    # ascolta da 3 porte websocket in parallelo PIU' il filtro HTTP, e la
    # copertura e' l'UNIONE: una porta in piu' non puo' far scendere il
    # numero. Contare "quanti ne vedo" era lo stadio sbagliato; quello giusto
    # e' "quale frazione di quelli che esistono", e il denominatore sta solo
    # in catena (agents/misura_occhio.py).
    coda=queue.Queue(); _fermo=[]; _porte_cadute={}
    def _caduta(u,e):
        # UNA FINESTRA CHIUSA IN SILENZIO e' il guasto che ci e' costato 8
        # liquidazioni su 8: si grida e si conta.
        _porte_cadute[u]=str(e)[:80]
        print(f"   PORTA CADUTA {u.split('//')[-1][:30]}: {str(e)[:60]}")
    OW.ascolta_tutte(lambda tx,porta: coda.put((tx,porta,time.monotonic())),
                     selettore=SELETTORE,
                     ferma=lambda: bool(_fermo), su_errore=_caduta)
    # IL SECONDO OCCHIO, da un fornitore DIVERSO (7/11).
    # Perche': il censimento di 30 porte gratuite col criterio giusto --
    # consegna un dizionario col campo input? -- ne ha fatta passare UNA,
    # publicnode (il suo secondo nome risolve agli stessi IP, quindi era un
    # fornitore solo). Ed e' caduto 2 volte in 5 ore. Un occhio solo
    # sull'unica cosa che decide se vinciamo.
    # Alchemy filtra LATO SERVER per indirizzo di destinazione: ci manda ~37
    # messaggi l'ora invece di ~43.000, quindi non aggiunge carico al filo
    # caldo -- lo togliamo. Il filtro e' obbligatorio e il modulo si rifiuta
    # di sottoscrivere senza (senza filtro: ~$640 al mese invece di zero).
    # La deduplicazione e' a valle, per hash, quindi due fonti nella stessa
    # coda non fanno comporre due volte lo stesso pacchetto.
    # Se non parte, si GRIDA e si continua con un occhio: un ripiego
    # silenzioso su una cosa indispensabile e' una bugia, ma fermare la
    # sentinella perche' manca la seconda fonte sarebbe peggio del problema.
    _alchemy_viva = [False]
    try:
        import occhio_alchemy as OA
        _ind_al = OA.destinatari()
        if not OA.chiavi.alchemy():
            print("   SECONDO OCCHIO SPENTO: chiave Alchemy assente "
                  "(sezione === ALCHEMY === nel file delle credenziali)")
        elif not _ind_al:
            print("   SECONDO OCCHIO SPENTO: nessun indirizzo da filtrare, "
                  "mi rifiuto di sottoscrivere senza filtro")
        else:
            def _occhio_due():
                try:
                    OA.ascolta(lambda tx, _p: coda.put(
                                   (tx, "alchemy", time.monotonic())),
                               ferma=lambda: bool(_fermo),
                               indirizzi=_ind_al)
                except Exception as _e:
                    print(f"   SECONDO OCCHIO CADUTO: {str(_e)[:90]}")
                    _alchemy_viva[0] = False
            threading.Thread(target=_occhio_due, daemon=True).start()
            _alchemy_viva[0] = True
            _cu, _fr, _ = OA.stato_consumo()
            print(f"   SECONDO OCCHIO ACCESO: alchemy, filtro su "
                  f"{len(_ind_al)} indirizzi, consumo del mese "
                  f"{_fr*100:.2f}% del gratuito")
    except Exception as _e:
        print(f"   SECONDO OCCHIO NON AVVIATO: {str(_e)[:90]}")
    gia_fatti=set(); dal_ws=0; dal_http=0; grezzi_in_casa=0; grezzi_da_rete=0
    _primo_arrivo={}; _prime_porta={}; _ritardo_porta={}
    _ultimo_filtro=[0.0]
    # IL FILO CHE RIEMPIE IL MAGAZZINO DELLE FIRME, in sottofondo.
    # Gira ogni 30 secondi: cosi' quando arriva la campanella la firma c'e'
    # gia' e comporre costa ZERO invece di 346-901 ms.
    def _rifornisci():
        while True:
            try:
                # TUTTE, non le 40 piu' ricche (6/11).
                # Pre-firmavamo le 40 col premio piu' alto, ma la scelta al
                # momento della campanella cade sulla piu' ricca FRA QUELLE
                # CHE CADONO -- che spesso non e' fra le 40 piu' ricche in
                # assoluto. Misurato: magazzino usato 1 volta su 5, le altre
                # 4 firmate al volo a 346-901 ms, cioe' il guadagno svaniva
                # proprio nei casi veri.
                # Le candidate in fascia sono ~150 e firmarle tutte costa
                # ~1 secondo in sottofondo: non c'e' ragione di scegliere.
                n=riempi_magazzino(400)
            except Exception as e:
                print(f"   magazzino firme: {str(e)[:70]}")
            # OGNI 8 SECONDI, non 30. Costa quasi niente quando non c'e'
            # niente di nuovo (le chiavi gia' presenti si saltano), e la
            # calldata degli ordini cambia in continuo: un magazzino
            # rifornito ogni 30 secondi era vecchio meta' delle volte.
            # NON si scende sotto: firmare e' un sottoprocesso, e il 4/11
            # dei sottoprocessi in eccesso hanno reso il pescatore cieco al
            # 25% rubandogli la macchina. Dopo ogni propagazione va guardato
            # l'effetto su chi non ho toccato.
            time.sleep(8)
    threading.Thread(target=_rifornisci, daemon=True).start()
    # E IL FILO CHE TIENE CALDE LE CONNESSIONI VERSO I COSTRUTTORI.
    # A freddo la consegna costa 369/117/95/67 ms per porta, a caldo
    # 125/47/29/27: la differenza fra essere dentro la finestra di 80-250 ms
    # e essere fuori. I costruttori chiudono le connessioni inattive, e una
    # connessione chiusa si scopre solo quando serve -- nel momento peggiore.
    from invia_pacchetto import tieni_calde as _tieni_calde
    threading.Thread(target=_tieni_calde, daemon=True).start()
    # E LA TESTA DELLA CATENA SEMPRE FRESCA (6/11).
    #
    # P._testa_e_nonce() e' in cache per 24 secondi, ma quando scade costa
    # 262 ms -- e quel costo cadeva DENTRO la finestra, perche' le campanelle
    # arrivano ogni pochi minuti e la cache era scaduta quasi sempre. Era il
    # termine dominante rimasto: spiega i 90-281 ms del «comporre» anche
    # quando la firma viene dal magazzino.
    # E sotto c'era un difetto peggiore della lentezza: una testa vecchia di
    # 24 secondi sono DUE BLOCCHI indietro, quindi puntavamo a testa+1 quando
    # quel blocco era gia' stato sigillato -- un pacchetto perfetto spedito a
    # un blocco che non esiste piu'. Un valore in cache non e' sbagliato
    # perche' e' lento: e' sbagliato perche' e' vecchio.
    def _testa_sempre_fresca():
        while True:
            try:
                P._testa_e_nonce(validita=0)   # forza la rilettura
            except Exception:
                pass
            time.sleep(4)
    threading.Thread(target=_testa_sempre_fresca, daemon=True).start()
    # TUTTI I PREZZI VECCHI IN CODA SUBITO, non uno per campanella.
    # Misurato: 13 campanelle di fila su 13 feed DIVERSI, quindi il filtro
    # delle cadute non si accendeva mai. Gli aggregatori Chainlink sono
    # decine e li conosciamo gia' (nomi_feed.json): si scaldano tutti in
    # sottofondo in pochi secondi.
    try:
        _in_coda = PN.scalda_tutti(
            lambda f:(lambda r:int(r,16) if r and r!="0x" else None)(
                (rpc("eth_call",[{"to":f,"data":"0x50d25bcd"},"latest"]) or {}).get("result")))
        print(f"   metto a scaldare {_in_coda} prezzi vecchi conosciuti")
    except Exception as _e:
        print(f"   non ho potuto scaldare i prezzi: {str(_e)[:80]}")
    cadute_previste=0; senza_cadute=0
    while time.time()-t0 < MINUTI*60:
        giri+=1
        # UNA SOLA presa, come il pescatore: dopo la prima ci si ferma e si
        # guarda cos'e' successo, invece di continuare a sparare.
        if os.path.exists(f"{D}/preso.flag"):
            print("   presa gia' avvenuta: mi fermo"); break
        # PRIMA le porte websocket: danno la transazione INTERA, quindi il
        # selettore si legge senza una seconda richiesta -- il giro di rete
        # che prima costava ~90 ms proprio nel momento in cui si corre.
        arrivi={}
        try:
            while True:
                _v=coda.get_nowait()
                # CHI ARRIVA PRIMA, MISURATO DOVE SI PUO' MISURARE (7/11).
                # Avevo provato a confrontare Alchemy e publicnode
                # incrociando il registro su file: impossibile, perche' il
                # registro scrive l'ora come "09:11:56", risoluzione UN
                # SECONDO, mentre il vantaggio da misurare e' di decine di
                # millisecondi. Stavo costruendo una misura che non poteva
                # rispondere, e l'ho scoperto solo dopo averla fatta girare
                # mezz'ora e averla fatta morire su un errore di tipo.
                # La misura giusta sta QUI: due fonti dentro lo stesso
                # processo, un solo orologio monotono, la differenza fra il
                # primo e il secondo arrivo dello STESSO hash.
                tx,_porta,_t = _v if isinstance(_v,tuple) else (_v,"?",0.0)
                hh=(tx.get("hash") or "").lower()
                if hh:
                    _p0=_primo_arrivo.get(hh)
                    if _p0 is None:
                        _primo_arrivo[hh]=(_porta,_t)
                        _prime_porta[_porta]=_prime_porta.get(_porta,0)+1
                    else:
                        _pp,_tt=_p0
                        if _porta!=_pp and _t>_tt:
                            _l=_ritardo_porta.setdefault(_porta,[])
                            if len(_l)<400: _l.append((_t-_tt)*1000)
                if len(_primo_arrivo)>20000:
                    for _k in list(_primo_arrivo)[:8000]: del _primo_arrivo[_k]
                if hh and hh not in gia_fatti:
                    arrivi[hh]=tx; dal_ws+=1
        except queue.Empty: pass
        # POI il filtro HTTP, che NON si butta: sente poco ma sente cose sue,
        # e l'unione non puo' che crescere.
        # IL FILTRO HTTP SI INTERROGA OGNI 2 SECONDI, NON A OGNI GIRO (6/11).
        #
        # Girava senza pausa (sleep 0.05 quando non c'era niente): ~1.200
        # richieste al minuto a publicnode. E publicnode e' l'UNICA delle tre
        # fonti che accetta le interrogazioni sui registri -- drpc e blastapi
        # rispondono 400 -- cioe' e' l'unica che puo' certificare il
        # contatore delle liquidazioni. Risultato misurato: 429 Too Many
        # Requests, e il contatore ha detto «non lo so» due giri di fila.
        # Il contatore e' il modo in cui sappiamo QUANDO imparare: stancare
        # la sua fonte per guadagnare qualche punto su un canale secondario
        # e' un cattivo scambio. Il websocket porta 200 campanelle contro le
        # 88 del filtro, e non costa richieste.
        # NON SI BRUCIA LA FONTE: e' la stessa regola che ho gia' violato
        # stanotte con le porte websocket, e questa e' la seconda volta.
        _ora = time.time()
        d = None
        if _ora - _ultimo_filtro[0] >= 2.0:
            _ultimo_filtro[0] = _ora
            d = rpc("eth_getFilterChanges",[fid])
            if d is None:
                fid=(rpc("eth_newPendingTransactionFilter",[]) or {}).get("result")
        if d is None:
            pass
        else:
            h=[x for x in (d.get("result") or [])
               if x.lower() not in gia_fatti and x.lower() not in arrivi]
            viste+=len(h)
            if h:
                for hh,tx in mazzo_tx(h).items():
                    hh=hh.lower()
                    if (tx.get("input") or "")[:10]!=SELETTORE: continue
                    if hh in gia_fatti or hh in arrivi: continue
                    arrivi[hh]=tx; dal_http+=1
        if not arrivi:
            time.sleep(0.05)
            try:
                json.dump({"pid":os.getpid(),"giri":giri,"viste":viste,
                    # CHI CI NUTRE: messaggi e "prime" per ogni porta (7/11).
                    # Senza questo non sapevamo che una delle tre finestre
                    # era muta, e il suo rumore copriva le cadute di quelle
                    # vere. "Aperta" non e' "sente".
                    "secondo_occhio":bool(_alchemy_viva[0]),
                    "gara_fra_fonti":{
                        "prime":dict(_prime_porta),
                        "ritardo_mediano_ms":{
                            _k:round(sorted(_vv)[len(_vv)//2],1)
                            for _k,_vv in _ritardo_porta.items() if _vv},
                        "misure":{_k:len(_vv)
                                  for _k,_vv in _ritardo_porta.items()}},
                    "porte":[{"porta":u.split("//")[-1],"messaggi":m,
                              "prime":pr,"cadute":c,
                              "ritardo_mediano_ms":(round(rm,1) if rm
                                                    is not None else None),
                              "ritardi_misurati":nr,
                              "passati_dal_filtro":pf}
                             for u,m,pr,c,rm,nr,pf in OW.resoconto_porte()],
                    "becchi":becchi,"nostri_feed":nostri_feed,
                    "non_nostri":non_nostri,"senza_esposte":senza_esposte,
                    "composti":composti,"utili":utili,
                    "minuti":round((time.time()-t0)/60,1),"armata":ARMATA,
                    "accettati":accettati_tot,
                    "dal_websocket":dal_ws,"dal_filtro_http":dal_http,
                    "grezzi_in_casa":grezzi_in_casa,
                    "grezzi_da_rete":grezzi_da_rete,
                    "firme_in_magazzino":len(_magazzino_firme),
                    "firme_usate_dal_magazzino":_usate_dal_magazzino[0],
                    "firme_fatte_al_volo":_firmate_al_volo[0],
                    # IL FILO CHE SCALDA I PREZZI VECCHI: se muore, il filtro
                    # delle cadute si spegne in SILENZIO. E' esattamente cio'
                    # che e' successo il 6/11 per tre giri di loop.
                    "prezzi_scaldati":PN.quanto_ha_scaldato(),
                    "in_castigo":len(_RIFIUTI_SIMULATI),
                    "i_piu_rifiutati":sorted(_RIFIUTI_SIMULATI.items(),
                                             key=lambda x:-x[1])[:3],
                    # quanto costa OGNI porta: il totale e' il massimo, non
                    # la somma, quindi conta sapere quale e' la lenta
                    "ms_per_porta":{k:(sum(v)//len(v) if v else None)
                                    for k,v in (_IP_TEMPI or {}).items()},
                    "porte_cadute":_porte_cadute},
                    open(VITA,"w"))
            except OSError: pass
            continue
        if len(gia_fatti)>40000:
            gia_fatti=set(list(gia_fatti)[-10000:])
        for hh,tx in arrivi.items():
            gia_fatti.add(hh)
            t_becco=time.time(); becchi+=1
            # I BYTE GREZZI SI RICOSTRUISCONO IN CASA dai campi che il
            # websocket ci ha gia' dato, firma compresa, e la prova e' esatta:
            # il keccak dei byte DEVE essere l'hash. Provato su tutte le 517
            # transazioni di un blocco, zero errori. Via un altro giro di rete.
            raw=GC.grezzo(tx)
            if raw: grezzi_in_casa+=1
            else:
                # NON si tira a indovinare e NON si tace: si chiede alla rete
                # e si dice che e' successo.
                print(f"   grezzo non ricostruito, chiedo alla rete: {hh[:14]}")
                raw=(rpc("eth_getRawTransactionByHash",[hh]) or {}).get("result")
                grezzi_da_rete+=1
            if not raw or len(raw)<100:
                print(f"   becco senza byte: {hh[:14]}"); continue
            # DI QUALE PREZZO PARLA QUESTO AGGIORNAMENTO
            bers=MF.bersaglio_di(tx.get("input") or "")
            tocca=MF.asset_toccati(bers,NOSTRI) if bers else []
            if not tocca:
                non_nostri+=1
                continue
            nostri_feed+=1
            testa,nonce=P._testa_e_nonce()
            cands=candidate(tocca)
            if not cands:
                senza_esposte+=1
                continue
            # CHI CADE DAVVERO CON QUESTO PREZZO (5/11).
            #
            # Sapevamo QUALE prezzo cambiava, non DI QUANTO, quindi si
            # spediva "nel caso" per ogni posizione esposta. Misurato: 106
            # pacchetti su 4 porte vogliono 31 secondi, e un blocco dura 12.
            # Il mazzo JSON-RPC non lo accetta nessuno dei quattro.
            # Ma il prezzo nuovo sta DENTRO la chiamata in attesa, e si
            # legge: provato su 3 aggiornamenti veri, la mediana delle
            # osservazioni e' IDENTICA al latestAnswer di quel blocco.
            # Cosi' si spedisce solo per chi scende davvero sotto 1.
            _feed,_med=PN.feed_e_mediana(tx.get("input") or "")
            _rap=PN.rapporto(_feed,_med,
                 lambda f:(lambda r:int(r,16) if r and r!="0x" else None)(
                     (rpc("eth_call",[{"to":f,"data":"0x50d25bcd"},"latest"]) or {}).get("result")))
            if _rap is None:
                # IL CASO «NON SO» NON DEVE ESSERE MUTO (6/11).
                # Per tre giri ho cercato perche' la riga del segnale non
                # comparisse mai, e la ragione era che quando il rapporto non
                # si sa non si stampa NIENTE: indistinguibile da un filtro
                # rotto. La regola di stanotte, imparata tre volte: un
                # meccanismo che lavora in silenzio non si puo' diagnosticare.
                _c,_ok,_ko,_vivo = PN.quanto_ha_scaldato()
                print(f"   prezzo {str(_feed)[:10]} ancora SENZA storico "
                      f"(mediana {_med}) -> non filtro, spedisco la piu' ricca "
                      f"di {len(cands)} | cache {_c} scaldate {_ok} errori {_ko} "
                      f"filo {'vivo' if _vivo else 'MORTO'}")
            if _rap is not None:
                _t=set(tocca)
                # MARGINE 1,02 E NON 1,00: la stima e' esatta solo se la
                # posizione ha un solo asset di garanzia e uno di debito.
                # Dove non lo e', salute_dopo restituisce la salute attuale e
                # non esclude niente. Il margine copre l'errore residuo: un
                # filtro troppo fiducioso escluderebbe la caduta vera, ed e'
                # esattamente l'errore che ci e' costato 8 liquidazioni.
                # DUE GRUPPI, NON UNO: chi cade DAVVERO e chi sta nel
                # margine (6/11, difetto trovato leggendo la nostra stessa
                # simulazione).
                #
                # MISURATO: su 2.093 pacchetti simulati, ZERO avrebbero
                # funzionato, e in 1.476 casi l'errore era
                # HealthFactorNotBelowThreshold -- la posizione, applicato il
                # prezzo nuovo, NON era sotto 1. Sono i casi di margine: li
                # includevo a 1,02 per coprire l'errore di stima (la stima e'
                # esatta solo con un asset di garanzia e uno di debito).
                # Andava bene quando mandavamo 12 pacchetti. Ma da quando ne
                # mandiamo UNO SOLO, scelto per premio, se il piu' ricco e'
                # un caso di margine bruciamo l'unico colpo su un pacchetto
                # che NON PUO' entrare, e lasciamo fuori quello che cade.
                # Quindi: prima i veri, ordinati per premio; i margine solo
                # se non c'e' nessun vero.
                def _dopo(c):
                    return PN.salute_dopo(c["salute"], _rap,
                                          c["garanzia"] in _t, c["debito"] in _t)
                # LA SOGLIA DEI «VERI» NON E' 1,00 MA 0,995 (6/11, imparato
                # dal primo caso che ci e' passato davanti).
                #
                # Alle 04:35 la stima ha dichiarato «sotto 1» la posizione da
                # $130.841 a salute 1,000734 con un movimento dello 0,146%:
                # 1,000734/1,00146 = 0,99927. La simulazione sulla catena dice
                # HealthFactorNotBelowThreshold: NON e' caduta.
                # PERCHE' la stima sbaglia: e' lineare e assume un solo asset
                # di garanzia e uno di debito. Su una posizione multi-asset
                # l'asset che si muove e' solo UNA PARTE del debito, quindi la
                # salute si muove MENO di quanto stimo -- e composizione.json
                # tiene solo l'asset principale, percio' non posso calcolarla
                # esatta con i dati che abbiamo.
                # Non potendo essere precisi, almeno non si spreca l'unico
                # colpo su un caso che sta a sette decimillesimi dalla soglia.
                # 0,995 e' PROVVISORIO: e' mezzo punto di margine scelto da me,
                # non misurato, perche' per misurarlo serve almeno un successo
                # da cui calibrare. Per questo ogni riga registra la stima
                # accanto all'esito della simulazione: quando arrivera' il
                # primo «buono», la soglia si ricava dai dati.
                SOGLIA_VERI = 0.995
                _veri   = [c for c in cands if _dopo(c) < SOGLIA_VERI]
                _margine= [c for c in cands if SOGLIA_VERI <= _dopo(c) < 1.02]
                # SE NESSUNO CADE DAVVERO, SI SPEDISCE SOLO A CHI NON HA
                # GIA' FALLITO -- e se hanno tutti fallito, NON si spedisce.
                #
                # La prova sta nei nostri 2.222 pacchetti simulati: ZERO
                # hanno funzionato, e 1.599 sono stati rifiutati con
                # HealthFactorNotBelowThreshold. Erano quasi tutti casi di
                # MARGINE, cioe' posizioni che la stima lineare dichiara
                # cadute e che sulla catena non cadono.
                # E il premio non le distingue: osETH->WETH ha un tetto di
                # vendita, quindi decine di posizioni portano il MEDESIMO
                # premio di $130.841 -- un plateau, non una classifica. Il
                # castigo spingeva indietro una e la successiva identica
                # prendeva il colpo.
                # Quindi: i veri prima; se non ce ne sono, si prova solo chi
                # non ha mai fallito; e se hanno fallito tutti si sta fermi,
                # perche' spedire un pacchetto che non puo' entrare non costa
                # gas ma costa reputazione verso i costruttori (beaverbuild e
                # Titan hanno filtri anti-rumore, lo dicono Astra e Grok).
                if _veri:
                    _cadono = _veri
                else:
                    _cadono = [c for c in _margine if _quanti_rifiuti(c.get("utente")) == 0]
                    if _margine and not _cadono:
                        print(f"   nessuno cade davvero e i {len(_margine)} di margine "
                              f"hanno gia' fallito: non spedisco")
                        senza_cadute += 1
                        continue
                _mosso=round((_rap-1)*100,3)
                print(f"   prezzo {_feed[:10] if _feed else '?'} muove {_mosso:+.3f}%"
                      f" -> sotto 0,995: {len(_veri)} | nel margine: {len(_margine)}"
                      f" | di {len(cands)} esposte")
                if _cadono:
                    cadute_previste+=len(_cadono)
                    # UN SOLO PACCHETTO, IL PIU' RICCO (6/11, da Astra e Grok
                    # consultati separatamente: concordano).
                    #
                    # Spedivamo un pacchetto per OGNI posizione che cade --
                    # 7-13 per campanella, ognuno a 4 porte e per 3 blocchi.
                    # Misurato dal nostro registro: da 799 a 3.535 ms per
                    # consegnarli. La finestra fra l'apparire
                    # dell'aggiornamento e la chiusura del blocco e' 80-250
                    # ms, e chi vince ci sta in 20-80: arrivavamo quando il
                    # blocco era GIA' SIGILLATO. «Accettato» per il blocco
                    # +1 non vuol dire arrivato in tempo per il +1.
                    #
                    # E non sono alternative: le nostre transazioni portano
                    # tutte LO STESSO NONCE, quindi solo una puo' entrare --
                    # erano 12 pacchetti in CONFLITTO fra loro, non 12
                    # possibilita'. Mandarne uno non riduce le occasioni:
                    # riduce il tempo di consegna di dieci volte.
                    # Beaverbuild e Titan hanno filtri anti-rumore, quindi
                    # spararne dodici peggiorava anche la reputazione.
                    #
                    # SI SCEGLIE PER WEI ASSOLUTI, non per percentuale: al
                    # costruttore interessa quanto incassa, e il nostro 9,6%
                    # su una liquidazione piccola perde contro il loro 5% su
                    # tre grandi. Il premio e' il miglior proxy che abbiamo.
                    # PRIMA CHI NON HA UNA STORIA DI RIFIUTI, poi il premio.
                    # Una posizione difesa che la stima dichiara caduta ogni
                    # volta ci mangiava un terzo dei colpi senza mai poter
                    # entrare: la prova stava nella nostra simulazione.
                    # A PREMIO PARI DECIDE LA SALUTE. Il premio e' tagliato
                    # dal tetto di vendita, quindi decine di posizioni hanno
                    # lo stesso numero: ordinare per premio su un plateau non
                    # e' una classifica. La vicinanza alla soglia dice chi ha
                    # piu' probabilita' di cadere per davvero.
                    _cadono.sort(key=lambda c: (min(_quanti_rifiuti(c.get("utente")), 3),
                                                -(c.get("premio") or 0),
                                                c.get("salute") or 9))
                    cands=_cadono[:1]
                    if len(_cadono) > 1:
                        print(f"   ne cadono {len(_cadono)}: spedisco solo la "
                              f"piu' ricca (${_cadono[0].get('premio',0):,.0f}), "
                              f"stesso nonce = erano in conflitto")
                else:
                    # NIENTE DA PRENDERE: non si spedisce. Non e' prudenza,
                    # e' che un pacchetto su una posizione che resta sana
                    # viene respinto comunque (HealthFactorNotBelowThreshold)
                    # e intanto occupa i millisecondi di quello che serve.
                    senza_cadute+=1
                    continue
            # IL LIMITE VALE ANCHE QUANDO NON SAPPIAMO CHI CADE (6/11).
            #
            # Il filtro delle cadute vere limita a 1 pacchetto, ma se il
            # rapporto del prezzo non si calcola (prezzo vecchio ignoto, feed
            # nuovo) quel blocco viene saltato e si ricadeva a spedire TUTTE
            # le candidate: misurato un evento da 4 pacchetti alle 01:00 col
            # codice nuovo gia' attivo, e prima fino a 30.
            # LA RAGIONE PER CUI NON SERVE: le nostre transazioni portano
            # tutte LO STESSO NONCE, quindi una sola puo' entrare. Trenta
            # pacchetti non sono mai stati trenta possibilita' -- erano trenta
            # bundle in CONFLITTO che si escludevano a vicenda, pagati in
            # secondi di latenza su una finestra di 80-250 ms.
            # Si tiene la piu' ricca: al costruttore interessa il wei
            # assoluto, e il premio e' il miglior proxy che abbiamo.
            if len(cands) > 1:
                cands = sorted(cands, key=lambda c: -(c.get("premio") or 0))[:1]
            pacchi=[pacchetto(raw,c,testa,nonce,pe) for c in cands]
            pacchi=[p for p in pacchi if p]
            composti+=len(pacchi)
            t_pronto=time.time()
            esiti=[]
            if ARMATA:
                def spedisci(p):
                    # A TUTTE LE PORTE, non solo al relay di Flashbots.
                    # Misurato il 4/11: beaverbuild costruisce il 75,5% dei
                    # blocchi dove avvengono le liquidazioni sopra i $500, e
                    # non riceveva nessuno dei nostri 12.000 pacchetti.
                    # "Accettato dal relay" non e' "arrivato a chi costruisce
                    # quel blocco", ed e' quasi certamente il motivo per cui
                    # zero pacchetti sono stati inclusi.
                    from invia_pacchetto import a_tutte_le_porte
                    # I TRE BLOCCHI IN PARALLELO, NON IN FILA (6/11).
                    # Erano un ciclo: tre invii uno dopo l'altro, e ciascuno
                    # costa ~650 ms verso quattro porte -> ~2 secondi, su una
                    # finestra utile di 80-250 ms. Sono richieste
                    # indipendenti: non c'e' nessuna ragione per cui la
                    # seconda aspetti la prima.
                    # TUTTE LE RICHIESTE IN UN SOLO GRUPPO DI FILI (6/11).
                    # Prima: un gruppo per blocco, e dentro un altro gruppo
                    # per le porte. Misurato ~250 ms di consegna quando le
                    # singole porte costano 61-99 ms: tre quarti erano
                    # struttura, non rete.
                    from invia_pacchetto import a_tutte_le_porte_molti
                    _corpi = p.get("corpi") or [p["corpo"]]
                    _es = a_tutte_le_porte_molti("eth_sendBundle", _corpi)
                    return any(ok for ok, _ in _es.values())
                with cf.ThreadPoolExecutor(max_workers=len(pacchi) or 1) as ex:
                    esiti=list(ex.map(spedisci, pacchi))
                # SI GUARDA SE E' ENTRATO. DIFETTO TROVATO l'1/11: la
                # sentinella consegnava 496 pacchetti e NON CONTROLLAVA MAI
                # l'esito. Se avesse vinto, nessuno se ne sarebbe accorto:
                # niente email a Nicolo', niente flag, e il pescatore
                # avrebbe continuato a sparare. I soldi sarebbero arrivati
                # in cassa in silenzio -- il guasto peggiore possibile per
                # un sistema il cui unico scopo e' avvisare.
                threading.Thread(target=controlla_esito,
                                 args=(pacchi,), daemon=True).start()
                # E SI SIMULA, per sapere se SAREBBE servito.
                #
                # La domanda che non abbiamo mai avuto il denominatore per
                # rispondere (4/11 sera): i nostri pacchetti sono SCOMMESSE
                # -- li mandiamo su posizioni ancora sane sperando che
                # quell'aggiornamento di prezzo le spinga sotto 1,0. Se non
                # le spinge, la liquidazione si annulla PER COSTRUZIONE.
                # Quindi "1.800 accettati e zero inclusi" puo' non essere un
                # problema di consegna: puo' essere che nessuna delle
                # candidate cadesse davvero.
                # La simulazione costa zero (eth_callBundle non esegue) e
                # gira in un filo di fondo per non rallentare la consegna.
                # Il numero che produce e' il piu' importante che ci manca:
                # quante volte un nostro pacchetto AVREBBE funzionato.
                # IL MOTIVO, NON SOLO IL NUMERO (riparato il 4/11 sera).
                # Difetto trovato da solo: la simulazione contava i buoni e
                # BUTTAVA VIA il motivo del fallimento. "74 simulati, 0
                # buoni" non dice niente su cosa riparare, ed e' la stessa
                # famiglia dei contatori senza nome: uno stadio che riporta
                # il fallimento senza dire perche' rassicura di stare
                # misurando mentre non insegna niente.
                # I motivi di Aave discriminano da soli la diagnosi:
                #   "45" = HEALTH_FACTOR_NOT_BELOW_THRESHOLD -> non e'
                #          caduta: o il prezzo e' andato nel verso buono,
                #          o il movimento era troppo piccolo;
                #   un errore NOSTRO (GuadagnoInsufficiente) = e' caduta
                #          davvero ma la vendita non copriva il prestito.
                # Sono due riparazioni opposte, e finora non sapevamo quale.
                def _motivo(r):
                    t = (r.get("revert") or r.get("error") or "")
                    t = str(t)
                    if not t: return "nessun motivo dato"
                    for cod, nome in (("'45'", "45 non e' caduta"),
                                      ('"45"', "45 non e' caduta")):
                        if cod in t: return nome
                    if "GuadagnoInsufficiente" in t or "0x4b6c4bfa" in t:
                        return "caduta ma vendita insufficiente"
                    # I NOMI NOTI, decodificati una volta e scritti qui
                    # (7/11). Il contatore registrava i selettori nudi, e per
                    # giorni il motivo dominante era «0x930bb771» -- un numero
                    # che non vuol dire niente a chi legge. L'ho decodificato
                    # oggi: e' HealthFactorNotBelowThreshold di Aave, cioe'
                    # «la posizione NON era liquidabile», il 71% dei nostri
                    # pacchetti. Un motivo che non si legge non si ripara.
                    NOTI = {
                        "0x930bb771": "NON era liquidabile "
                                      "(HealthFactorNotBelowThreshold)",
                        "0x4b6c4bfa": "caduta ma vendita insufficiente",
                        # decodificato il 7/11 sera da un archivio pubblico
                        # di firme, dopo aver provato 60 candidati a mano
                        # senza trovarlo: indovinare costa e non conclude,
                        # cercare in un registro costa una richiesta.
                        # Il dato catturato era il selettore NUDO, senza
                        # argomenti, quindi un errore senza parametri.
                        "0x2075cc10": "garanzia da prendere ZERO "
                                      "(InvalidBurnAmount)",
                    }
                    for _sel, _nome in NOTI.items():
                        if _sel in t:
                            return _nome
                    # UN SELETTORE IGNOTO SI REGISTRA PER INTERO, non si
                    # indovina. Ho provato a decodificare «0x2075cc10» contro
                    # 60 firme candidate e non l'ho trovato: indovinare costa
                    # e non conclude. Il dato completo lo decodifica da solo
                    # la prima volta che qualcuno lo guarda.
                    # LA CONDIZIONE ERA TROPPO STRETTA e il registratore non
                    # ha catturato NIENTE (trovato un giro dopo averlo
                    # scritto): pretendeva che il testo INIZIASSE con «0x»,
                    # mentre un revert arriva come «execution reverted: 0x...»
                    # o dentro una struttura. Una trappola che non scatta e'
                    # una trappola che non esiste -- e me ne sono accorto solo
                    # perche' il file era vuoto mentre il motivo compariva 4
                    # volte su 5 nella finestra.
                    import re as _re
                    _m4 = _re.search(r"0x[0-9a-fA-F]{8,}", t)
                    if _m4:
                        try:
                            _ig = f"{D}/reverti_ignoti.json"
                            try:
                                _d = json.load(open(_ig))
                            except Exception:
                                _d = {}
                            _k = _m4.group(0)[:10]
                            _v = _d.setdefault(_k, {"quante": 0,
                                                    "dato_intero": t[:260]})
                            _v["quante"] += 1
                            json.dump(_d, open(_ig, "w"), indent=1)
                        except Exception:
                            pass
                    return t[:70]
                def _simula_dopo(pp):
                    buoni = 0; motivi = {}; oracolo_ko = 0
                    for p in pp[:8]:          # i primi otto, per non pesare
                        try:
                            # SI SIMULA SULLO STATO DEL BLOCCO PRIMA, non
                            # su "latest". Difetto misurato il 5/11: 367
                            # pacchetti su 764 risultavano "non simulabili",
                            # cioe' il 48% della misura era cieca. Motivo:
                            # la transazione dell'oracolo e' GIA' INCLUSA nel
                            # blocco quando simuliamo, e sullo stato
                            # successivo il suo nonce e' troppo basso. Sullo
                            # stato del blocco precedente invece e' valida.
                            _sb = p["corpo"].get("blockNumber")
                            try:
                                _sb = hex(int(_sb, 16) - 1) if _sb else "latest"
                            except Exception:
                                _sb = "latest"
                            rr = flashbots("eth_callBundle", [{**p["corpo"],
                                   "stateBlockNumber": _sb}])
                            ris = ((rr or {}).get("result") or {}).get("results") or []
                            if len(ris) < 2:
                                # UN RIFIUTO DELLA FONTE NON E' UN GUASTO
                                # NOSTRO (7/11). Qui finiva tutto nello stesso
                                # secchio «pacchetto non simulabile»: 612 su
                                # 2.345, il 26% della misura cieca. Ma dentro
                                # quel secchio c'erano due cose diversissime:
                                # un pacchetto davvero non simulabile, e
                                # Flashbots che risponde con un errore o un
                                # limite -- che non dice NIENTE sul pacchetto.
                                # E' la quarta volta oggi che trovo questa
                                # famiglia: mescolare «non ce l'ho fatta» con
                                # «la fonte non ha risposto» rende il numero
                                # inutile e nasconde il problema vero.
                                _err = ((rr or {}).get("error") or {})
                                _msg = str(_err.get("message")
                                           or (rr or {}).get("errore")
                                           or "")[:60]
                                if _msg:
                                    _k = ("la fonte della simulazione ha "
                                          "rifiutato: " + _msg[:34])
                                elif not rr:
                                    _k = ("la fonte della simulazione non ha "
                                          "risposto")
                                else:
                                    _k = "pacchetto non simulabile"
                                motivi[_k] = motivi.get(_k, 0) + 1
                                continue
                            # SI GUARDA ANCHE IL PRIMO: se la transazione
                            # dell'oracolo non passa nella simulazione, il
                            # pacchetto non vuol dire niente e contarlo come
                            # "non avrebbe funzionato" e' una bugia.
                            r0 = ris[0]
                            if ("error" in r0) or ("revert" in r0):
                                oracolo_ko += 1
                                motivi["l'oracolo stesso non passa"] = motivi.get(
                                    "l'oracolo stesso non passa", 0) + 1
                                continue
                            r1 = ris[1]
                            if not (("error" in r1) or ("revert" in r1)
                                    or (r1.get("value") is None)):
                                buoni += 1
                                # chi funziona esce dal castigo: il castigo
                                # descrive il passato, non una condanna
                                if _RIFIUTI_SIMULATI.pop((p.get("utente") or "")[:12], None):
                                    _salva_castigo()
                            else:
                                _u = (p.get("utente") or "")[:12]
                                if _u:
                                    _RIFIUTI_SIMULATI[_u] = _RIFIUTI_SIMULATI.get(_u, 0) + 1
                                    _salva_castigo()
                                m = _motivo(r1)
                                motivi[m] = motivi.get(m, 0) + 1
                                # UN MOTIVO SENZA IL SUO SOGGETTO NON SI
                                # RIPARA (7/11 sera). Sapevo che il 67% dei
                                # fallimenti recenti era «garanzia da prendere
                                # ZERO» e non sapevo su QUALI posizioni:
                                # stessa lezione delle «3 scoperte» senza
                                # nomi, che mi ha fatto perdere mezz'ora a
                                # ricostruirle da fuori ottenendo 440 invece
                                # di 3. Qui si registra chi, col premio e la
                                # salute, cosi' il prossimo giro parte da una
                                # prova invece che da un'ipotesi.
                                try:
                                    _cp = f"{D}/chi_fallisce.json"
                                    try:
                                        _dd = json.load(open(_cp))
                                    except Exception:
                                        _dd = {}
                                    _rig = _dd.setdefault(m[:48], [])
                                    _rig.append({
                                        "utente": p.get("utente"),
                                        "premio": p.get("premio"),
                                        "salute": p.get("salute"),
                                        "quando": time.strftime("%H:%M")})
                                    _dd[m[:48]] = _rig[-12:]
                                    _t3 = _cp + ".tmp"
                                    json.dump(_dd, open(_t3, "w"), indent=1)
                                    os.replace(_t3, _cp)
                                except Exception:
                                    pass
                        except Exception as e:
                            m = f"rete: {type(e).__name__}"
                            motivi[m] = motivi.get(m, 0) + 1
                    try:
                        q = json.load(open(f"{D}/avrebbero_funzionato.json"))
                    except Exception:
                        q = {"simulati": 0, "buoni": 0, "eventi": 0}
                    q["simulati"] += min(8, len(pp)); q["buoni"] += buoni
                    q["eventi"] += 1; q["quando"] = time.time()
                    q["oracolo_ko"] = q.get("oracolo_ko", 0) + oracolo_ko
                    mm = q.setdefault("motivi", {})
                    for k, n in motivi.items():
                        mm[k] = mm.get(k, 0) + n
                    # UN CONTATORE CUMULATIVO ATTRAVERSO UNA RIPARAZIONE NON
                    # DICE SE LA RIPARAZIONE HA FUNZIONATO (7/11).
                    # Il 6/11 ho riparato la scelta del candidato (prima i
                    # «veri», i casi di margine solo se non c'e' nessun vero)
                    # perche' 1.476 pacchetti su 2.093 si annullavano con
                    # HealthFactorNotBelowThreshold: la posizione, col prezzo
                    # nuovo, NON era sotto 1.
                    # Oggi il totale dice 1.670 su 2.345, cioe' il 71% -- ma
                    # e' la somma di PRIMA e DOPO la riparazione, quindi non
                    # posso sapere se e' servita. E' la famiglia «due archivi,
                    # un falso fenomeno»: un numero che attraversa un cambio
                    # di codice nasconde l'effetto del cambio.
                    # Quindi si tiene anche una FINESTRA degli ultimi esiti,
                    # con il momento in cui e' stata azzerata.
                    _fin = q.setdefault("finestra", {"da": time.time(),
                                                     "simulati": 0,
                                                     "buoni": 0,
                                                     "motivi": {}})
                    _fin["simulati"] = _fin.get("simulati", 0) + len(pp[:8])
                    _fin["buoni"] = _fin.get("buoni", 0) + buoni
                    _fm = _fin.setdefault("motivi", {})
                    for k, n in motivi.items():
                        _fm[k] = _fm.get(k, 0) + n
                    if _fin["simulati"] > 400:      # si ricomincia a contare
                        q["finestra_precedente"] = _fin
                        q["finestra"] = {"da": time.time(), "simulati": 0,
                                         "buoni": 0, "motivi": {}}
                    json.dump(q, open(f"{D}/avrebbero_funzionato.json", "w"), indent=1)
                    if buoni:
                        print(f"   !!! {buoni} pacchetti AVREBBERO FUNZIONATO "
                              f"su questo aggiornamento")
                threading.Thread(target=_simula_dopo, args=(pacchi,),
                                 daemon=True).start()
            else:
                # SILENZIOSA: si SIMULA, per sapere se sarebbe servito
                def simula(p):
                    r=flashbots("eth_callBundle",[{**p["corpo"],
                        "stateBlockNumber":"latest"}])
                    ris=((r or {}).get("result") or {}).get("results") or []
                    if len(ris)<2: return None
                    r1=ris[1]
                    return not (("error" in r1) or ("revert" in r1)
                                or (r1.get("value") is None))
                with cf.ThreadPoolExecutor(max_workers=len(pacchi) or 1) as ex:
                    esiti=list(ex.map(simula, pacchi))
            buoni=sum(1 for e in esiti if e)
            utili+=buoni
            # UN NOME ONESTO PER OGNI STADIO. Il 3/11 questo numero veniva
            # scritto nel registro come "avrebbero_funzionato" anche quando
            # la sentinella era ARMATA -- e da armata significa "ACCETTATI
            # dal relay". Diceva 0 su 660 pacchetti, cioe' il sistema
            # spediva a salve, e il nome sbagliato lo faceva sembrare solo
            # una simulazione che non serviva. La causa era la chiave di
            # identita' verso il relay cancellata dalla cartella temporanea.
            # Ogni stadio della catena vuole il suo contatore col suo nome.
            accettati = buoni if ARMATA else 0
            accettati_tot += accettati
            riga={"quando":time.strftime("%H:%M:%S",time.gmtime(t_becco)),
                  "tx_oracolo":hh,"verso":tx.get("to"),
                  "pacchetti":len(pacchi),
                  "ms_per_comporre":round((t_pronto-t_becco)*1000),
                  "ms_totali":round((time.time()-t_becco)*1000),
                  "armata":ARMATA,
                  "accettati":accettati,
                  "avrebbero_funzionato":(0 if ARMATA else buoni),
                  # LA STIMA si registra accanto all'esito: senza questo
                  # non si potra' mai calibrare la soglia sui fatti.
                  "rapporto_prezzo": locals().get("_rap"),
                  "candidate":[{"u":p["utente"][:12],"salute":p["salute"],
                                "premio":p["premio"],"gwei":p["gwei"],
                                "uguale":p.get("uguale")}
                               for p in pacchi]}
            print(f"   ORACOLO {riga['quando']}  {len(pacchi)} pacchetti in "
                  f"{riga['ms_per_comporre']} ms (totale {riga['ms_totali']} ms)  "
                  f"-> {buoni} {'spediti' if ARMATA else 'avrebbero funzionato'}")
            try:
                with open(REG,"a") as g: g.write(json.dumps(riga)+"\n")
            except OSError: pass
    print(f"   firme: {len(_magazzino_firme)} in magazzino | usate dal magazzino "
          f"{_usate_dal_magazzino[0]} | fatte al volo {_firmate_al_volo[0]}")
    print(f"   campanelle sui nostri prezzi {nostri_feed} | senza nessuna caduta "
          f"{senza_cadute} | posizioni che cadevano {cadute_previste}")
    print(f"   sentiti dal websocket {dal_ws} | dal filtro HTTP {dal_http} | "
          f"grezzi in casa {grezzi_in_casa} | chiesti alla rete {grezzi_da_rete}")
    if _porte_cadute:
        print(f"   PORTE CADUTE: {list(_porte_cadute)}")
    print(f"   feed NOSTRI {nostri_feed} | di altri asset {non_nostri} | "
          f"nostri ma senza posizioni esposte {senza_esposte}")
    print(f"\n   {giri} giri | {viste} transazioni | {becchi} aggiornamenti "
          f"| {composti} pacchetti composti | {utili} utili")
if __name__=="__main__":
    main()
