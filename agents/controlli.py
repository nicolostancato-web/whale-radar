#!/usr/bin/env python3
"""
CONTROLLI — la cassetta degli attrezzi per non prendere il rumore per un vantaggio.

Nata il 02/09 dalla consulenza esterna, che ha demolito il modo in cui misuravamo. Tre errori
ripetuti in ogni test fatto finora, e qui vengono chiusi una volta per tutte:

  1. CONFRONTO SBAGLIATO. Confrontavamo una strategia con "un token a caso". Ma se il nostro
     segnale pesca token appena nati e illiquidi, e il caso pesca l'intero universo, stiamo
     confrontando due mercati diversi, non due bravure. La domanda giusta e':
     *a parita' di opportunita' disponibili in quel momento, quel segnale aggiunge informazione?*
     -> matched(): controlli appaiati per eta' e liquidita'.

  2. ORIZZONTE UNICO. Tenevamo 24 ore fisse. Un segnale che vale 30 minuti risultava morto non
     perche' non c'era, ma perche' guardavamo troppo tardi. -> markout(): 5m/30m/2h/6h/24h,
     orizzonti fissati QUI, prima di vedere i dati, per non sceglierli dopo.

  3. FINTA ABBONDANZA. 32.749 acquisti non sono 32.749 esperimenti: lo stesso wallet che compra
     lo stesso token cinque volte non e' cinque prove della sua bravura. -> unita_indipendenti().

E in piu' il pezzo che ci mancava del tutto: i CLUSTER. Trenta wallet diversi finanziati dallo
stesso portafoglio non sono trenta compratori, sono UNA entita'. Non abbiamo i funder su tutte le
chain, ma non servono: chi appartiene alla stessa entita' si tradisce COMPORTANDOSI uguale —
compra gli stessi token negli stessi secondi, ripetutamente. -> cluster(): gratis, su ogni chain.
"""
import json, os, gzip, time, math, sys
from collections import defaultdict
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import multichain_brain as B

ORIZZONTI = [300, 1800, 7200, 21600, 86400]        # 5m, 30m, 2h, 6h, 24h — fissati PRIMA di guardare
ETICHETTE = {300: "5 min", 1800: "30 min", 7200: "2 ore", 21600: "6 ore", 86400: "24 ore"}
FINESTRA_CLUSTER = 120                              # due wallet "insieme" se comprano entro 2 minuti
MIN_INSIEME = 3                                     # e se lo fanno su almeno 3 token diversi


# ---------------------------------------------------------------- serie e profilo
def serie(chain, limite=None):
    """{addr: [[ts, op, hi, lo, cl, vol], ...]} ordinate nel tempo."""
    out = {}
    for f in B.serie_files(chain):
        if limite and len(out) >= limite: break
        addr = os.path.basename(f).replace(".jsonl.gz", "")
        try:
            cs = []
            for l in gzip.open(f, "rt"):
                d = json.loads(l)
                if d.get("cl"): cs.append([int(d["ts"]), d.get("op"), d.get("hi"), d.get("lo"),
                                           d["cl"], d.get("vol") or 0])
            if len(cs) >= B.MIN_CANDLES: cs.sort(); out[addr] = cs
        except Exception: pass
    return out


def profilo(cs):
    """(nascita, fine) — quando il token e' comparso e quando finiscono i nostri dati."""
    return cs[0][0], cs[-1][0]


def volume_prima(cs, ts, finestra=3600):
    """quanto girava nell'ora prima di ts: la nostra misura di liquidita' senza dati esterni."""
    return sum(c[5] or 0 for c in cs if ts - finestra <= c[0] < ts)


def _fascia(x, base=4.0):
    """fasce logaritmiche: due token sono 'simili' se stanno nella stessa fascia, non se hanno
    lo stesso numero. Un token da 900$ e uno da 1.100$ di volume sono la stessa cosa."""
    return int(math.log(max(x, 1.0), base))


# ---------------------------------------------------------------- controlli appaiati
class Universo:
    """L'insieme delle occasioni disponibili istante per istante — serve a rispondere alla domanda
    giusta: non 'ha guadagnato?', ma 'ha guadagnato piu' di quello che potevi comprare comunque?'"""

    def __init__(self, chain, limite=None):
        self.cs = serie(chain, limite)
        self.nasce = {a: c[0][0] for a, c in self.cs.items()}
        self.muore = {a: c[-1][0] for a, c in self.cs.items()}
        self.ordine = sorted(self.cs, key=lambda a: self.nasce[a])

    def vivi(self, ts):
        return [a for a in self.ordine if self.nasce[a] <= ts <= self.muore[a]]

    def matched(self, addr, ts, k=5, candidati=None):
        """k token CONFRONTABILI con addr all'istante ts: stessa fascia di eta' e di liquidita'.
        Se non ne trova abbastanza allarga solo l'eta' — mai la liquidita', che e' quella che
        decide davvero quanto ti costa uscire."""
        cs = self.cs.get(addr)
        if not cs: return []
        eta = _fascia(max(ts - self.nasce[addr], 60), 3.0)
        vol = _fascia(volume_prima(cs, ts))
        pool = candidati if candidati is not None else self.vivi(ts)
        stretti, larghi = [], []
        for a in pool:
            if a == addr: continue
            c2 = self.cs[a]
            if _fascia(volume_prima(c2, ts)) != vol: continue
            if _fascia(max(ts - self.nasce[a], 60), 3.0) == eta: stretti.append(a)
            else: larghi.append(a)
            if len(stretti) >= k: break
        return (stretti + larghi)[:k]


