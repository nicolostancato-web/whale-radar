"""Leggere Uniswap v4, la piazza dove la liquidita' e' migrata.

PERCHE' ESISTE (5/11). Avevamo misurato che la maggior parte della liquidita'
dei nostri gettoni sta su Uniswap v4 (cbBTC 99%, LBTC 100%, sUSDe 100%,
wstETH 81%, WBTC 76%, USDT 65%) e il nostro codice NON sapeva leggerla: una
cecita' che risponde "zero" invece di "non lo so", ed e' il peggiore dei due.

MISURATO SUBITO, con i prezzi dell'oracolo (non con prezzi a memoria: la
prima versione di questa misura usava 104.000 $ per il Bitcoin mentre
l'oracolo ne diceva 79.870, e le rese sembravano del 77%):
    WBTC->USDC  99,82%     WBTC->WETH  100,21%
    cbBTC->USDC 99,70%     wstETH->WETH 99,67%
    USDT->USDC  99,99%     USDT->WETH   99,92%
Tutte sopra la nostra soglia di resa. Qui c'e' strada.

COSA MANCA ANCORA: comporre la calldata di scambio (si passa dall'Universal
Router, non da un router semplice come in v3). Questo modulo per ora LEGGE:
serve a scegliere la sede e a sapere quanto si prende, e dice la verita' su
cosa esiste invece di far finta che non ci sia niente.
"""
import json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pescatore import rpc

CAST = os.path.expanduser("~/.foundry/bin/cast")
# verificati in catena il 5/11 (hanno codice): non sono indirizzi presi da un
# articolo, e il selettore sotto viene da `cast sig`.
QUOTER = "0x52f0e24d1c21c8a0cb1e5a5dd6198556bd9e1203"
POOL_MANAGER = "0x000000000004444c5dc75cb358380d2e3de08a90"
UNIVERSAL_ROUTER = "0x66a9893cc07d91d95644aedd05d03f95e1dba8af"
NATIVO = "0x0000000000000000000000000000000000000000"
SENZA_GANCI = "0x0000000000000000000000000000000000000000"
FIRMA_QUOTA = ("quoteExactInputSingle(((address,address,uint24,int24,address),"
               "bool,uint128,bytes))")
# in v4 la coppia (commissione, passo del tick) non e' libera: queste sono
# le combinazioni standard, e si provano tutte perche' la pozza buona puo'
# stare su qualunque livello.
LIVELLI = ((100, 1), (500, 10), (3000, 60), (10000, 200))


def _calldata(c0, c1, fee, ts, zero_per_uno, q):
    a = (f"(({c0},{c1},{fee},{ts},{SENZA_GANCI}),"
         f"{'true' if zero_per_uno else 'false'},{q},0x)")
    r = subprocess.run([CAST, "calldata", FIRMA_QUOTA, a],
                       capture_output=True, text=True).stdout.strip()
    return r if r.startswith("0x") else None


def quota(src, dst, q, dst_e_weth=False):
    """Quanto rende vendere q di src verso dst su v4. (uscita, fee, dst_usato).

    Si prova anche con l'ETH NATIVO al posto del WETH: in v4 l'ether non e'
    avvolto, e la pozza buona di wstETH e di WBTC sta proprio sul nativo --
    cercare solo il WETH avrebbe risposto "nessuna pozza" su entrambe.
    """
    src = src if src.startswith("0x") else "0x" + src
    candidati = [dst] + ([NATIVO] if dst_e_weth else [])
    meglio = None
    for d in candidati:
        c0, c1 = (src, d) if int(src, 16) < int(d, 16) else (d, src)
        zpu = c0.lower() == src.lower()
        for fee, ts in LIVELLI:
            cd = _calldata(c0, c1, fee, ts, zpu, q)
            if not cd:
                continue
            r = rpc("eth_call", [{"to": QUOTER, "data": cd}, "latest"], giri=1)
            if isinstance(r, str) and len(r) > 2 and int(r[2:66], 16) > 0:
                out = int(r[2:66], 16)
                if meglio is None or out > meglio[0]:
                    meglio = (out, fee, d)
    return meglio


