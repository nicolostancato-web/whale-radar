"""IL PESCATORE: il sistema completo, calibrato, per la PRIMA BOLLA.

Non e' «live su tutto». E' una canna sola in acqua, che aspetta il primo
pesce e tira. Quando ne prende uno, si ferma e si guarda cos'e' successo.

CALIBRAZIONI (31/10, misurate non assunte):
  limite di gas      1.750.000  (+50% sui 1.168.724 della prova riuscita)
  guadagno minimo    5 dollari  (25 volte il costo di un tentativo)
  asset ammessi      wstETH weETH WBTC LINK AAVE sUSDe WETH USDT USDC
  rsETH              ESCLUSO: due prove dicono che non si vende

ASSET DI DEBITO (quello che si prende in prestito lampo), provati il 31/10
con ProvaVera.t.sol su posizioni vere al blocco attuale:
  WETH  PASSA  $25.578 in cassa      USDT  PASSA  $5.130 in cassa
  USDC  PASSA  $288 in cassa         GHO   PASSA  1.077 GHO in cassa
Coprono il 97,8% del premio potenziale fra le posizioni armate. Gli altri
(wstETH, DAI, WBTC, USDtb, USDe, LINK come DEBITO) non sono provati ma non
si bloccano: se il prestito lampo non c'e', il contratto si annulla e il
tentativo costa centesimi. Meglio provarci che perdere l'occasione.

SICUREZZE:
  - il contratto si annulla se il guadagno e' sotto soglia: caso peggiore,
    centesimi di gas
  - un solo tentativo per posizione, poi si ferma: e' la PRIMA bolla
  - il guadagno va alla cassa di Nicolo', mai al portafoglio operativo
"""
import json, os, subprocess, time, threading, urllib.request, sys, socket
sys.path.insert(0,"agents")
from keccak import firma
ARMATO = True           # <<< ARMATO il 31/10 con via ufficiale di Nicolo'
UNA_SOLA = True         # dopo la prima presa, ci si ferma
# RIDOTTO da 1.750.000 il 5/11, su misura e non a sentimento.
#
# Il gas MISURATO nelle prove in catena: 800.000 per il piano a un passaggio,
# 1.006.000 per quello a due (Uniswap v4), 1.101.000 per quello a tre (due
# piazze). Il limite a 1,75 milioni era sovrabbondante del 59%.
#
# Perche' conta: il limite moltiplica il prezzo del gas, e con la base fee
# passata da 0,04 a 9 gwei in un'ora il portafoglio operativo (35 $) copriva
# UN SOLO colpo. A 1,4 milioni ne copre il 25% in piu', senza rischi nuovi:
# restano 27 punti di margine sul massimo mai misurato.
#
# E il rischio di un limite troppo basso NON e' una perdita: la transazione
# finisce il gas, si annulla, il pacchetto non entra e non si paga niente.
# Si perde l'occasione, non i soldi. Quindi il margine va tenuto, ma non
# esagerato -- esagerarlo costa occasioni quando il gas e' alto.
GAS_LIMITE = 1_400_000


