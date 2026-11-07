"""ARCHITETTURA NUOVA: non prevedere, ma farsi pagare per fornire il lato che
manca.

Quando il tasso di finanziamento e' positivo, chi e' lungo paga chi e' corto
ogni ora. Stando corti sul perpetuo e lunghi sul pronto per la stessa quantita'
si e' NEUTRALI al prezzo: non importa dove va il mercato, si incassa il
finanziamento. Non e' una previsione — e' il prezzo di un servizio.

Cosa si sopporta davvero (e quindi perche' pagano): il capitale immobilizzato
su due gambe, il rischio che il tasso diventi negativo, e il rischio di base
fra pronto e perpetuo.

Dati: 178 mercati Hyperliquid, 637.000 letture orarie gia' scaricate.
Costo di ingresso/uscita: 4 gambe (apri perp + apri pronto, chiudi entrambi).
Su Hyperliquid 0,045% per gamba da chi prende il prezzo = 0,18% una volta sola,
non per ciclo: si entra e si resta.
"""
import json, glob, os, statistics as st, math
ING=4*0.00045        # 4 gambe, una volta sola
mercati=[]
for f in sorted(glob.glob("data/finanziamento/*.json")):
    d=json.load(open(f))
    if len(d)>2000:
        mercati.append((os.path.basename(f)[:-5], sorted(((x["time"], float(x["fundingRate"])) for x in d))))
print(f"{len(mercati)} mercati | {sum(len(m[1]) for m in mercati):,} letture orarie\n")
print("   durata    incasso lordo    meno ingresso    quanti mercati pagano")
for ore in (24, 24*7, 24*30):
    res=[]
    for nome,serie in mercati:
        if len(serie)<ore+10: continue
        # si entra all'inizio e si tiene: si sommano i tassi orari del periodo
        for inizio in range(0, len(serie)-ore, ore):
            tot=sum(t for _,t in serie[inizio:inizio+ore])
            res.append(tot)
    if len(res)<50: continue
    m=st.mean(res); e=1.96*st.stdev(res)/math.sqrt(len(res))
    netto=m-ING
    pos=sum(1 for x in res if x-ING>0)
    print(f"   {ore:>5}h   {m*100:+7.4f}% +/-{e*100:5.4f}   {netto*100:+7.4f}%   "
          f"{pos}/{len(res)} periodi positivi")
print("\n   NB: incasso del FINANZIAMENTO soltanto. Mancano ancora: il costo di")
print("       tenere la gamba a pronto, e il rischio che il tasso diventi negativo.")
