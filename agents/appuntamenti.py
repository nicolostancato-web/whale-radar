#!/usr/bin/env python3
"""GLI APPUNTAMENTI: le posizioni che cadranno DA SOLE, e in quale blocco.

Nata dalla quattordicesima liquidazione (7/11, premio 141,12 $, garanzia e
debito nello stesso gettone quindi senza nemmeno vendere). Quella posizione
non e' caduta per un prezzo nuovo: la sua salute scendeva DA SOLA di 3,5
miliardi di unita' per blocco, lineare su 300 blocchi, perche' gli interessi
sul debito maturano. Al blocco prima stava 1,21 miliardi sopra l'uno, cioe'
a tre decimi di blocco dall'attraversamento. Era un APPUNTAMENTO, e noi
stavamo aspettando di VEDERLA scendere.

La differenza che conta:
  - una caduta da ORACOLO e' una gara di 80-250 millisecondi e si vince solo
    decodificando la transazione d'oracolo in attesa;
  - una caduta da DERIVA si CALCOLA con ore di anticipo e non ha gara. Basta
    avere il pacchetto pronto per il blocco giusto.

Misurato sulle 14 liquidazioni: la gara vale 10 casi e 7.531 $, la corsia
lenta 4 casi e 142 $. La corsia lenta e' piccola, ma e' la sola che si vince
con CERTEZZA -- e 141 $ sono 700 volte la nostra cassa.

ATTENZIONE A NON GENERALIZZARE DA UN CASO: la deriva si misura per OGNI
posizione, perche' dipende dal tasso del suo debito e dalla sua
composizione. Una posizione che non scende non e' un appuntamento, e
prometterle un blocco sarebbe inventare.
"""
import json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import registri as R

D = "data/liquidazioni"
POOL = "0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2"
UNO = 10 ** 18
PASSO_INDIETRO = 150        # su quanti blocchi si misura la pendenza
QUANTE = 60                 # le piu' vicine: leggere costa
ORIZZONTE_BLOCCHI = 7200    # ~24 ore


def _c(m, p, archivio=True):
    fonti = [u for u in R.FONTI if "publicnode" not in u] if archivio \
        else R.FONTI
    for u in fonti:
        try:
            return R._chiedi(u, m, p)
        except Exception:
            pass
    return None


def salute(utente, blocco=None):
    v = _c("eth_call", [{"to": POOL,
                         "data": "0xbf92857c" + utente[2:].zfill(64)},
                        hex(blocco) if blocco else "latest"])
    if isinstance(v, str) and len(v) >= 2 + 64 * 6:
        return int(v[2:][320:384], 16)
    return None


def main():
    testa = _c("eth_blockNumber", [], archivio=False)
    if not testa:
        print("   non so a che blocco siamo")
        return 1
    testa = int(testa, 16)
    corta = json.load(open(f"{D}/lista_corta.json"))
    vicine = [x for x in corta if x.get("salute", 9) < 1.01][:QUANTE]
    print(f"   blocco {testa}, guardo le {len(vicine)} posizioni piu' vicine")
    fuori = []
    for x in vicine:
        u = x["indirizzo"]
        ora = salute(u)
        prima = salute(u, testa - PASSO_INDIETRO)
        if ora is None or prima is None or ora >= UNO * 2:
            continue
        passo = (prima - ora) / float(PASSO_INDIETRO)
        sopra = ora - UNO
        if sopra <= 0:
            fuori.append({"utente": u, "debito": x.get("debito"),
                          "stato": "GIA' SOTTO", "blocchi": 0,
                          "passo": passo})
            continue
        if passo <= 0:
            continue                      # non scende: non e' un appuntamento
        blocchi = sopra / passo
        if blocchi <= ORIZZONTE_BLOCCHI:
            fuori.append({"utente": u, "debito": x.get("debito"),
                          "stato": "APPUNTAMENTO", "blocchi": blocchi,
                          "blocco_previsto": int(testa + blocchi),
                          "passo": passo,
                          "premio_stimato": (x.get("debito") or 0) * 0.03})
    fuori.sort(key=lambda y: y["blocchi"])
    print()
    print("   quando      blocco      premio      debito      scende di")
    for y in fuori:
        quando = ("GIA' SOTTO" if y["stato"] == "GIA' SOTTO"
                  else f"{y['blocchi']*12/60:.0f} min")
        print("   %-10s  %9s  $%8.0f  $%9.0f  %.3g/blocco" % (
            quando, y.get("blocco_previsto", "-"),
            y.get("premio_stimato", 0), y.get("debito") or 0, y["passo"]))
    app = [y for y in fuori if y["stato"] == "APPUNTAMENTO"]
    print(f"\n   {len(app)} appuntamenti entro 24 ore, premio stimato "
          f"${sum(y.get('premio_stimato', 0) for y in app):,.0f}")
    entro1h = [y for y in app if y["blocchi"] <= 300]
    print(f"   di cui {len(entro1h)} entro un'ora, premio "
          f"${sum(y.get('premio_stimato', 0) for y in entro1h):,.0f}")
    t = f"{D}/appuntamenti.json.tmp"
    json.dump({"quando": time.time(), "testa": testa, "righe": fuori},
              open(t, "w"), indent=1)
    os.replace(t, f"{D}/appuntamenti.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
