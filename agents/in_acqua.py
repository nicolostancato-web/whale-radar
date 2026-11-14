"""IN ACQUA: il pescatore armato, che sorveglia e tira.

Armato il 31/10 con via ufficiale di Nicolo'.
Dopo la prima presa riuscita si FERMA e aspetta il suo giudizio.
"""
import json, os, sys, time, urllib.request
import concurrent.futures as cf
sys.path.insert(0,"agents")
from keccak import firma
from pescatore import tenta, salute, AMMESSI, GUADAGNO_MINIMO_USD, ARMATO
POOL="0x87870bca3f3fd6335c3f4ce8392d69350b4fa4e2"
SEL=firma("getUserAccountData(address)")[2:10]
# fonti provate l'1/11 mazzo per mazzo: a 25 reggono, a 50 rifiutano
FONTI=["https://ethereum-rpc.publicnode.com","https://rpc.mevblocker.io"]
MAZZO=25
FILI=6               # provato l'1/11: 150 letture in fila 3.580 ms, con 3
                     # fili 1.674, con 6 fili 922, con 10 ancora 927. Oltre
                     # i 6 non migliora: il limite e' la fonte, non noi.
def blocco_ora():
    """Il numero del blocco in testa. Serve per agganciare il giro al blocco:
    i prezzi in catena cambiano solo quando un blocco arriva.
    DIFETTO 1/11: la prima volta ho aggiunto il CHIAMANTE e non questa
    funzione, e il mio controllo verificava un'altra variabile -- quindi
    passava. Il pescatore armato e' morto in ciclo di riavvii per due
    minuti con NameError. Si controlla la cosa che serve, non una vicina.
    """
    try:
        c=json.dumps({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber",
                      "params":[]}).encode()
        r=urllib.request.Request(FONTI[0],data=c,
            headers={"content-type":"application/json","user-agent":"Mozilla/5.0"})
        return int(json.load(urllib.request.urlopen(r,timeout=6))["result"],16)
    except Exception: return None
def salute_tutte(indirizzi):
    """Le stesse letture, ma i mazzi in parallelo.

    PERCHE' CONTA, e perche' prima stavo ottimizzando la cosa sbagliata:
    sparare costa 476 ms, ma ACCORGERSI costava fino a 5.600 ms, perche' il
    giro leggeva tutto in fila. Il ritardo di accorgersi era dieci volte
    quello di sparare. Il termine dominante era l'altro.
    """
    # RITIRATO l'1/11, pochi minuti dopo averlo messo: in produzione dava
    # «viste 0, mute 136» -- il pescatore ARMATO era CIECO. Nella prova a
    # mano i 6 fili funzionavano (922 ms contro 3.580); dentro il processo
    # vero no. Differenza fra la prova e la produzione che non ho capito
    # subito, quindi si torna alla lettura in fila, che funziona.
    # Lo strumento che l'ha preso in due minuti e' il campo «mute» del file
    # di vita (feedback_guardia_mai_provata, lezione 1/11): senza quello
    # avremmo aspettato per sempre una presa impossibile.
    if True: return salute_mazzo(indirizzi)
    if len(indirizzi) <= MAZZO: return salute_mazzo(indirizzi)
    gruppi=[indirizzi[i::FILI] for i in range(FILI)]
    fuori={}
    try:
        with cf.ThreadPoolExecutor(max_workers=FILI) as ex:
            for d in ex.map(salute_mazzo, gruppi): fuori.update(d)
    except Exception:
        return salute_mazzo(indirizzi)      # se i fili danno problemi, in fila
    return fuori