# ---------------------------------------------------------------------------
# COMPORRE LO SCAMBIO, provato eseguendolo sul fork il 5/11.
#
# NON e' una ricostruzione da documentazione: la sequenza qui sotto ha
# scambiato davvero 0,01 WBTC ricevendo 0,3322 ETH (100,57% di resa al netto
# del gas) su una copia della catena. I valori delle azioni erano una mia
# ipotesi e li ho verificati ESEGUENDO, non leggendo.
#
# La forma: UniversalRouter.execute(comandi, ingressi, scadenza)
#   comandi  = 0x10                       -> un solo comando: scambio su v4
#   ingressi = [ abi.encode(azioni, parametri[]) ]
#   azioni   = 0x06 0x0c 0x0f             -> scambia esatto in ingresso,
#                                            paga tutto, prendi tutto
#   parametri[0] = (chiaveDellaPozza, zeroVersoUno, quantita, minimoInUscita, ganci)
#   parametri[1] = (gettoneCheEsce, quantita)        per "paga tutto"
#   parametri[2] = (gettoneCheEntra, minimo)         per "prendi tutto"
#
# IL PREZZO DA PAGARE: il router preleva tramite PERMIT2, quindi servono DUE
# autorizzazioni (il gettone verso Permit2, e Permit2 verso il router). La
# catena di passaggi del nostro contratto ne fa una per passaggio, quindi
# serve un passaggio in piu'.
#
# IL LIMITE, misurato: la pozza migliore di WBTC e wstETH sta sull'ETH
# NATIVO, e "prendi tutto" consegna ether, non WETH. Il nostro contratto
# chiama senza valore, quindi non sa riavvolgerlo: oggi v4 e' usabile dove
# l'uscita e' un gettone normale (USDC, USDT), che e' comunque il caso della
# maggior parte dei debiti che ci interessano. Avvolgere l'ether e' il
# prossimo pezzo, e va fatto nel contratto, non qui.
# PROVATO ESEGUENDO, due volte, sul fork (5/11):
#   0,01 WBTC -> 0,3322 ETH nativo   = 100,57% di resa
#   0,01 WBTC -> 802,71 USDC         = 100,50% di resa
# con la calldata composta da questo modulo, non a mano.
#
# E UN INCIAMPO CHE VALE OLTRE QUESTO CODICE: la prima prova e' fallita con
# "Blacklistable: account is blacklisted" e per un attimo sembrava un difetto
# dell'encoder. Era l'indirizzo che impersonavo (una grande piazza di
# scambio) a essere in LISTA NERA su USDC -- `isBlacklisted` dice true.
# Una prova puo' fallire per colpa del proprio banco di prova: prima di
# accusare il codice, si controlla il banco.
#
# E LO STESSO INCIAMPO, UN'ORA DOPO, in forma peggiore: lo scambio verso
# ether "riusciva" ma il saldo del conto non saliva, e sembrava che il
# ricavato svanisse -- il guasto piu' grave immaginabile. La traccia ha
# mostrato `take(nativo, conto, 0,3321 ETH)`: l'ether ARRIVAVA, e poi il
# conto lo inoltrava da se'. Motivo: i conti predefiniti di anvil hanno,
# sul fork di mainnet, codice 0xef0100... cioe' una DELEGA EIP-7702 a un
# contratto che gira l'ether altrove.
# REGOLA: per provare che un VALORE arriva, usare un indirizzo senza
# codice. Con un indirizzo pulito il saldo e' passato da 0,999998 a
# 1,332108 ETH. Due volte nella stessa sera il banco di prova mi ha fatto
# sospettare il codice.
PERMIT2 = "0x000000000022d473030f116ddee9f6b43ac78ba3"
COMANDO_V4 = "0x10"
AZIONI = "0x060c0f"
FIRMA_ESEGUI_UR = "execute(bytes,bytes[],uint256)"
FIRMA_P0 = ("f(((address,address,uint24,int24,address),bool,uint128,uint128,"
            "bytes))")
FIRMA_COPPIA = "f(address,uint128)"
FIRMA_INGRESSO = "f(bytes,bytes[])"


def _cod(firma, *args):
    r = subprocess.run([CAST, "abi-encode", firma, *args],
                       capture_output=True, text=True).stdout.strip()
    return r if r.startswith("0x") else None


MAX128 = (1 << 128) - 1


def scambio(src, dst, fee, ts, q, minimo=1, scadenza=4_000_000_000,
            con_posizione=False):
    """La calldata per vendere q di src verso dst su v4.

    Con con_posizione=True torna (calldata, posizione) dove posizione e'
    l'offset in byte della QUANTITA' dentro la calldata: il contratto la
    riscrive da se', perche' quanta garanzia si incassa si scopre solo
    dentro l'operazione.
    Il "paga tutto" porta un MASSIMO, non la quantita' esatta, proprio
    perche' cosi' c'e' un solo punto da riscrivere invece di due: due punti
    da tenere d'accordo sono due occasioni di sbagliarne uno.
    L'uscita in ETHER ORA SI PUO': il contratto avvolge l'ether nudo
    all'inizio di ogni passaggio e alla fine della catena (vedi _avvolgi).
    """
    c0, c1 = (src, dst) if int(src, 16) < int(dst, 16) else (dst, src)
    zpu = "true" if c0.lower() == src.lower() else "false"

    def componi(quanto):
        p0 = _cod(FIRMA_P0, f"(({c0},{c1},{fee},{ts},{SENZA_GANCI}),"
                            f"{zpu},{quanto},{minimo},0x)")
        p1 = _cod(FIRMA_COPPIA, src, str(MAX128))
        p2 = _cod(FIRMA_COPPIA, dst, str(minimo))
        if not (p0 and p1 and p2):
            return None
        ing = _cod(FIRMA_INGRESSO, AZIONI, f"[{p0},{p1},{p2}]")
        if not ing:
            return None
        r = subprocess.run([CAST, "calldata", FIRMA_ESEGUI_UR,
                            COMANDO_V4, f"[{ing}]", str(scadenza)],
                           capture_output=True, text=True).stdout.strip()
        return r if r.startswith("0x") else None

    cd = componi(q)
    if not cd or not con_posizione:
        return cd
    # DOVE STA LA QUANTITA': non si indovina, si CERCA. Si compone una
    # seconda volta con un valore sentinella e si guarda dove e' cambiato.
    # Un offset calcolato a mano e' un numero che invecchia al primo campo
    # aggiunto; cercato, si aggiorna da se'.
    sentinella = 0xDEADBEEF12345678
    alt = componi(sentinella)
    if not alt or len(alt) != len(cd):
        return None
    parola = hex(sentinella)[2:].rjust(64, "0")
    i = alt[2:].lower().find(parola)
    if i < 0 or i % 2:
        return None
    return cd, i // 2