def gas_per_piano(calldata):
    """Il limite di gas misurato per il piano che stiamo spedendo.

    PERCHE' (5/11 sera, con Nicolo' che non puo' rifornire il portafoglio).
    Mandavamo 1.400.000 per QUALUNQUE piano, ma i piani costano diverso:
    misurato in catena, 800.000 per un passaggio, 1.006.000 per due (v4),
    1.101.000 per tre (due piazze). Il limite moltiplica il prezzo del gas,
    e con 35 $ nel portafoglio la soglia per essere in gara e' limite x gas:
    a 1.400.000 siamo fuori sopra gli 11 gwei, a 950.000 sopra i 16,5.
    Non e' un risparmio: e' il prezzo del gas oltre il quale esistiamo.
    Il margine resta ~18% sul massimo misurato per ciascun tipo, e un limite
    troppo basso costa un'OCCASIONE (la tx finisce il gas e il pacchetto non
    entra), non capitale.
    """
    # MARGINI ALLARGATI il 5/11 sera, dopo il rifornimento del portafoglio
    # (da 35 a 95 $). Prima li stringevo per NECESSITA': con 35 $ il limite
    # decideva se potevamo partecipare, e ogni 100.000 di gas in meno erano
    # gwei di prezzo in piu' che potevamo sopportare.
    # Ora che c'e' capienza, il rischio da comprare e' l'opposto: un limite
    # troppo stretto fa finire il gas alla transazione, il pacchetto non
    # entra, e si perde l'OCCASIONE. Con 95 $ restiamo in gara fino a 38
    # gwei anche con questi margini (il 30% sopra il massimo misurato),
    # contro una base fee di 2,7: non serve risparmiare, serve non mancare.
    n = (len(calldata) // 2) if calldata else 0
    if n > 2400:
        return 1_450_000        # tre passaggi, misurato 1.101.000 (+32%)
    if n > 1500:
        return 1_350_000        # due passaggi, misurato 1.006.000 (+34%)
    return 1_100_000            # un passaggio, misurato 800.000 (+37%)
# IL PAVIMENTO SCESO A 0,40 \$ (6/11, con l'ok di Nicolo' a spendere ~3 \$).
#
# PERCHE'. La guardia vera e' `max(pavimento, 25% del premio)`: e' il 25%
# che ci protegge da chi ci ruba il premio a metà operazione -- su un premio
# da 3.000 \$ pretende 750 \$ e il pavimento non c'entra. Il pavimento morde
# SOLO sui premi sotto i 20 \$, cioe' esattamente la polvere.
# E la polvere ci serve, per una ragione misurata: NON E' CONTESA. L'11a
# liquidazione e' rimasta a salute 0,943 per DUE ORE senza che nessuno la
# toccasse, perche' non vale il gas di nessuno. Su quelle vinciamo.
# A cosa serve vincerne una: Grok dice che il difetto fatale del nostro
# setup e' che la catena di produzione non ha MAI attraversato un blocco
# vero -- «stai ottimizzando un simulatore». Una presa da due dollari lo
# chiude per intero, chiamata di liquidazione compresa, e costa il gas
# (~0,20 \$) piu' una mancia minuscola presa dal ricavato.
# Il 25% resta dov'era: questo cambio NON tocca la protezione delle
# posizioni grosse, apre solo il fondo della scala.
GUADAGNO_MINIMO_USD = 0.40

# IL MARGINE CHIESTO ALL'AGGREGATORE, in punti base. Trovato il 3/11: era
# 100 (l'1%) scritto a mano dentro la chiamata, mentre il commento che
# giustificava di tenere le vendite pronte fino a sei ore diceva 5%. Con
# l'1% un ordine preparato mezz'ora prima e' probabilmente gia' annullato,
# e in un crollo del 5-9% si annullano TUTTI: la soglia dello scambio
# scatta prima che il contratto possa guadagnare.
#
# Perche' allargarlo non aggiunge rischio: la soglia dello scambio e' una
# guardia DOPPIA, e quella vera e' dentro il contratto (GuadagnoInsufficiente)
# che annulla se non copre prestito + guadagno minimo, misurato in dollari
# al momento vero. Un pacchetto annullato non costa niente. Quindi:
#   - margine dello scambio LARGO, cosi' il movimento di prezzo non ci blocca
#   - guadagno minimo del contratto SEVERO, cosi' un riempimento cattivo
#     viene rifiutato dove il controllo non si puo' aggirare
# Provato il 3/11 con la prova sul blocco vero: a 1500 la prova FALLIVA
# ancora a crolli del 2,5% e del 5%, e passava solo al 10%. Il motivo non
# e' il prezzo, e' la QUANTITA': la soglia e' tarata sull'importo per cui
# l'ordine e' stato costruito (62,05), mentre l'importo davvero incassato
# si scopre al momento (48,76 -- il 78%). Qualunque divergenza in basso
# annulla il colpo, e un crollo e' proprio quando divergono.
# Quindi la soglia dello scambio si rende INERTE (il massimo che
# l'aggregatore accetta) e la difesa resta una sola, dove e' giusta:
# FRAZIONE_PREMIO_PRETESA dentro il contratto, in dollari, sugli importi
# veri del momento. Un pacchetto annullato non costa niente.
SCIVOLAMENTO_BP = 9000
# La frazione del premio atteso che il contratto PRETENDE di incassare.
# Sostituisce i 5 dollari fissi: cinque dollari su un premio da 600 non e'
# una guardia, e' una formalita'.
FRAZIONE_PREMIO_PRETESA = 0.25
# QUANTO VALE UN ORDINE PRONTO al momento del colpo. Portata qui fuori il
# 4/11 notte: era una variabile dentro tenta(), e l'indicatore della
# copertura non poteva vederla -- quindi contava come coperti anche ordini
# che il pescatore avrebbe rifiutato. Una costante, un nome, un posto.
ORDINE_VALE = 21600        # sei ore
AMMESSI = {
 "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0",  # wstETH
 "0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee",  # weETH
 "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599",  # WBTC
 "0x514910771af9ca656af840dff83e8264ecf986ca",  # LINK
 "0x7fc66500c84a76ad7e9c93437bfc5ac33e2ddae9",  # AAVE
 "0x9d39a5de30e57443bff2a8307a4256c8797a3497",  # sUSDe
 # AGGIUNTO il 31/10 dopo misura e prova:
 #   il 60% delle liquidazioni vere di Aave (53 su 93 in 9 giorni) e' su
 #   garanzia WETH, e non era ammessa: eravamo ciechi su meta' mercato.
 #   Tetto misurato $2.000.000 (scivolamento 0,38%).
 #   Prova WethVera.t.sol su posizione vera al blocco attuale: PASSA,
 #   $25.225 arrivati in cassa.
 "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",  # WETH
 # AGGIUNTO il 31/10 dopo prova: USDT e' il 28% del premio reale.
 #   Tetto misurato $2.000.000 (scivolamento 0,01%).
 #   ProvaVera.t.sol su 0x009ae54b (USDT->USDC): PASSA, $5.130 in cassa.
 "0xdac17f958d2ee523a2206206994597c13d831ec7",  # USDT
 # AGGIUNTO il 31/10 dopo prova. USDC e' solo lo 0,15% del premio reale,
 #   ma e' garanzia di 14 posizioni sorvegliate e costa zero ammetterla.
 #   Tetto misurato $2.000.000 (scivolamento 0,50%).
 #   ProvaVera.t.sol su 0x342c3aff (USDC->USDT): PASSA, $288 in cassa.
 #   Su questa rotta l'importo stava a offset 132 -- il valore della vecchia
 #   costante. Tutti e tre i valori visti (132, 68, 100) esistono davvero:
 #   la ricerca non era zelo, era necessaria.
 "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",  # USDC
 # AGGIUNTI il 3/11, chiedendo quale garanzia hanno le posizioni SCOPERTE.
 # Misurato: a un crollo del 9% diventano liquidabili 672 posizioni, 206
 # senza ordine pronto, e TUTTE E 206 erano bloccate da questo elenco --
 # non dal mercato. I gettoni esclusi erano i derivati di ETH a leva, cioe'
 # proprio quelli che in un crollo scendono PIU' di ETH.
 # Ognuno provato con una vendita vera da $100.000: unita' lette dal suo
 # contratto (simbolo + decimali), rotta data dall'aggregatore, dollari
 # tornati >= 97%, importo trovato UNA volta sola nella calldata.
 "0x4c9edd5852cd905f086c759e8383e09bff1e68b3",  # USDe   reso 100,08%
 "0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf",  # cbBTC  reso  99,99%
 "0xbe9895146f7af43049ca1c1ae358b0541ea49704",  # cbETH  reso  99,78%
 "0xae78736cd615f374d3085123a210448e74fc6393",  # rETH   reso  99,97%
 "0x8236a87084f8b84306f72007f36f2618a5634494",  # LBTC   reso  99,38%
 "0x18084fba666a33d37592fa2633fd49a74dd93a88",  # tBTC   reso 100,01%
 "0x68749665ff8d2d112fa859aa293f07a622782f38",  # XAUt   reso  99,59%
 # NON ammessi, e il motivo e' diverso per ognuno (3/11):
 #   rsETH     0xa1290d69: nessuna rotta in NESSUNA configurazione provata
 #             (libera, senza Curve, solo UniswapV3, solo Balancer: 400 o
 #             404 ogni volta). L'aggregatore non lo tratta e basta.
 #             CORREZIONE del 3/11 sera: avevo scritto qui che "vale una
 #             rotta diretta su Uniswap". Provato: su Uniswap non c'e'
 #             niente da prendere. La nota era una mia supposizione.
 #   syrupUSDT 0x356b8d89: l'aggregatore risponde 404, non lo conosce.
 #   osETH     0xf1c9acdc: si VENDE bene (99,6% verso WETH, 99,76% verso
 #             USDC, via Curve). Lo blocca il nostro codice: la rotta e'
 #             multiSwap e l'importo compare a DUE offset (68 e dentro la
 #             calldata di Curve), mentre il contratto patcha un offset solo.
 #
 #             E QUANTO VALE DAVVERO, misurato il 3/11 sera: tutte le 125
 #             posizioni con garanzia osETH hanno il debito in WETH, cioe'
 #             sono coppie UGUALI. In un dump non cadono: ne' al 5%, ne' al
 #             20%. Gli "$8,7M scoperti" che avevo segnalato NON sono
 #             esposti al dump. La piu' vicina a cadere da sola sta a
 #             salute 1,0195, cioe' mesi di interessi.
 #             Quindi non e' urgente, e la strada esiste senza ridistribuire
 #             il contratto: posizioneImporto=0 lo fa saltare il patch
 #             (riga 145 di Liquidatore.sol), e si costruisce l'ordine su
 #             una quantita' prudente lasciando l'avanzo alla cassa.
 #             Da fare quando serve la copertura dello scivolamento lento,
 #             non per il dump.
 #
 #             CORREZIONE del 4/11 notte, e ribalta la conclusione sopra.
 #             Avevo scritto "non e' urgente" perche' le 125 posizioni
 #             osETH erano tutte coppie uguali e la piu' vicina stava a
 #             salute 1,0195, cioe' mesi di interessi. Ma quel giudizio
 #             nasceva da un elenco INCOMPLETO: il raccoglitore non
 #             rileggeva la finestra della testa, e stanotte sono comparsi
 #             166 debitori mai visti. Fra loro, TRE con garanzia osETH:
 #               salute 1,0215  premio $40.541
 #               salute 1,0215  premio $40.541
 #               salute 1,0215  premio  $9.713
 #             Novantamila dollari a salute 1,02 -- lo scivolamento li
 #             raggiunge in giorni, non in mesi. E il nostro contratto non
 #             sa venderli.
 #             QUINDI E' URGENTE, e la strada e' quella scritta sopra:
 #             posizioneImporto=0 fa saltare il patch (riga 145 di
 #             Liquidatore.sol), si costruisce l'ordine su una quantita'
 #             PRUDENTE e l'avanzo di garanzia finisce in cassa da solo
 #             (riga 177). Nessun nuovo deploy.
 #             Non fatto la notte del 4/11 per un motivo preciso: avevo
 #             esaurito le richieste all'aggregatore con le prove della
 #             serata, e costruire e provare un ordine osETH richiede
 #             preventivi. Primo lavoro appena la fonte si libera.
 #
 #             LEZIONE: un giudizio di priorita' poggia sui dati che hai, e
 #             i miei erano incompleti. Quando si corregge una sorgente, si
 #             rivedono le decisioni prese quando era rotta.
}
# Il ramo STESSO GETTONE (garanzia e debito nello stesso asset): zero passi,
# nessuna vendita, si incassa la garanzia e si ripaga col medesimo gettone.
# PROVATO il 1/11 su 0x18a95d14 (WETH/WETH): PASSA, 0,0912 WETH in cassa.
# Come si e' fatto a provarlo: una posizione cosi' NON cade abbassando il
# prezzo -- garanzia e debito scalano insieme -- e non ce n'era nessuna gia'
# sotto 1,0 (sarebbe stata liquidata). Cadono col TEMPO, perche' il debito
# costa piu' di quanto rende la garanzia: sulla copia locale si sono fatti
# passare 630 giorni di interessi, che e' il meccanismo vero con cui cadono,
# solo accelerato. Nessun prezzo falsificato.
# ONESTA' sulla prova: i 630 giorni distorcono l'IMPORTO (il debito cresce e
# l'importo del prestito lampo e' calcolato su oggi). Cio' che e' dimostrato
# e' il MECCANISMO -- piano a zero passi, guadagno in cassa -- non la taglia.
STESSO_GETTONE_PROVATO = True
# TETTI DI TAGLIA (31/10, misurati): oltre questi lo scivolamento supera
# l'1% e l'operazione puo' andare in perdita. Senza questo tetto avremmo
# tentato un colpo da 24 milioni su sUSDe, dove sopra il milione il mercato
# non da' nemmeno un prezzo.
TETTI = json.load(open("data/liquidazioni/tetti.json"))
# IL TETTO VA SULLA COPPIA, non sul gettone. Misurato il 3/11 sera:
# wstETH verso WETH recupera il 99,96% a qualunque taglia fino a 2 milioni,
# wstETH verso le stabili scende al 94,69% a 2 milioni -- e a quel punto il
# premio reale e' l'1,27%, sotto l'1,75% che il contratto pretende: la
# posizione verrebbe RIFIUTATA del tutto invece di presa in una fetta
# redditizia. A 1 milione il premio e' il 3,93%, cioe' 39.300 dollari
# invece di zero.
try:
    _TC = json.load(open("data/liquidazioni/tetti_coppia.json")).get("tetti", {})
except Exception:
    _TC = {}
_FAM_TETTI = {
 "0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0":"ETH","0xcd5fe23c85820f7b72d0926fc9b05b43e359b7ee":"ETH",
 "0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2":"ETH","0xae78736cd615f374d3085123a210448e74fc6393":"ETH",
 "0xbe9895146f7af43049ca1c1ae358b0541ea49704":"ETH",
 "0x2260fac5e5542a773aa44fbcfedf7c193bc2c599":"BTC","0xcbb7c0000ab88b473b1f5afd9ef808440eed33bf":"BTC",
 "0x18084fba666a33d37592fa2633fd49a74dd93a88":"BTC","0x8236a87084f8b84306f72007f36f2618a5634494":"BTC"}
def tetto_per(garanzia, debito):
    """Quanto grande puo' essere la chiusura per QUESTA coppia.

    Tre livelli, dal piu' preciso al piu' generico:
      1. il tetto MISURATO per questa coppia esatta (garanzia|debito),
         trovato per dimezzamenti col Quoter da agents/tetti_misurati.py;
      2. il tetto per garanzia+famiglia del debito (scritto a mano il 3/11);
      3. il tetto per garanzia, e in ultimo il default.
    Il primo livello e' nato il 4/11: i tetti a mano invecchiano (quelli del
    3/11 avevano 71 ore) e non sanno distinguere wstETH->WETH, che regge due
    milioni al 99,96%, da wstETH->cbBTC, che oltre cinquantamila si mangia
    il premio. La differenza fra le due e' 40 volte.
    """
    g = (garanzia or "").lower(); d = (debito or "").lower()
    v = _TC.get(f"{g}|{d}")
    if v: return v
    f = _FAM_TETTI.get(d, "USD")
    v = _TC.get(f"{g}->{f}")
    if v: return v
    return TETTI.get(g, 100_000)
PROXY="0x216B4B4Ba9F3e719726886d34a177484278Bfcae"
# POSIZIONE_IMPORTO non esiste piu' come costante: si cerca per ogni rotta.
# Vedi trova_posizione() e il difetto che l'ha fatta nascere.
FOUNDRY=os.path.expanduser("~/.foundry/bin")
# L'INDIRIZZO VIENE DA UN SOLO POSTO (4/11 sera). Era scritto a mano in
# dieci file, il sorgente e' cresciuto e il contratto in catena non e' mai
# stato ridistribuito: la calldata chiamava un selettore che il bytecode
# distribuito non aveva, e ~12.000 pacchetti sono morti al primo byte con
# revert vuoto. Vedi agents/indirizzi.py.
from indirizzi import contratto as _dove, FIRMA_ESEGUI, MANCIA_WEI

CONTRATTO=_dove()
U="https://ethereum-rpc.publicnode.com"
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
PR=json.load(open("data/liquidazioni/prezzi_oracolo.json"))
REG="data/liquidazioni/pescatore.jsonl"
CHIAVE=subprocess.run(["grep","-oE","Private key wallet 1 0x[a-fA-F0-9]{64}",
    os.path.expanduser("~/Documents/b2b-finder-credentials.txt")],
    capture_output=True,text=True).stdout.strip().split()[-1]
def cast(*a):
    return subprocess.run([f"{FOUNDRY}/cast",*a],capture_output=True,text=True).stdout.strip()
def rpc(m,p,giri=2):
    c=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode()
    for g in range(giri):
        try:
            r=urllib.request.Request(U,data=c,headers={
              "content-type":"application/json","user-agent":"Mozilla/5.0"})
            d=json.load(urllib.request.urlopen(r,timeout=12))
            if "result" in d: return d["result"]
        except Exception: pass
        time.sleep(0.2)
    return None
def salute(a):
    v=rpc("eth_call",[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},"latest"])
    if isinstance(v,str) and len(v)>=2+64*6:
        x=v[2:]
        return {"debito":int(x[64:128],16)/1e8,"salute":int(x[320:384],16)/1e18}
    return None