def salute_mazzo(indirizzi):
    """Salute di piu' posizioni in una richiesta. ABBINA PER ID, mai per
    posizione: alcune fonti ne restituiscono meno di quante chieste, e
    l'abbinamento per indice sposta i dati di una casella in silenzio
    (imparato su Base, vedi reference_base_rpc_tronca)."""
    fuori={}
    for i in range(0,len(indirizzi),MAZZO):
        pezzo=indirizzi[i:i+MAZZO]
        corpo=[{"jsonrpc":"2.0","id":j,"method":"eth_call",
                "params":[{"to":POOL,"data":"0x"+SEL+a[2:].zfill(64)},"latest"]}
               for j,a in enumerate(pezzo)]
        for u in FONTI:
            try:
                r=urllib.request.Request(u,data=json.dumps(corpo).encode(),
                  headers={"content-type":"application/json",
                           "user-agent":"Mozilla/5.0"})
                d=json.load(urllib.request.urlopen(r,timeout=20))
                if not isinstance(d,list): continue
                n=0
                for e in d:
                    j=e.get("id")
                    if not isinstance(j,int) or j>=len(pezzo): continue
                    v=e.get("result")
                    if not v or len(v)<2+64*6: continue
                    x=v[2:]
                    fuori[pezzo[j]]={"debito":int(x[64:128],16)/1e8,
                                     "salute":int(x[320:384],16)/1e18}
                    n+=1
                if n: break
            except Exception: pass
    return fuori