# ---------------------------------------------------------------- markout
def prezzo_a(cs, quando):
    for c in cs:
        if c[0] >= quando and c[4]: return c[4]
    return None


def markout(cs, ts, orizzonti=None):
    """{orizzonte: rendimento LORDO} entrando a ts. Lordo di proposito: prima si guarda se
    l'informazione ESISTE, poi se sopravvive ai costi. Invertire i due passi fa buttare via
    segnali veri per colpa di un modello di costo sbagliato — ed e' successo."""
    out = {}
    e = prezzo_a(cs, ts)
    if not e or e <= 0: return out
    for h in (orizzonti or ORIZZONTI):
        u = prezzo_a(cs, ts + h)
        if u: out[h] = u / e - 1
    return out


def excess(cs_seg, cs_ctrl, ts, orizzonti=None):
    """quanto ha reso IN PIU' dei suoi controlli. E' questo il numero che conta."""
    a = markout(cs_seg, ts, orizzonti)
    if not a: return {}
    ctrl = [markout(c, ts, orizzonti) for c in cs_ctrl]
    out = {}
    for h, v in a.items():
        base = [c[h] for c in ctrl if h in c]
        if base: out[h] = v - sum(base) / len(base)
    return out


def placebo(cs, ts, orizzonti=None):
    """Il controllo ALL'INDIETRO: cos'era successo PRIMA del segnale.
    Se un segnale 'predice' anche il passato, non sta predicendo: sta guardando qualcosa che
    era gia' successo (momentum), oppure gli e' finito dentro un dato che non poteva avere."""
    out = {}
    e = prezzo_a(cs, ts)
    if not e or e <= 0: return out
    for h in (orizzonti or ORIZZONTI):
        p = prezzo_a(cs, ts - h)
        if p: out[h] = e / p - 1
    return out


# ---------------------------------------------------------------- cluster
def cluster(chain, addrs=None, max_token=1200):
    """{wallet: id_entita'} dedotto dal COMPORTAMENTO.

    Non abbiamo i funder su tutte le chain, ma non servono per la domanda che ci interessa:
    due wallet che ricompaiono INSIEME, entro due minuti, su almeno tre token diversi, non sono
    due persone che hanno avuto la stessa idea tre volte. Sono la stessa mano.
    Serve a non scambiare uno sciame di wallet di una sola entita' per 'trenta compratori indipendenti'."""
    insieme = defaultdict(set)
    tokens = addrs if addrs is not None else [
        os.path.basename(f).replace(".jsonl.gz", "")
        for f in sorted(B.trade_files(chain))[:max_token]] if hasattr(B, "trade_files") else []
    if not tokens:
        import glob
        tokens = [os.path.basename(f).replace(".jsonl.gz", "")
                  for f in sorted(glob.glob(f"data/multichain/{chain}/trades/*.jsonl.gz"))[:max_token]]
    for tk in tokens:
        buys = sorted((int(t["ts"]), t["w"]) for t in B.load_trades(chain, tk)
                      if t.get("kind") == "buy" and t.get("w") and t.get("ts"))
        for i, (ts, w) in enumerate(buys):
            for ts2, w2 in buys[i + 1:]:
                if ts2 - ts > FINESTRA_CLUSTER: break
                if w2 != w: insieme[tuple(sorted((w, w2)))].add(tk)
    padre = {}
    def radice(x):
        while padre.get(x, x) != x: x = padre[x]
        return x
    for (a, b), tk in insieme.items():
        if len(tk) < MIN_INSIEME: continue
        ra, rb = radice(a), radice(b)
        if ra != rb: padre[ra] = rb
    return {w: radice(w) for w in {x for c in insieme for x in c}}


def unita_indipendenti(eventi, chiave_cluster=None):
    """Tiene solo la PRIMA decisione di ogni (entita' x token).
    Lo stesso wallet che ricompra lo stesso token non e' una nuova prova della sua bravura:
    e' la stessa opinione ripetuta. Contarla dieci volte gonfia il campione e non l'evidenza."""
    visti, out = set(), []
    for ev in sorted(eventi, key=lambda e: e[0]):
        ts, w, addr = ev[0], ev[1], ev[2]
        k = ((chiave_cluster or {}).get(w, w), addr)
        if k in visti: continue
        visti.add(k); out.append(ev)
    return out