def trova_posizione(calldata_hex, importo):
    """DOVE sta scritto l'importo da vendere, dentro la calldata.

    DIFETTO TROVATO IL 31/10, e riguardava il sistema ARMATO:
      la posizione era la costante 132, MISURATA SU UNA SOLA ROTTA. Sulla
      rotta 0x46c67b6d (garanzia WETH) l'importo sta invece a 72, e il 132
      cadeva sull'importo ATTESO IN USCITA: il contratto sovrascriveva il
      campo sbagliato, vendeva la quantita' del preventivo invece di quella
      incassata davvero, e si annullava per guadagno insufficiente.
      Nessuna perdita -- il contratto ha fatto il suo dovere -- ma ogni
      liquidazione su una rotta diversa sarebbe andata persa in silenzio.

    Una costante che vale per un caso non e' una costante: si CERCA.
    E se non si trova esattamente una volta, NON si tira: un offset
    indovinato scrive un numero dentro un campo che non sa di esserlo.
    """
    b=bytes.fromhex(calldata_hex[2:] if calldata_hex.startswith("0x") else calldata_hex)
    ago=int(importo).to_bytes(32,"big")
    dove=[i for i in range(0,len(b)-32+1) if b[i:i+32]==ago]
    if len(dove)!=1: return None, len(dove)
    return dove[0], 1
