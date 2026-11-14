# -*- coding: utf-8 -*-
"""COSTRUISCE LA DOMANDA PER I REVISORI ESTERNI, dallo stato di ADESSO.

Perche' esiste (4/11 sera). Il primo consulto l'ho scritto a mano, e la
domanda era buona perche' la situazione era fresca. Ma fra una settimana,
scritta a mano, chiederei ancora le cose di oggi. La domanda va GENERATA
dallo stato del momento: blocchi e percentuali, punteggio del tabellone,
cosa e' cambiato dall'ultimo consulto, e -- la parte che vale -- **cosa non
sappiamo spiegare**.

REGOLA IMPARATA A CARO PREZZO nel primo consulto: nel prompt vanno solo
cose MISURATE. Avevo scritto che un pagamento di 210 ETH era una mancia del
vincitore (era il builder che pagava il validatore, cosa presente in quasi
ogni blocco) ed entrambi i revisori hanno costruito la tesi centrale su
quell'errore. **I revisori amplificano quello che gli dai, errori
compresi.** Quindi: ogni numero in questo prompt viene da un file misurato,
e le cose incerte si dichiarano incerte.
"""
import json, os, sys, time
D = "data/liquidazioni"
def L(f, d=None):
    try: return json.load(open(f"{D}/{f}.json"))
    except Exception: return d
def costruisci():
    bl = L("blocchi", {}) or {}
    tb = L("tabellone", {}) or {}
    sv = L("storico_vincitori", {}) or {}
    sb = L("spazio_nel_blocco", {}) or {}
    cr = L("crescita_check", {}) or {}
    ch = L("check_finale", {}) or {}
    cassa = L("cassa", {}) or {}
    pezzi = []
    pezzi.append("""Sei un ingegnere MEV senior con dieci anni su Ethereum: hai costruito e
gestito bot di liquidazione su Aave, Compound, Morpho. Sei pagato per
demolire, non per incoraggiare. Se l'impostazione e' sbagliata lo dici alla
prima riga. Ogni numero qui sotto e' MISURATO sulla catena, non stimato;
dove non sappiamo, c'e' scritto che non sappiamo.""")
    pezzi.append("\n=== DOVE SIAMO ADESSO ===\n")
    pezzi.append(f"Cassa: {cassa.get('valore_usd','?')} USD. Prese: ZERO, mai vinta una liquidazione.")
    if bl.get("righe"):
        pezzi.append("I sei blocchi di autodiagnosi, con la percentuale calcolata "
                     "dalle verifiche verdi (non stimata):")
        for r in bl["righe"]:
            c = r.get("colpa_dal_tabellone")
            extra = (f"  [il tabellone gli ha dato la colpa di "
                     f"${c['premio_perso']:,.0f} persi: {c['perche']}]") if c and c.get("punti") else ""
            pezzi.append(f"  {r['blocco']}: {r['percento']}% "
                         f"({r['verdi']}/{r['verifiche']} verifiche verdi){extra}")
        if bl.get("righe"):
            rossi = [x for r in bl["righe"] for x in (r.get("rossi") or [])]
            if rossi:
                pezzi.append("  verifiche rosse adesso: " + "; ".join(rossi[:6]))
    if tb:
        pezzi.append(f"\nTabellone (ultime {tb.get('ore','?')} ore): "
                     f"{tb.get('quante','?')} liquidazioni vere, premio passato "
                     f"${(tb.get('premio_nostro',0)+tb.get('premio_altrui',0)):,.0f}, "
                     f"preso da noi ${tb.get('premio_nostro',0):,.0f}.")
        for r in (tb.get("liquidazioni") or [])[:3]:
            pezzi.append(f"  ${r.get('premio_vero_usd',0):,.0f}: {r.get('motivo')}")
    if sv:
        pezzi.append(f"\nStorico {sv.get('giorni')} giorni: {sv.get('liquidazioni')} "
                     f"liquidazioni, ${sv.get('premio_totale',0):,.0f} di premio "
                     f"(${sv.get('premio_al_giorno',0):,.0f}/giorno). "
                     f"{sv.get('vincitori_distinti')} vincitori, {sv.get('vincitori_ripetuti')} "
                     f"ripetuti che prendono il {sv.get('quota_dei_ripetuti')}%; i primi tre il "
                     f"{sv.get('quota_dei_primi_tre')}%. Premio mediano "
                     f"${sv.get('premio_mediano',0):,.0f}; sopra $10.000 solo "
                     f"{sv.get('sopra_diecimila')} eventi nel periodo.")
    if sb:
        pezzi.append(f"\nSpazio nel blocco: delle {sb.get('liquidazioni')} liquidazioni "
                     f"sopra ${sb.get('minimo',0):,.0f}, i blocchi li costruiscono "
                     f"{len(sb.get('costruttori') or [])} soggetti. Noi consegniamo a "
                     f"{len(sb.get('porte_nostre') or [])} porte e copriamo il "
                     f"{sb.get('quota_coperta')}% del premio.")
        for c in (sb.get("costruttori") or []):
            pezzi.append(f"  {c['chi']}: {c['quota']}% del premio, "
                         f"gli consegniamo: {'si' if c['gli_consegniamo'] else 'NO'}")
    if cr.get("giri"):
        ultimi = cr["giri"][-3:]
        pezzi.append("\n=== COSA ABBIAMO RIPARATO NEGLI ULTIMI GIRI ===")
        for g in ultimi:
            pezzi.append(f"  {g.get('quando')}: {str(g.get('aggiunta'))[:400]}")
    pezzi.append("""
=== QUELLO CHE NON SAPPIAMO SPIEGARE ===
1. Abbiamo consegnato oltre 12.000 pacchetti ACCETTATI dal relay e ZERO sono
   stati inclusi. Fino a stasera consegnavamo a una porta sola (Flashbots) che
   non ha costruito NESSUNO dei blocchi delle liquidazioni che contano: e' la
   spiegazione che ci siamo dati, ma non l'abbiamo ancora verificata vincendo.
2. Non sappiamo se i vincitori paghino una mancia dentro la transazione
   (trasferimento a block.coinbase): il nodo pubblico non traccia le chiamate
   interne e non abbiamo trovato un altro modo. Finche' non lo sappiamo, non
   sappiamo quanto serve offrire.
3. Non sappiamo misurare "accettato -> incluso" per singolo costruttore.

=== LE DOMANDE ===
1. La spiegazione al punto 1 (consegnavamo al costruttore sbagliato) regge, o
   e' una spiegazione comoda? Cosa controlleresti per falsificarla?
2. Come misureresti il punto 2 senza un nodo che traccia? C'e' un modo
   indiretto affidabile?
3. Dato lo stato qui sopra, qual e' LA PROSSIMA COSA da fare, una sola, che
   massimizza la probabilita' della prima presa? E cosa NON faresti?
4. Quale cecita' vedi che non e' nella lista "quello che non sappiamo"?

FORMATO: risposta secca in una riga, poi il perche', poi cosa misurare.
Niente incoraggiamenti, niente riassunti di quello che ti ho scritto.""")
    return "\n".join(pezzi)
if __name__ == "__main__":
    t = costruisci()
    p = "/tmp/domanda_per_fuori.txt"
    open(p, "w").write(t)
    print(f"   domanda costruita: {len(t)} caratteri -> {p}")
