"""Il bersaglio cambia: non «quanto rende» ma «va a zero si' o no».

PERCHE' QUESTO FILE ESISTE (4/10). La decomposizione di stasera
(RILEVATORE_DI_AZZERAMENTI.md) dice che su base quattro quinti del vantaggio vengono
dall'EVITARE le monete che muoiono, non dal prendere quelle che salgono. E che fra i
sopravvissuti il quinto migliore rende +7,0%: il conto resta sotto zero solo per l'8,6%
che muore comunque.

Quindi la domanda utile non e' piu' «quale rende» ma «quale muore». E' una domanda
BINARIA, quindi:
  - il fondale e' noto e non e' una media trascinata dalle code (31,5% su base);
  - non serve il prezzo d'uscita per giudicarla, serve solo sapere se c'e' stata;
  - un vantaggio di pochi punti sul rendimento e' rumore, ma dieci punti di
    azzeramento in meno valgono dieci punti di capitale.

LA REGOLA DEL METRO MISURATO VALE IDENTICA. Qui si misura anche la versione a etichette
rimescolate: se mescolo «e' morta / non e' morta» e cerco con la stessa fatica, il meglio
che trovo e' il tetto del caso. Una separazione sotto quel tetto non e' una scoperta,
e' quanto si trova cercando in un mazzo senza struttura.

E LA COPERTURA SI STAMPA SEMPRE ACCANTO AL TASSO (lezione del 24/09, famiglia
«rapporto != copertura»): una condizione che evita il 100% degli azzeramenti su undici
pool non e' un filtro, e' un aneddoto. Quindi ogni riga porta quanti pool tiene.
"""
import json
import os
import numpy as np
from combinazioni import carica, condizioni, maschera

MORTA = -0.99          # bersaglio <= questo = si e' perso tutto
MIN_POOL = 200          # sotto questa copertura non si giudica: e' un aneddoto
RIMESCOLATE = int(os.environ.get("RIMESCOLATE", 20))


def tasso(morti, masc):
    if masc.sum() < MIN_POOL:
        return None, 0
    return float(morti[masc].mean()), int(masc.sum())


def migliori(righe, morti, nomi, quante=10, rimescola=False, seme=0):
    """Le `quante` condizioni che piu' abbassano il tasso di morte, sul pezzo di ricerca."""
    m = morti.copy()
    if rimescola:
        np.random.default_rng(seme).shuffle(m)
    fondale = float(m.mean())
    fuori = []
    for c in condizioni(righe, nomi):
        t, q = tasso(m, maschera(righe, c))
        if t is None:
            continue
        fuori.append((fondale - t, c, q))
    fuori.sort(key=lambda z: -z[0])
    return fuori[:quante], fondale


def giudica(righe, morti, scelte):
    """Le condizioni scelte, misurate sul pezzo mai visto. Nessuna soglia ritoccata qui."""
    fondale = float(morti.mean())
    fuori = []
    for _, c, _ in scelte:
        t, q = tasso(morti, maschera(righe, c))
        if t is None:
            continue
        fuori.append((fondale - t, c[0], t, q, q / len(righe)))
    fuori.sort(key=lambda z: -z[0])
    return fuori, fondale


def main():
    chain = os.environ.get("CHAIN", "base")
    righe = carica(chain)
    nomi = sorted(k for k in righe[0] if not k.startswith("_"))
    morti = np.array([1.0 if x["_bersaglio"] <= MORTA else 0.0 for x in righe])
    n = len(righe)
    a, b = int(n * 0.45), int(n * 0.72)
    rc, rs, rg = righe[:a], righe[a:b], righe[b:]
    mc, ms, mg = morti[:a], morti[a:b], morti[b:]
    print(f"AZZERAMENTO | {chain}: {n:,} pool, {morti.mean():6.1%} muoiono "
          f"(cerco {len(rc):,} / scelgo {len(rs):,} / giudico {len(rg):,} mai visti)",
          flush=True)

    # cerco sul primo pezzo, scelgo le dieci migliori col secondo, giudico col terzo
    dieci, _ = migliori(rc, mc, nomi, quante=40)
    riscelte, _ = giudica(rs, ms, dieci)
    scelte = [(v, (nome, None, None, None), q) for v, nome, _, q, _ in riscelte[:10]]
    # ricostruisco le condizioni vere per nome (la tupla serve a maschera())
    per_nome = {c[0]: c for c in condizioni(rc, nomi)}
    scelte = [(v, per_nome[nome], q) for v, nome, _, q, _ in riscelte[:10] if nome in per_nome]
    vere, fondale_g = giudica(rg, mg, scelte)

    # IL METRO MISURATO: la stessa fatica su etichette rimescolate.
    tetti = []
    for s in range(RIMESCOLATE):
        d, _ = migliori(rc, mc, nomi, quante=40, rimescola=True, seme=s)
        r, _ = giudica(rs, ms, d)
        sc = [(v, per_nome[nome], q) for v, nome, _, q, _ in r[:10] if nome in per_nome]
        if not sc:
            continue
        mgf = mg.copy()
        np.random.default_rng(1000 + s).shuffle(mgf)
        vf, _ = giudica(rg, mgf, sc)
        if vf:
            tetti.append(vf[0][0])
    metro = max(tetti) if tetti else None

    print(f"\n   fondale sul pezzo mai visto: {fondale_g:.1%} muoiono")
    if metro is not None:
        print(f"   metro misurato su {len(tetti)} rimescolate: "
              f"{metro:+.1f} punti (sotto questo e' caso)")
    print(f"\n   {'condizione':<42} {'muoiono':>9} {'punti':>8} {'pool':>7} {'copre':>7}")
    for v, nome, t, q, frazione in vere[:10]:
        segno = "  <-- batte il caso" if metro is not None and v > metro else ""
        print(f"   {nome:<42} {t:8.1%} {v*100:+7.1f} {q:7,} {frazione:6.1%}{segno}")

    passate = [z for z in vere if metro is not None and z[0] > metro]
    os.makedirs("data", exist_ok=True)
    json.dump({"chain": chain, "pool": n, "fondale": fondale_g, "metro": metro,
               "quante_passano": len(passate),
               "righe": [{"condizione": nome, "muoiono": t, "punti": v,
                          "pool": q, "copre": frazione}
                         for v, nome, t, q, frazione in vere]},
              open(f"data/azzeramento_{chain}.json", "w"), ensure_ascii=False, indent=1)
    print(f"\n   {len(passate)} condizioni su {len(vere)} battono il metro misurato", flush=True)


if __name__ == "__main__":
    main()