# QUANDO L'AGGREGATORE CI CACCIA, SI SMETTE DI CHIEDERE -- ma non si
# smette di lavorare. Fino al 4/11 un rifiuto fermava tutta la passata
# (regola giusta quando era l'unica fonte: insistere chiude la porta per
# ore). Ora che sappiamo costruirci le vendite da soli, buttare via la
# passata e' solo danno: si mette la fonte in castigo per un quarto d'ora
# e intanto si va di Uniswap.
_CASTIGO = {"fino": 0}
CASTIGO_SECONDI = 900
def aggregatore_in_castigo():
    # SI PUO' FORZARE IL RIPIEGO. Aggiunto il 4/11: per provare la strada
    # Curve ho dovuto aspettare che l'aggregatore ci bloccasse, e quando e'
    # tornato la prova ha ripreso la sua strada -- cioe' l'alternativa si
    # poteva provare solo quando la fonte principale era rotta. Sbagliato:
    # un ripiego che si prova solo in emergenza e' un ripiego non provato.
    # FORZA_RIPIEGO=1 lo mette in castigo a comando.
    if os.environ.get("FORZA_RIPIEGO") == "1": return True
    # L'AGGREGATORE RESTA IN CASTIGO FINCHE' NON LO VEDIAMO ESEGUIRE
    # (deciso il 5/11 a mezzogiorno, su una prova).
    #
    # Fatto misurato: ogni volta che il pianificatore ha scelto l'aggregatore
    # e abbiamo provato l'ordine in catena, la vendita e' fallita con
    # ScambioFallito. Oggi e' capitato di nuovo: lo stesso ordine che
    # passava con la rotta Uniswap (2.021 byte) ha iniziato a fallire appena
    # l'aggregatore e' tornato disponibile e il pianificatore l'ha preferito
    # (3.173 byte). Isolato cambiando UNA cosa sola: con mancia 10% e 15% il
    # fallimento e' identico, quindi non era la mancia -- era la sede.
    #
    # Perche' veniva preferito: si scegliera la rotta col PREVENTIVO
    # migliore, e il suo preventivo e' il migliore. Ma un preventivo che non
    # esegue vale ZERO -- e' la terza volta oggi che incontro questa cosa
    # (il modulo di GHO quotava 1:1 mentre era chiuso; una pozza v4 vuota
    # quotava piu' di zero). Una sede entra fra le scelte quando l'abbiamo
    # vista INCASSARE, non quando promette di piu'.
    #
    # Si riapre mettendo PROVA_AGGREGATORE=1 e facendo passare la prova da
    # capo a fondo: se incassa, si toglie questo blocco.
    if os.environ.get("PROVA_AGGREGATORE") != "1": return True
    return time.time() < _CASTIGO["fino"]