REG="data/liquidazioni/in_acqua.jsonl"
# LUCCHETTO. Due pescatori ARMATI vorrebbero dire tentare due volte la stessa
# caduta: la seconda transazione fallirebbe (il debito e' gia' chiuso) ma
# pagherebbe gas, e soprattutto «UNA_SOLA presa e poi mi fermo» perderebbe
# senso. Il 1/11 i riavvii della guardia hanno lasciato in giro TRE quaderni,
# perche' i processi vecchi non dichiaravano il pid e nessuno li chiudeva.
# Qui il processo si rifiuta di partire se un altro e' vivo.
# DIFETTO TROVATO l'1/11 provando a misurare la velocita' di lettura: il
# lucchetto e il ciclo stavano al livello del modulo, quindi IMPORTARE
# in_acqua faceva partire il lucchetto e si fermava con «un altro pescatore
# e' vivo». Risultato: non si poteva provare nulla di questo file mentre il
# pescatore girava -- e una prova che non attraversa il codice vero non e'
# una prova (feedback_verifica_attraversa_il_codice).
# Ora le definizioni stanno al modulo e gli effetti dentro main().
def main():
    # IL FLAG DELLA PRESA VIENE PRIMA DI TUTTO, anche del lucchetto. Se la
    # presa e' avvenuta non si arma nulla, per nessuna strada. Prima avevo
    # messo questo controllo dopo il lucchetto, e la prova non lo raggiungeva
    # mai: il lucchetto rispondeva per primo e il ramo restava non provato --
    # cioe' esattamente il tipo di codice che gira una volta sola e non si sa
    # se funziona (feedback_chi_vince_deve_avvisare).
    FLAG="data/liquidazioni/preso.flag"
    if os.path.exists(FLAG):
        try: det=open(FLAG).read()[:200]
        except OSError: det=""
        print(f"   presa gia' avvenuta, non mi armo: {det}")
        return
    LUCCHETTO="data/liquidazioni/in_acqua.lock"
    if os.path.exists(LUCCHETTO):
        try:
            altro=int(open(LUCCHETTO).read().strip())
            os.kill(altro, 0)                      # non lo uccide: chiede se c'e'
            print(f"   un altro pescatore e' vivo (pid {altro}): non parto")
            sys.exit(0)
        except (ValueError, ProcessLookupError, PermissionError, OSError):
            pass                                    # lucchetto abbandonato
    try: open(LUCCHETTO,"w").write(str(os.getpid()))
    except OSError: pass
    import atexit
    atexit.register(lambda: os.path.exists(LUCCHETTO) and os.remove(LUCCHETTO))
    VITA="data/liquidazioni/pescatore_vivo.json"
    # DIFETTO TROVATO IL 31/10: la lista si leggeva UNA VOLTA all'avvio, quindi
    # il laghetto cresceva (140 -> 344) e il pescatore restava sui suoi 11.
    # Allargare serve solo se chi pesca rilegge: ora si ricarica da sola.
    def carica():
        try: comp=json.load(open("data/liquidazioni/composizione.json"))
        except Exception: return None
        buone={k:v for k,v in comp.items()
               if v["garanzia_principale"].lower() in AMMESSI}
        return sorted(buone.items(), key=lambda x:x[1]["salute"])
    lista=carica() or []
    # DUE CORSIE, introdotte l'1/11 per una ragione di reazione.
    # Il pescatore leggeva TUTTE le posizioni a ogni giro, una alla volta: 44
    # secondi su 417, e la raccolta le sta portando verso migliaia. A 2.000
    # sarebbero 3 minuti e mezzo per giro -- inutile, perche' una caduta si
    # prende in secondi, non in minuti. Ma restringere la sorveglianza alle
    # sole imminenti e' pericoloso: in un crollo una posizione a 1,10 arriva a
    # 1,0 in pochi minuti, e se non la guardavamo l'abbiamo persa.
    # Quindi: le VICINE a ogni giro (reazione), TUTTE ogni poche decine di giri
    # (copertura). Il confine si misura, non si indovina: 1,03 perche' le
    # cadute misurate nella fascia 1,00-1,05 sono il 55% in 9 giorni e sopra
    # 1,10 sono l'1,4% (vedi feedback_le_grosse_sono_difese).
    # SOGLIA RIPORTATA A 1,02 il 2/11, dopo che 1,10 ha reso il pescatore
    # CIECO AL 32%: 575 posizioni nella corsia veloce, 275 letture fallite su
    # 850. La misura che lo spiega: leggere 900 posizioni funziona senza
    # errori ma costa 55 SECONDI, e un blocco dura dodici. La capacita' c'era,
    # mancava il tempo -- e in produzione la concorrenza con gli altri
    # processi faceva il resto.
    #
    # CONSEGUENZA SUL DISEGNO, piu' importante del numero: con 900 posizioni
    # armate il pescatore NON PUO' essere la via rapida. I ruoli sono:
    #   - la SENTINELLA e' la via rapida (reagisce all'evento, non sonda);
    #   - il PESCATORE e' la rete di sicurezza (sonda piano, prende cio' che
    #     alla sentinella e' sfuggito).
    # Tenerlo a 1,10 significava renderlo lento E cieco invece di lento e
    # affidabile.
    VICINA=1.02
    OGNI_TANTO_TUTTE=20
    RILEGGI=40           # il laghetto cresce in fretta: si rilegge piu' spesso
                         # (a ~36s il giro su 400 posizioni, sono ~25 minuti)
    print(f"   IN ACQUA — {'ARMATO' if ARMATO else 'SILENZIOSO'}")
    print(f"   sorveglio {len(lista)} posizioni (rileggo ogni {RILEGGI} giri)\n")
    MINUTI=int(sys.argv[1]) if len(sys.argv)>1 else 600
    try:
        json.dump({"pid":os.getpid(),"ultimo":time.strftime("%Y-%m-%d %H:%M:%S",
            time.gmtime()),"giri":0,"minuti":0,"armato":ARMATO,"preso":False,
            "sorvegliate":len(lista),"viste":0,"mute":0,"avvio":True},
            open(VITA,"w"))
    except OSError: pass
    t0=time.time(); giri=0; preso=False
    vicine_note=set()      # le posizioni che si guardano a OGNI giro
    ultimo_blocco=0
    while time.time()-t0 < MINUTI*60 and not preso:
        giri+=1
        # IL GUASTO PEGGIORE POSSIBILE: armato ma CIECO. Se le letture di salute
        # fallissero in silenzio, il file di vita direbbe «giri 346, armato, 391
        # sorvegliate» esattamente come adesso, e noi aspetteremmo per sempre una
        # presa che non puo' arrivare. Quindi ogni giro registra COSA HA VISTO:
        # quante hanno risposto, quante sono mute, e la piu' malata trovata.
        # Se «mute» sale o «piu_malata» resta immobile, c'e' qualcosa che non va.
        peggiore=(9.0,None)
        if giri % RILEGGI == 0:
            nuova=carica()
            if nuova is not None and len(nuova)!=len(lista):
                print(f"   lista aggiornata: {len(lista)} -> {len(nuova)} posizioni")
                lista=nuova
            elif nuova is not None:
                lista=nuova
        def _quanto_vale(u):
            try: return (PREMI.get(u) or PREMI.get(u.lower()) or 0)
            except Exception: return 0
        # quanto vale ogni posizione: sta gia' negli ordini pronti
        try:
            PREMI = {k: (x.get("premio") or 0) for k, x in
                     json.load(open("data/liquidazioni/vendite_pronte.json")).items()}
        except Exception:
            PREMI = {}
        tutte = (giri % OGNI_TANTO_TUTTE == 1) or not vicine_note
        # LA CORSIA SI LEGGE A FETTE, non tutta a ogni giro.
        #
        # DISASTRO CAUSATO DA ME il 4/11: avevo allargato la corsia veloce
        # a 250 posizioni lette a OGNI giro, e il pescatore e' diventato
        # cieco all'80% -- 200 letture mute su 250. Ho bruciato la fonte,
        # lo stesso errore che avevo gia' fatto con i preventivi.
        # E 80% cieco e' MOLTO peggio del problema che volevo risolvere:
        # avevo scambiato "guardo piu' posizioni" con "vedo di piu'".
        #
        # Quello che serve non e' "tutte a ogni giro", e' "ognuna almeno
        # ogni N secondi". Quindi: le piu' preziose si leggono SEMPRE, il
        # resto a fette che ruotano. Con 40 fisse + fette da 60, ogni
        # posizione della corsia si vede entro tre o quattro giri, cioe'
        # meno di un minuto -- contro i quattro minuti di prima, e senza
        # accecare niente.
        SEMPRE = 40          # le piu' preziose, a ogni singolo giro
        FETTA  = 60          # quante delle altre per giro
        if tutte:
            da_leggere = [u for u,_ in lista]
        else:
            ordinate = sorted(vicine_note, key=lambda u: -_quanto_vale(u))
            fisse = ordinate[:SEMPRE]
            resto = ordinate[SEMPRE:]
            if resto:
                inizio = (giri*FETTA) % len(resto)
                fetta = (resto+resto)[inizio:inizio+FETTA]
            else:
                fetta = []
            da_leggere = fisse + fetta
        letture = salute_tutte(da_leggere)
        if tutte:
            # si aggiorna chi e' "vicina": sono quelle che si guardano a ogni giro
            # LA CORSIA VELOCE SI SCEGLIE PER QUANTO VALE, non solo per
            # quanto e' vicina.
            #
            # DIFETTO PAGATO CARO, il 4/11: la posizione
            # 0x8d53903625... e' stata liquidata per $24.048.189 e il
            # premio vero, $297.942, l'ha preso un altro pagando $1,92 di
            # gas e mancia ZERO -- quindi non era un'asta, e' arrivato
            # prima e basta.
            # Noi la conoscevamo, avevamo l'ordine pronto, la sentinella la
            # metteva fra le candidate. Ma stava a salute 1,0217, cioe' lo
            # 0,17% SOPRA questa soglia: finiva nella corsia lenta e la
            # guardavamo una volta ogni quattro minuti invece che a ogni
            # blocco. E' caduta in quella finestra.
            #
            # Il difetto era di ragionamento: avevo scelto la corsia per
            # vicinanza per risparmiare letture (misurate 55 s per 900
            # posizioni). Ma il risparmio vale secondi e l'errore vale
            # centinaia di migliaia di dollari: il conto non sta in piedi.
            # Ora entra nella corsia veloce chi e' vicino OPPURE chi vale
            # tanto, con la soglia che si allarga col premio:
            #   premio sotto $1.000   -> serve salute < 1,02
            #   premio oltre $10.000  -> basta salute < 1,10
            #   premio oltre $100.000 -> basta salute < 1,25 (tutta la banda)
            def _soglia_per(premio):
                if premio >= 100_000: return 1.25
                if premio >= 10_000:  return 1.10
                if premio >= 1_000:   return 1.05
                return VICINA
            # E LA CORSIA HA UN TETTO, perche' le letture costano tempo.
            # MISURATO il 4/11 sul codice vero (non estrapolato):
            #   165 posizioni -> 7,65 s     366 -> 13,47 s     600 -> 19,29 s
            # Un blocco dura 12 secondi: oltre ~250 posizioni il pescatore
            # non sta piu' dietro a ogni blocco, e una corsia veloce che
            # non e' veloce non e' una corsia veloce.
            # Quindi: dentro ci va chi passa la soglia del suo valore, e se
            # sono troppi si tengono I PIU' PREZIOSI. Prima il criterio era
            # la vicinanza e il valore non contava: e' cosi' che una
            # posizione da $130.841 di premio atteso e' finita in corsia
            # lenta e l'abbiamo perduta.
            TETTO_CORSIA = 250
            ammesse = [(_quanto_vale(u), v["salute"], u)
                       for u, v in letture.items()
                       if v["debito"] > 150
                       and v["salute"] < _soglia_per(_quanto_vale(u))]
            # chi vale piu' prima; a pari valore, chi e' piu' vicino
            ammesse.sort(key=lambda t: (-t[0], t[1]))
            vicine_note = {u for _, _, u in ammesse[:TETTO_CORSIA]}
            if len(ammesse) > TETTO_CORSIA:
                print(f"   corsia veloce piena: {len(ammesse)} candidate, "
                      f"tengo le {TETTO_CORSIA} piu' preziose "
                      f"(dal premio {ammesse[0][0]:,.0f} al "
                      f"{ammesse[TETTO_CORSIA-1][0]:,.0f})")
        # SI PUBBLICA LA TABELLA DELLE SALUTI VIVE, perche' serve alla
        # sentinella.
        #
        # MISURATO il 4/11 sera, ed e' la scoperta che spiega tutti gli
        # zero: un aggiornamento dell'oracolo muove il prezzo dello 0,507%
        # in mediana e dello 0,585% al massimo. Quindi un pacchetto
        # "stesso blocco" puo' funzionare SOLO su posizioni sotto salute
        # ~1,006. Le candidate della sentinella arrivavano a 1,25: per
        # quelle servirebbe un movimento 34 volte il massimo mai visto --
        # posti sprecati per costruzione (0 su 168 avrebbero funzionato).
        # E la sentinella leggeva la salute dall'ARCHIVIO: sulla sconfitta
        # da $947.639 vedeva 1,0217 mentre il vero era 1,0054, cioe'
        # esattamente a tiro. Non poteva saperlo.
        # Il pescatore invece legge il vivo a ogni giro: queste letture
        # sono il dato giusto, e vanno condivise.
        try:
            tmp = "data/liquidazioni/saluti_vive.json.tmp"
            with open(tmp, "w") as _f:
                json.dump({"quando": time.time(),
                           "blocco": ultimo_blocco,
                           "saluti": {u: round(v["salute"], 6)
                                      for u, v in letture.items()}}, _f)
            os.replace(tmp, "data/liquidazioni/saluti_vive.json")
        except OSError: pass
        mute = len(da_leggere) - len(letture)
        viste = len(letture)
        for u,c in lista:
            s=letture.get(u)
            if not s: continue
            if s["salute"]<peggiore[0] and s["debito"]>100:
                peggiore=(s["salute"],u)
            if s["salute"] < 1.0:
                print(f"   !!! CADUTA {u[:14]} salute {s['salute']:.4f} — tento")
                r=tenta(u,c)
                try:
                    with open(REG,"a") as g:
                        g.write(json.dumps({"quando":time.strftime("%Y-%m-%d %H:%M:%S",
                            time.gmtime()), **{k:v for k,v in r.items()}})+"\n")
                except OSError: pass
                print(f"   esito: {json.dumps(r)[:400]}")
                if r.get("riuscita"):
                    preso=True
                    # IL FLAG DELLA PRESA, su file. DIFETTO TROVATO l'1/11:
                    # «preso» esisteva solo in memoria. Il processo usciva, e
                    # la guardia -- che decide guardando questo file -- lo
                    # rialzava come se nulla fosse. E la sentinella, che si
                    # ferma leggendo lo stesso file, avrebbe continuato a
                    # sparare. «Una sola presa e poi si guarda» era una
                    # frase nel commento, non un comportamento.
                    try:
                        with open(f"{os.path.dirname(VITA)}/preso.flag","w") as g:
                            g.write(json.dumps({
                                "quando":time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()),
                                "chi":"pescatore","utente":u,
                                "transazione":r.get("transazione"),
                                "premio_atteso_usd":r.get("premio_atteso_usd")}))
                    except OSError: pass
                    # E POI SI AVVISA. DIFETTO TROVATO il 3/11 sera dal
                    # C-check: qui il pescatore scriveva il flag, stampava
                    # "PRESA" e si fermava -- senza verificare la cassa e
                    # SENZA MANDARE NESSUNA EMAIL. Avvisava solo la
                    # sentinella. Ma il pescatore e' quello che prende le
                    # cadute da SCIVOLAMENTO, cioe' il modo piu' probabile
                    # in cui arriva la prima bolla: il premio sarebbe
                    # finito in cassa e Nicolo' non l'avrebbe saputo.
                    # Quarto guasto della stessa famiglia in un giorno:
                    # ultimo stadio muto, tutto il resto verde.
                    # L'ORDINE conta ed e' la regola di Nicolo': prima si
                    # verifica che i soldi siano nel portafoglio, POI si
                    # avvisa. Ci pensa dopo_la_liquidazione.
                    # Il flag si scrive PRIMA dell'email: se l'avviso
                    # fallisce ci si deve fermare comunque.
                    try:
                        from conferma_e_avvisa import dopo_la_liquidazione
                        dopo_la_liquidazione(
                            c.get("debito_principale"), u,
                            r.get("transazione"),
                            r.get("premio_atteso_usd") or 0,
                            (r.get("premio_atteso_usd") or 0)/0.07,
                            garanzia=str(c.get("garanzia_principale"))[:10])
                        print("   email mandata dopo aver verificato la cassa")
                    except Exception as e:
                        print(f"   AVVISO FALLITO: {str(e)[:150]}")
                    print(f"\n   >>> PRESA. Mi fermo come stabilito. <<<")
                    break
        try:
            json.dump({"pid":os.getpid(),
                       "ultimo":time.strftime("%Y-%m-%d %H:%M:%S",time.gmtime()),
                       "giri":giri,"minuti":round((time.time()-t0)/60,1),
                       "armato":ARMATO,"preso":preso,
                       "sorvegliate":len(lista),
                       "viste":viste,"mute":mute,
                       "blocco":ultimo_blocco,
                   "corsia":"tutte" if tutte else "vicine",
                       "vicine":len(vicine_note),
                       "piu_malata":round(peggiore[0],4) if peggiore[1] else None,
                       "chi":peggiore[1][:12] if peggiore[1] else None},
                      open(VITA,"w"))
        except OSError: pass
        # si aspetta il BLOCCO nuovo, non un tempo fisso: i prezzi in catena
        # cambiano solo quando arriva un blocco, quindi leggere nel mezzo e'
        # lavoro buttato e leggere in ritardo sul blocco e' tempo regalato.
        # DIFETTO MIO, corretto subito: la prima stesura di questo blocco e'
        # finita FUORI dal ciclo per un errore di indentazione (la sostituzione
        # aveva agganciato 4 spazi invece di 8). Risultato: nessuna pausa, il
        # pescatore martellava la fonte a giro continuo. Lo ha rivelato il
        # campo "blocco" del file di vita, che restava a 0.
        for _ in range(40):                  # al massimo ~12 secondi
            b=blocco_ora()
            if b and b!=ultimo_blocco:
                ultimo_blocco=b; break
            time.sleep(0.3)
    print(f"\n   {giri} giri | {'PRESO' if preso else 'nessuna caduta'}")


if __name__ == "__main__":
    main()