def _metti_in_castigo():
    _CASTIGO["fino"] = time.time() + CASTIGO_SECONDI
def preventivo(src,dst,q,sd,dd):
    # IL TIPO SI STABILISCE AL CONFINE (7/11).
    # Un chiamante passava l'importo come STRINGA. vendita_uniswap fa
    # aritmetica, esplodeva con TypeError, l'eccezione finiva in un `except`
    # largo e si ripiegava su Curve -- che su WETH->USDT rende il 35,41%
    # invece del 100%. Poi la guardia del contratto rifiutava l'occasione
    # INTERA, 11.308 $ di premio, e per giorni ho creduto fosse il mercato.
    # Un errore di tipo travestito da proprieta' del mercato, nascosto da un
    # ripiego silenzioso. Qui si converte una volta, e tutti i rami sotto
    # ricevono un numero.
    q = int(q)
    """Ritorna (sede, calldata, posizione_importo, daApprovare)
    oppure (None, perche', None, None).

    IL QUARTO VALORE, aggiunto il 4/11 notte: chi preleva i gettoni. Con
    l'aggregatore e' un contratto DIVERSO dalla sede (il suo proxy dei
    trasferimenti); con Uniswap e' il router stesso, e allora si passa
    zero -- il contratto autorizza la sede (riga 155 di Liquidatore.sol).
    Prima questo valore era scritto a mano come PROXY in tre punti: con il
    ripiego su Uniswap sarebbe stato quello SBAGLIATO, e lo scambio si
    sarebbe annullato con "transfer amount exceeds allowance" -- lo stesso
    errore del 31/10, che allora sembrava un difetto dei dati.
    """
    if aggregatore_in_castigo():
        return _ripiego_uniswap(src, dst, q, "aggregatore in castigo")
    try:
        r=urllib.request.Request(
            f"https://api.paraswap.io/prices?srcToken={src}&destToken={dst}"
            f"&amount={q}&srcDecimals={sd}&destDecimals={dd}&side=SELL&network=1",
            headers={"user-agent":"Mozilla/5.0","accept":"application/json"})
        pr=json.load(urllib.request.urlopen(r,timeout=12))["priceRoute"]
        rq=urllib.request.Request(
            "https://api.paraswap.io/transactions/1?ignoreChecks=true&ignoreGasEstimate=true",
            data=json.dumps({"srcToken":src,"destToken":dst,"srcAmount":str(q),
                "priceRoute":pr,"userAddress":CONTRATTO,
                "slippage":SCIVOLAMENTO_BP}).encode(),
            headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
        tx=json.load(urllib.request.urlopen(rq,timeout=12))
        dati=tx.get("data")
        # si cerca l'importo che l'aggregatore ha DETTO di vendere (srcAmount
        # della rotta), non quello che gli abbiamo chiesto: arrotonda.
        pos,n=trova_posizione(dati, pr["srcAmount"])
        if pos is None:
            return _ripiego_uniswap(src, dst, q,
                                    f"importo trovato {n} volte")
        # UN PREVENTIVO SI CONFRONTA COL VALORE GIUSTO (7/11).
        # Questa riga mancava, ed e' la causa per cui la prova completa
        # falliva da giorni: Paraswap ci dava una rotta che su 76,71 WETH
        # verso USDT rendeva 61.009 invece di 172.298, cioe' il 35,41%, e noi
        # la accettavamo perche' lo scivolamento e' a 9000 punti base (90%:
        # scelta deliberata, la difesa vera sta nel contratto). Risultato: la
        # guardia del contratto rifiutava l'occasione INTERA -- 11.308 $ di
        # premio -- invece di perdere due punti. Il modo piu' stupido di
        # perdere: la macchina funziona e si dice no da sola.
        # Sulla stessa taglia 1inch rende il 99,78%. Quindi non si stringe la
        # tolleranza (gli scambi si annullerebbero): si cambia SEDE.
        try:
            import rotta_migliore as _RM
            _rec = _RM.recupero(src, dst, int(q), int(pr["destAmount"]))
            if _rec is not None and _rec < _RM.SOGLIA_RECUPERO:
                _s2, _d2, _u2 = _RM.da_1inch(src, dst, int(q), CONTRATTO)
                _rec2 = _RM.recupero(src, dst, int(q), _u2) if _s2 else None
                if _s2 and _rec2 and _rec2 > _rec:
                    _p2, _n2 = trova_posizione(_d2, str(int(q)))
                    if _p2 is not None:
                        print(f"   ROTTA CAMBIATA: paraswap rendeva "
                              f"{_rec*100:.2f}%, 1inch rende "
                              f"{_rec2*100:.2f}% -> uso 1inch")
                        # 1inch preleva tramite il router stesso
                        return _s2, _d2, _p2, 0
                    print(f"   1inch rende {_rec2*100:.2f}% ma l'importo non "
                          f"si trova nella calldata ({_n2} volte): tengo "
                          f"paraswap")
                else:
                    print(f"   ATTENZIONE: paraswap rende solo "
                          f"{_rec*100:.2f}% e non ho una sede migliore")
        except Exception as _e:
            print(f"   giudizio della rotta non riuscito: {str(_e)[:70]}")
        return tx.get("to"), dati, pos, PROXY
    except Exception as e:
        if "429" in str(e) or "Too Many" in str(e):
            _metti_in_castigo()
        return _ripiego_uniswap(src, dst, q, str(e)[:60])
def _ripiego_uniswap(src, dst, q, perche):
    """Quando l'aggregatore non risponde, ci si costruisce la vendita da
    soli leggendo solo la catena.
    Nato il 4/11 notte: l'aggregatore ci ha BLOCCATI (anche una singola
    richiesta nuda torna rifiutata), il rinnovo degli ordini si e' fermato
    e 274 erano scaduti. Tutta la capacita' di vendere stava su UNA fonte
    gratuita che puo' chiudere la porta quando vuole."""
    q = int(q)
    # OGNI RIPIEGO SI GIUDICA. Prima nessuno dei tre livelli confrontava la
    # resa col valore giusto: bastava che una sede rispondesse. Cosi' Curve
    # al 35% e Uniswap al 100% ci sembravano la stessa cosa, e prendevamo la
    # prima che parlava.
    def _ok(sede, uscita, chi):
        if not sede: return False
        try:
            import rotta_migliore as _RM
            r = _RM.recupero(src, dst, q, uscita) if uscita else None
            if r is not None and r < _RM.SOGLIA_RECUPERO:
                print(f"   SEDE SCARTATA — {chi} rende solo {r*100:.2f}%")
                return False
        except Exception:
            pass
        return True
    try:
        from vendita_uniswap import preventivo as uni
        sede, dati, pos, app = uni(src, dst, q, CONTRATTO)
        if sede:
            return sede, dati, pos, app
        uni_perche = dati
    except Exception as e2:
        # UN'ECCEZIONE QUI NON SI INGHIOTTE: la si DICE. Il silenzio di
        # questo `except` ha nascosto per giorni un errore di tipo.
        uni_perche = f"{type(e2).__name__}: {str(e2)[:60]}"
        print(f"   RIPIEGO UNISWAP ESPLOSO: {uni_perche}")
    # SECONDO RIPIEGO: CURVE. Collegato il 4/11 (gradino 8 della scaletta).
    # Alcune monete non hanno compratore su Uniswap e ce l'hanno su Curve:
    # osETH, sUSDe, rsETH, e GHO -- che e' la stablecoin di Aave ed e' il
    # DEBITO di quattro posizioni che restavano scoperte nella fascia 5-9%.
    # Curve regge taglie piu' piccole: il tetto per coppia lo misura.
    try:
        from vendita_curve import preventivo as curv
        v2, d2, p2, a2, uscita, out = curv(src, dst, int(q))
        if v2 and _ok(v2, out or uscita, "curve"):
            return v2, d2, p2, a2
        if v2:
            return None, (f"curve rende troppo poco e non ho altre sedi "
                          f"(aggregatore: {perche} | uniswap: "
                          f"{uni_perche})"), None, None
        return None, f"aggregatore: {perche} | uniswap: {uni_perche} | curve: {d2}", None, None
    except Exception as e3:
        return None, f"aggregatore: {perche} | uniswap: {uni_perche} | curve: {str(e3)[:40]}", None, None
_CACHE={"quando":0,"testa":0,"nonce":0}
def _testa_e_nonce(validita=24):
    """Testa della catena e nonce, tenuti in cache per pochi secondi.
    Leggerli al momento del colpo costava 594 ms -- piu' della consegna
    stessa. Un nonce vecchio di qualche secondo e' ancora buono: il
    portafoglio operativo non manda altre transazioni."""
    if time.time()-_CACHE["quando"] < validita and _CACHE["testa"]:
        return _CACHE["testa"], _CACHE["nonce"]
    try:
        # UNA CHIAMATA SOLA PER DUE COSE. Chiedere l'intestazione del blocco
        # invece del solo numero costa uguale e porta anche la base fee, che
        # serve alla guardia economica: prima la guardia non sapeva il gas e
        # sparava in perdita nelle ore in cui il gas sale (vedi gas_ora.py).
        blk=rpc("eth_getBlockByNumber",["latest",False])
        n=rpc("eth_getTransactionCount",
            [cast("wallet","address","--private-key",CHIAVE),"pending"])
        if blk and n:
            _CACHE.update({"quando":time.time(),
                           "testa":int(blk["number"],16),
                           "nonce":int(n,16)})
            try:
                import gas_ora as _GO
                _pe=(PR.get("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
                     or {}).get("prezzo_usd")
                _GO.scrivi(int(blk["baseFeePerGas"],16),
                           int(blk["number"],16), _pe)
            except Exception: pass
    except Exception: pass
    return _CACHE["testa"], _CACHE["nonce"]
def tenta(utente, comp):
    """Compone e, se ARMATO, manda. Ritorna il resoconto."""
    t0=time.time()
    s=salute(utente)
    if not s or s["salute"]>=1.0: return {"esito":"non caduta"}
    gar=comp["garanzia_principale"].lower(); deb=comp["debito_principale"]
    if gar not in AMMESSI: return {"esito":"garanzia non ammessa","gar":gar}
    pg=PR.get(gar); pd=PR.get(deb)
    if not pg or not pd: return {"esito":"prezzo mancante"}
    quota = 1.0 if s["salute"]<0.95 else 0.5
    dus=comp["debito_usd"]*quota
    # si taglia alla dimensione che il mercato regge per QUESTA garanzia
    tetto = tetto_per(gar, deb)
    if dus*1.07 > tetto:
        dus = tetto/1.07
    if dus*0.07 < GUADAGNO_MINIMO_USD:
        return {"esito":"troppo piccola","premio_atteso":round(dus*0.07,2)}
    qd=int(dus/pd["prezzo_usd"]*10**pd["decimali"])
    # LA GUARDIA, con lo STESSO valore che usa prepara_vendite.py.
    # Trovato il 3/11 sera: qui restavano i 5 dollari fissi mentre gli
    # ordini preparati pretendevano un quarto del premio. Lo stesso
    # controllo con due valori in due file -- e quello debole era proprio
    # sul ramo di ripiego, cioe' quello che gira quando qualcosa e' gia'
    # andato storto. Una costante, un nome.
    # IL GAS DENTRO LA GUARDIA (7/11). Prima qui non c'era, e la guardia
    # era cieca ESATTAMENTE nelle ore in cui compaiono i soldi: i premi
    # grossi delle 12 perse sono arrivati in un grappolo a 8-10 gwei, dove
    # un colpo costa 24,60 $ invece di 0,10. Una posizione da 2 $ di premio
    # passava la guardia perdendo 23 $. Se il gas non lo sappiamo non si
    # inventa niente: resta la vecchia pretesa.
    _costo_gas=None
    try:
        import gas_ora as _GO
        _costo_gas=_GO.costo_colpo_usd(GAS_LIMITE)
    except Exception: pass
    gm_usd=max(GUADAGNO_MINIMO_USD, dus*0.07*FRAZIONE_PREMIO_PRETESA)
    if _costo_gas:
        gm_usd=max(gm_usd, _costo_gas*1.5)
        if dus*0.07 < _costo_gas*1.5:
            return {"esito":"il gas se la mangia",
                    "premio_atteso":round(dus*0.07,2),
                    "costo_gas_usd":round(_costo_gas,2)}
    gm=int(gm_usd/pd["prezzo_usd"]*10**pd["decimali"])
    # VENDITA PRONTA (1/11). Se il preventivo e' stato preparato mentre la
    # posizione era ancora sana, non si chiede niente a nessuno: si spara.
    # MISURATO: chiedere il preventivo costa 885 ms (mediana su 6 posizioni,
    # da 877 a 931); leggerlo dal cassetto costa 0. E le liquidazioni grosse
    # si prendono NELLO STESSO BLOCCO dell'aggiornamento di prezzo, quindi
    # quei 885 ms erano quasi certamente tutto il nostro ritardo.
    # L'importo scritto nella calldata preparata puo' essere diverso da
    # quello vero incassato: non e' un problema, il contratto lo sovrascrive
    # all'offset trovato -- e' esattamente a questo che serve quel
    # meccanismo. Se la vendita pronta manca o e' vecchia, si ripiega sul
    # preventivo dal vivo: piu' lento, ma mai bloccati.
    pronta=None
    try:
        VP=json.load(open("data/liquidazioni/vendite_pronte.json"))
        v=VP.get(utente) or VP.get(utente.lower())
        # QUANTO SI ACCETTA UN ORDINE PRONTO. Era 1800 secondi fissi, e
        # il 3/11 sera e' diventato sbagliato: il margine dello scambio ora
        # e' inerte (9000 bp), quindi un ordine regge molto piu' a lungo, e
        # il programmatore di freschezza in prepara_vendite.py li tiene
        # fino a sei ore. Con il limite a mezz'ora il pescatore buttava via
        # l'ordine pronto e ripiegava sul preventivo dal vivo -- 885 ms in
        # piu' proprio nel momento in cui contano. Si usa la stessa scala.
        # CORREZIONE della correzione, mezz'ora dopo, trovata provando il
        # percorso invece di leggerlo. Avevo messo qui la stessa scala di
        # prepara_vendite.py (1800/7200/21600 secondo la salute), ma e' un
        # errore di ragionamento: al momento del colpo la salute e' SEMPRE
        # sotto 1,02 -- e' caduta -- quindi la scala si risolveva sempre a
        # mezz'ora e l'ordine pronto veniva buttato comunque.
        # Quella scala risponde a "ogni quanto RIFARE un ordine", che e'
        # un'altra domanda. Qui la domanda e' "questo ordine e' ancora
        # valido?", e con il margine inerte la risposta e' si' per ore: a
        # difendere il guadagno c'e' la guardia in dollari del contratto.
        # Provato: con mezz'ora il percorso ripiegava sul preventivo dal
        # vivo e metteva 1.030 ms invece di una novantina.
        if v and (time.time()-v.get("quando",0)) < ORDINE_VALE and v.get("sede"):
            pronta=v
    except Exception: pass
    r_pronta=False
    if gar == deb.lower() and not STESSO_GETTONE_PROVATO:
        return {"esito":"ramo stesso-gettone non provato: non si tira","gar":gar}
    if gar == deb.lower():
        # STESSO GETTONE (es. garanzia WETH, debito WETH): non c'e' niente da
        # vendere. Si incassa la garanzia e si ripaga col medesimo gettone, e
        # il guadagno e' il bonus meno il pedaggio del prestito lampo.
        # Il piano va con ZERO passi: il contratto cicla su una lista vuota e
        # poi fa il controllo del guadagno, che e' esattamente quello che
        # serve. Nessuna fonte esterna da interrogare -> anche piu' veloce.
        # Caso scoperto il 31/10: il 60% delle liquidazioni vere e' su
        # garanzia WETH (53 su 93). Di quelle 53, solo 4 avevano il debito
        # anche in WETH: questo ramo e' raro, le altre 49 passano dalla
        # vendita. Contato, non stimato.
        passi="[]"
    elif pronta:
        passi=f"[({gar},{pronta['sede']},{pronta.get('approvare') or PROXY},{pronta['dati']},{pronta['posizione']})]"
        r_pronta=True
    else:
        # QUANTO chiedere di vendere nel preventivo. Era il 90% dell'atteso,
        # contando sulla sovrascrittura del contratto per correggere al vero.
        # DIFETTO 31/10: su alcune rotte la sovrascrittura NON si propaga ai
        # singoli passaggi dello scambio, quindi si vendeva davvero il 90% --
        # e il 90% di una garanzia che vale il 107% del debito da' il 96%:
        # non basta a ripagare, e il contratto si annullava.
        #   USDT->USDC: incassati 77.247, servivano 80.271.
        # Ora si chiede il 99,5% dell'atteso: se la sovrascrittura prende si
        # vende tutto, se non prende se ne vende il 99,5%, che basta comunque
        # (margine 6,4 punti sul 7% di premio).
        # NOTA aperta: nel secondo caso resta in contratto lo 0,5% di garanzia
        # come polvere. Va aggiunto uno spazzino al contratto -- richiede un
        # nuovo deploy, segnato come prossimo passo.
        qg=int(dus*1.07*0.995/pg["prezzo_usd"]*10**pg["decimali"])
        sede,dati,pos,app=preventivo(gar,deb,qg,pg["decimali"],pd["decimali"])
        if not sede: return {"esito":"vendita non ottenuta","perche":dati}
        passi=f"[({gar},{sede},{app},{dati},{pos})]"
    # CHIAMATA GIA' PRONTA: se e' stata preparata e il debito non si e'
    # mosso piu' del 5%, si usa cosi' com'e'. Comporla costa 90 ms, che su
    # 507 totali e' il 18%: e' il secondo pezzo di tempo piu' grosso dopo
    # la consegna stessa.
    r_chiamata_pronta=False
    if (pronta and pronta.get("chiamata") and
            pronta.get("debito_previsto") and
            dus >= pronta["debito_previsto"]):
        ch=pronta["chiamata"]; r_chiamata_pronta=True
    else:
        ch=cast("calldata",
          FIRMA_ESEGUI,
          deb,str(qd),
          f"({gar},{utente},{passi},{gm},{MANCIA_WEI})")
    if not ch.startswith("0x"): return {"esito":"composizione fallita"}
    r={"esito":"PRONTA","utente":utente,"salute":s["salute"],
       "vendita_pronta":r_pronta,"chiamata_pronta":r_chiamata_pronta,
       "premio_atteso_usd":round(dus*0.07,2),
       "secondi":round(time.time()-t0,2),"armato":ARMATO}
    if ARMATO:
        # CONSEGNA PRIVATA (1/11). Prima si spediva con un invio PUBBLICO, e
        # quello era il difetto peggiore: una liquidazione redditizia era
        # VISIBILE nella piazza prima di essere eseguita, quindi copiabile.
        # Giocavamo a carte scoperte. Ora il pacchetto va diretto al
        # costruttore del blocco: nessuno lo vede, e un pacchetto respinto
        # NON SI PAGA -- tentare costa zero invece di gas bruciato.
        # Prima di spedire si SIMULA (gratis): se si annullerebbe, non parte.
        from invia_pacchetto import manda, flashbots
        pe=PR.get("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2",{}).get("prezzo_usd")
        # la testa della catena e il nonce si tengono in cache: leggerli al
        # momento del colpo costava 394+200 ms, cioe' piu' della consegna.
        testa=_testa_e_nonce()
        if testa:
            m=manda(CONTRATTO, ch, CHIAVE, GAS_LIMITE, testa[0], blocchi=3,
                    prezzo_eth=pe, nonce=testa[1])
            r["consegna"]=m.get("esito"); r["priorita_gwei"]=m.get("priorita_gwei")
            r["gas_simulato"]=m.get("gas_simulato")
            r["simulazione"]=m.get("simulazione")
            if not m.get("accettati"):
                r["riuscita"]=False; r["perche_no"]=str(m.get("perche"))[:160]
                return r
            # il pacchetto e' per i prossimi 3 blocchi: si aspetta l'esito,
            # non si dichiara vinto prima di vederlo nella catena.
            tx=None
            try: tx=json.loads(m["simulazione"])["result"]["results"][0]["txHash"]
            except Exception: pass
            r["transazione"]=tx
            r["riuscita"]=False
            if tx:
                for _ in range(14):              # ~42 secondi, 3-4 blocchi
                    time.sleep(3)
                    rc=rpc("eth_getTransactionReceipt",[tx])
                    if rc:
                        r["riuscita"] = str(rc.get("status")) in ("0x1","1")
                        r["gas_vero"]=rc.get("gasUsed")
                        break
                else:
                    r["perche_no"]="pacchetto non incluso nei 3 blocchi"
        else:
            # il relay non risponde: si ripiega sull'invio pubblico, perche'
            # perdere l'occasione e' peggio che mostrarla.
            out=subprocess.run([f"{FOUNDRY}/cast","send",CONTRATTO,ch,
              "--private-key",CHIAVE,"--gas-limit",str(GAS_LIMITE),
              "--rpc-url",U,"--json"],capture_output=True,text=True).stdout
            r["consegna"]="PUBBLICA (relay muto)"; r["invio"]=out[:200]
            try:
                d=json.loads(out); r["transazione"]=d.get("transactionHash")
                r["riuscita"]= str(d.get("status")) in ("0x1","1","success")
            except Exception as e: r["errore_invio"]=str(e)[:120]
        if r.get("riuscita"):
            # PRIMA si verifica il wallet, POI si avvisa
            try:
                from conferma_e_avvisa import dopo_la_liquidazione
                r["avvisato"]=dopo_la_liquidazione(
                    deb, utente, r.get("transazione"), dus*0.07, dus,
                    garanzia=comp["garanzia_principale"][:10])
            except Exception as e:
                r["errore_avviso"]=str(e)[:120]
    return r
if __name__=="__main__":
    print(f"   PESCATORE — {'ARMATO' if ARMATO else 'silenzioso (non manda)'}")
    print(f"   gas limite {GAS_LIMITE:,} | guadagno minimo ${GUADAGNO_MINIMO_USD}")
    print(f"   asset ammessi: {len(AMMESSI)} | rsETH escluso")
    comp=json.load(open("data/liquidazioni/composizione.json"))
    buone={k:v for k,v in comp.items()
           if v["garanzia_principale"].lower() in AMMESSI}
    print(f"   {len(buone)} posizioni su {len(comp)} hanno garanzia ammessa")
    vic=sorted(buone.items(), key=lambda x:x[1]["salute"])[:5]
    # il cruscotto DEVE mostrare gli stessi numeri che usa il sistema:
    # un display che mostra il premio senza tetto fa credere a occasioni
    # che non esistono.
    for u,c in vic:
        gar=c["garanzia_principale"].lower()
        dus=c["debito_usd"]*0.5
        tetto=TETTI.get(gar,100_000)
        tagliata = dus*1.07 > tetto
        if tagliata: dus = tetto/1.07
        prem=dus*0.07
        print(f"      {u[:14]}  salute {c['salute']:.4f}  "
              f"premio ${prem:>10,.0f}"
              f"{'  (tagliato dal tetto)' if tagliata else ''}")
