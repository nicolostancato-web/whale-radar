# -*- coding: utf-8 -*-
"""Genera la METRICA: una pagina da telefono con tutte le posizioni sorvegliate.

Si rigenera da metrica.json. Quando il laghetto cresce, la pagina cresce:
non c'e' nulla scritto a mano qui dentro, tutti i numeri vengono dalla catena.
"""
import json, time, html

D = json.load(open("data/liquidazioni/metrica.json"))
POS = D["posizioni"]
deb = json.load(open("data/liquidazioni/debitori.json"))
corta = json.load(open("data/liquidazioni/lista_corta.json"))
fatte = json.load(open("data/liquidazioni/finestre_fatte_v2.json"))
# cosa ha pagato il mercato DAVVERO, letto dai log delle liquidazioni vere.
# Vale piu' di qualunque mio modello: non e' una probabilita', e' un incasso
# che e' avvenuto. Se il file manca, la sezione non si stampa (niente stime).
try: PAG_ = json.load(open("data/liquidazioni/avrebbe_pagato.json"))
except Exception: PAG_ = None
# l'osservazione DIRETTA: cosa ha prodotto il NOSTRO laghetto, senza modelli
try: PROD = json.load(open("data/liquidazioni/laghetto_ha_prodotto.json"))
except Exception: PROD = None
# ogni quanto arriva la grossa, su 88 giorni invece di 9
try: FREQ = json.load(open("data/liquidazioni/ogni_quanto.json"))
except Exception: FREQ = None
# la gara: e' chiusa o ci si puo' entrare?
try: GARA = json.load(open("data/liquidazioni/la_gara.json"))
except Exception: GARA = None
# ACCORGERSI: la barra che Nicolo' vuole vedere appena apre lo schermo
try: ACC = json.load(open("data/liquidazioni/accorgersi.json"))
except Exception: ACC = None
# chi potrebbe essere la prima bolla: le candidate pronte, piu' vicine
try: BOLLA = json.load(open("data/liquidazioni/prima_bolla.json"))
except Exception: BOLLA = None
N_DEB = len(deb); N_CORTA = len(corta); N_FIN = len(fatte)

tot = sum(p["premio"] for p in POS)
atteso = sum(p["premio"] * p["prob30"] / 100 for p in POS)
diverse = [p for p in POS if p["tipo"] == "coppia diversa"]
uguali  = [p for p in POS if p["tipo"] == "coppia uguale"]
for g in (diverse, uguali):
    g.sort(key=lambda p: -(p["premio"] * p["prob30"]))

def eur(n):
    return f"{n:,.0f}".replace(",", ".")

def fascia(p):
    if p >= 40: return "alta"
    if p >= 10: return "media"
    if p >= 2:  return "bassa"
    return "remota"

ETICHETTA = {"alta": "alta", "media": "media", "bassa": "bassa", "remota": "remota"}

def carta(p):
    f = fascia(p["prob30"])
    ev = p["premio"] * p["prob30"] / 100
    largh = max(1.5, min(100, p["prob30"]))
    tag = ('<span class="cap">tetto</span>' if p["tagliato"] else "")
    deb_lbl = p["debito"] if p["debito"] != "?" else "dollaro"
    return f"""
      <article class="carta f-{f}">
        <header>
          <code class="id">{html.escape(p['pos'][:10])}</code>
          <div class="coppia"><span class="gar">{html.escape(p['garanzia'])}</span><span class="vs">contro</span><span class="dbt">{html.escape(deb_lbl)}</span></div>
        </header>
        <div class="prob">
          <div class="pnum"><b>{p['prob30']:.1f}</b><span>%</span></div>
          <div class="plab">probabilit&agrave; di cadere<br><span class="sub">entro 30 giorni &middot; {ETICHETTA[f]}</span></div>
        </div>
        <div class="barra"><i style="width:{largh:.1f}%"></i></div>
        <dl class="dati">
          <div><dt>premio se cade</dt><dd class="big">&euro;{eur(p['premio'])} {tag}</dd></div>
          <div><dt>valore atteso</dt><dd>&euro;{eur(ev)}</dd></div>
          <div><dt>calo necessario</dt><dd>{p['calo']:.2f}%</dd></div>
          <div><dt>salute oggi</dt><dd>{p['salute']:.4f}</dd></div>
        </dl>
        <p class="nota">{html.escape(p['nota'])}</p>
      </article>"""


def sez_bolla():
    if not BOLLA: return ""
    def riga(r, forte=False):
        tag=" <span class='cap'>tetto</span>" if r.get("tagliato") else ""
        cl=" class='ris'" if forte else ""
        return (f"<tr{cl}><td class='calo'>{r['calo']:.2f}%</td>"
                f"<td class='cop'>{html.escape(r['gar'])}/{html.escape(r['deb'])}</td>"
                f"<td class='pre'>&euro;{eur(r['premio'])}{tag}</td></tr>")
    dv="".join(riga(r, i==0) for i,r in enumerate(BOLLA["diverse"]))
    bb="".join(riga(r) for r in BOLLA["bombe"])
    return f"""
    <section class="gruppo bolla">
      <h2>Chi potrebbe essere la prima bolla</h2>
      <p class="spiega"><b>{BOLLA['quante_pronte']}</b> posizioni pronte a
      sparare su {BOLLA['quante_armate']} armate. Entrano solo quelle con la
      vendita gi&agrave; preparata: su una senza vendita il pacchetto non si
      compone in tempo, quindi non &egrave; una candidata.</p>
      <h3 class="sub2">Le pi&ugrave; vicine, coppia diversa</h3>
      <p class="minuta">Ordinate per quanto manca alla caduta, non per premio:
      la prima bolla la fa quella che cade, non quella che vale pi&ugrave;.</p>
      <table class="bt"><thead><tr><th>calo</th><th>coppia</th><th>premio</th>
      </tr></thead><tbody>{dv}</tbody></table>
      <h3 class="sub2">Le bombe a coppia uguale</h3>
      <p class="minuta">Premio enorme, caduta rara: garanzia e debito si
      muovono insieme, quindi un calo di mercato non le tocca. Si sorvegliano
      per lo sganciamento.</p>
      <table class="bt"><tbody>{bb}</tbody></table>
    </section>"""
def sez_accorgersi():
    if not ACC: return ""
    SIMB={"fatto":"✓","in ascolto":"◴","da fare":"○"}
    righe="".join(
      f"<li class='st-{p['stato'].replace(' ','-')}'>"
      f"<span class='seg'>{SIMB.get(p['stato'],'·')}</span>"
      f"<span class='pp'>{html.escape(p['p'])}"
      f"<em>{html.escape(p['nota'])}</em></span></li>"
      for p in ACC["passi"])
    return f"""
    <section class="gruppo acc">
      <div class="accTesta">
        <h2>{html.escape(ACC['titolo'])}</h2>
        <div class="accNum">{ACC['percento']}<span>%</span></div>
      </div>
      <div class="accBarra"><i style="width:{ACC['percento']}%"></i></div>
      <p class="spiega">Il 100% &egrave; {html.escape(ACC['cosa_e_100'])}.</p>
      <ul class="passi">{righe}</ul>
    </section>"""
def sez_gara():
    if not GARA: return ""
    return f"""
    <section class="gruppo vero">
      <h2>La gara &egrave; aperta</h2>
      <p class="spiega">L&rsquo;ultima cosa che non sapevamo: se pochi
      prendessero tutto, non avremmo speranza. Misurato sulle
      {GARA['grosse_oltre_10k']} liquidazioni sopra &euro;10.000 degli
      {GARA['giorni']} giorni.</p>
      <table class="vt"><tbody>
      <tr><th>contratti liquidatori</th><td>{GARA['contratti']}</td><td class="gg"></td></tr>
      <tr><th>persone distinte dietro</th><td>{GARA['mittenti']}</td>
          <td class="gg">pi&ugrave; dei contratti</td></tr>
      <tr><th>quota del primo</th>
          <td>{GARA['primo_per_mittente_pct']}&ndash;{GARA['primo_fondendo_contratti_pct']}%</td>
          <td class="gg">non un monopolio</td></tr>
      <tr class="ris"><th>ne hanno presa UNA SOLA</th>
          <td>{GARA['mittenti_con_una_sola']} su {GARA['su']}</td>
          <td class="gg">{GARA['pct']}% del denaro</td></tr>
      </tbody></table>
      <p class="avviso prod"><b>Met&agrave; del denaro grosso va a chi compare
      una volta sola in tre mesi.</b> Non &egrave; un oligopolio chiuso: un
      nuovo arrivato vince, a volte. &Egrave; la ragione per cui questa fase
      ha senso.</p>
      <p class="avviso">Limite dichiarato: persone diverse che usano lo stesso
      contratto potrebbero essere una sola entit&agrave; con pi&ugrave;
      portafogli. Non lo si pu&ograve; escludere a costo zero, da cui
      l&rsquo;intervallo invece di un numero secco.</p>
    </section>"""
def sez_freq():
    if not FREQ: return ""
    righe=""
    for soglia,n,gg,arm in FREQ["frequenza"]:
        forte=' class="ris"' if soglia>=100000 else ''
        righe+=(f"<tr{forte}><th>oltre &euro;{eur(soglia)}</th>"
                f"<td>{n}</td><td class='gg'>ogni {gg:.1f} gg</td></tr>")
    return f"""
    <section class="gruppo vero">
      <h2>Ogni quanto arriva la grossa</h2>
      <p class="spiega">{FREQ['liquidazioni']} liquidazioni vere lette su
      {FREQ['giorni']} giorni contigui, senza buchi. Non una stima: un conteggio.</p>
      <table class="vt"><tbody>{righe}</tbody></table>
      <p class="avviso prod"><b>Tutte e {FREQ['frequenza'][-1][3]} quelle sopra
      &euro;100.000 erano su garanzie che oggi sorvegliamo.</b> La pi&ugrave;
      grossa degli {FREQ['giorni']} giorni ha pagato
      &euro;{eur(FREQ['piu_grossa'])}.</p>
      <p class="avviso">Met&agrave; delle liquidazioni sono <b>polvere</b>:
      {FREQ['polveri_sotto_5']} su {FREQ['liquidazioni']} valgono meno di
      &euro;5 e non ci interessano. Quelle che contano sono
      <b>{FREQ['sopra_minimo_5']}</b>, cio&egrave;
      <b>{FREQ['sopra_minimo_al_giorno']} al giorno</b>, con premio mediano
      &euro;{eur(FREQ['mediana_sopra_minimo'])}.</p>
      <p class="avviso">Il mercato paga &euro;{eur(FREQ['al_giorno'])} al giorno
      di premio lordo, di cui il <b>{FREQ['su_armate_pct']}%</b> su garanzie
      armate: &euro;{eur(FREQ['su_armate_al_giorno'])} al giorno.</p>
    </section>"""
def sez_vero():
    if not PAG_: return ""
    g = PAG_["giorni"]
    return f"""
    <section class="gruppo vero">
      <h2>Cosa ha pagato il mercato</h2>
      <p class="spiega">Non un modello: {PAG_['n']} liquidazioni vere lette dai log
      degli ultimi {g:.0f} giorni. Ogni evento porta scritto dentro il debito che
      e&rsquo; stato chiuso; il premio e&rsquo; il 7,00% su quello.</p>
      <table class="vt">
        <tbody>
        <tr><th>tutto il mercato</th>
            <td>&euro;{eur(PAG_['tot'])}</td><td class="gg">&euro;{eur(PAG_['tot']/g)}/gg</td></tr>
        <tr><th>su garanzie che so vendere</th>
            <td>&euro;{eur(PAG_['vendibile'])}</td><td class="gg">&euro;{eur(PAG_['vendibile']/g)}/gg</td></tr>
        <tr><th>su debitori gi&agrave; nel laghetto</th>
            <td>&euro;{eur(PAG_['nostri'])}</td><td class="gg">&euro;{eur(PAG_['nostri']/g)}/gg</td></tr>
        <tr class="ris"><th>aggredibile oggi</th>
            <td>&euro;{eur(PAG_['aggredibile'])}</td><td class="gg">&euro;{eur(PAG_['aggredibile']/g)}/gg</td></tr>
        </tbody>
      </table>
      <p class="avviso"><b>Premio mediano per liquidazione: &euro;{eur(PAG_['mediana'])}.</b>
      Le tre pi&ugrave; grosse di questi {g:.0f} giorni valevano &euro;39.862, &euro;17.122 e
      &euro;12.319 &mdash; tutte e tre su garanzie che non riesco a vendere. Il premio
      vendibile e&rsquo; il 10% del totale: <b>cade il grosso dove non si incassa</b>.
      Le cifre enormi nelle carte qui sotto sono di posizioni che non cadono.</p>
      {("<p class='avviso prod'><b>E il nostro laghetto, nello stesso periodo: "
         "&euro;" + eur(PROD['premio_somma']) + ".</b> "
         + str(PROD['cadute']) + " delle " + str(PROD['su_quante']) +
         " posizioni sorvegliate sono cadute fra il blocco di 9 giorni fa e "
         "oggi. Premio mediano &euro;" + eur(PROD['premio_mediana']) +
         ", il pi&ugrave; grosso &euro;" + eur(PROD['premio_max']) + ". "
         "Questa non &egrave; una probabilit&agrave;: &egrave; un prima/dopo. "
         "E la mediana coincide con quella di tutto il mercato (&euro;" +
         eur(PAG_['mediana']) + "), misurata per un'altra strada.</p>")
        if PROD else ""}
      <p class="avviso"><b>Questo e&rsquo; il premio del mercato, non il nostro incasso.</b>
      Ogni occasione la prende qualcuno, e su 484 giri armati abbiamo preso zero.
      Le occasioni esistono; vincere la gara e&rsquo; un&rsquo;altra cosa e si sapr&agrave;
      solo alla prima presa.</p>
    </section>"""

def sezione(titolo, sotto, gruppo):
    if not gruppo: return ""
    t = sum(p["premio"] for p in gruppo)
    e = sum(p["premio"] * p["prob30"] / 100 for p in gruppo)
    return f"""
    <section class="gruppo">
      <h2>{titolo}</h2>
      <p class="spiega">{sotto}</p>
      <div class="riga-tot">
        <span><em>{len(gruppo)}</em> posizioni</span>
        <span>premio <em>&euro;{eur(t)}</em></span>
        <span>atteso <em>&euro;{eur(e)}</em></span>
      </div>
      {''.join(carta(p) for p in gruppo)}
    </section>"""

PAG = f"""<title>Il Laghetto</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@600;800&family=IBM+Plex+Mono:wght@400;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
:root {{
  --ground:#F0F2F6; --surface:#FFFFFF; --sunk:#E6E9F0;
  --ink:#171C27; --mid:#4E5668; --faint:#8C94A6; --hair:#D6DAE4;
  --brass:#8E6722; --brass-soft:#F2EAD8;
  --alta:#B2443A; --media:#A9761F; --bassa:#4A6E8C; --remota:#7A8296;
  --disp:'Archivo',system-ui,sans-serif;
  --body:'IBM Plex Sans',system-ui,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,monospace;
}}
@media (prefers-color-scheme:dark) {{
  :root:not([data-theme="light"]) {{
    --ground:#12161F; --surface:#1B2130; --sunk:#161B27;
    --ink:#E3E7F0; --mid:#9AA3B6; --faint:#6B7488; --hair:#2A3243;
    --brass:#C79A4A; --brass-soft:#2A2314;
    --alta:#D86154; --media:#D29B3C; --bassa:#6E9CC2; --remota:#79839A;
  }}
}}
:root[data-theme="dark"] {{
  --ground:#12161F; --surface:#1B2130; --sunk:#161B27;
  --ink:#E3E7F0; --mid:#9AA3B6; --faint:#6B7488; --hair:#2A3243;
  --brass:#C79A4A; --brass-soft:#2A2314;
  --alta:#D86154; --media:#D29B3C; --bassa:#6E9CC2; --remota:#79839A;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:var(--body); font-size:16px; line-height:1.55;
  -webkit-text-size-adjust:100%;
}}
.wrap {{ max-width:600px; margin:0 auto; padding:28px 18px 72px; }}

/* ---- testa ---- */
.testa {{ display:flex; flex-direction:column; gap:6px; margin-bottom:26px; }}
.occhio {{
  font-family:var(--mono); font-size:11px; letter-spacing:.16em;
  text-transform:uppercase; color:var(--brass); font-weight:600;
}}
h1 {{
  font-family:var(--disp); font-weight:800; font-size:clamp(30px,9vw,42px);
  line-height:1.03; margin:0; letter-spacing:-.02em; text-wrap:balance;
}}
.quando {{ font-family:var(--mono); font-size:12px; color:var(--faint); }}

/* ---- due numeri grossi ---- */
.somme {{ display:grid; grid-template-columns:1fr 1fr; gap:10px; margin:22px 0 10px; }}
.somma {{
  background:var(--surface); border:1px solid var(--hair);
  border-radius:3px; padding:14px 14px 12px;
}}
.somma dt {{
  font-family:var(--mono); font-size:10.5px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--faint); margin-bottom:5px;
}}
.somma dd {{
  margin:0; font-family:var(--disp); font-weight:800;
  font-size:clamp(22px,6.4vw,28px); letter-spacing:-.015em;
  font-variant-numeric:tabular-nums;
}}
.somma.ev dd {{ color:var(--brass); }}
.somma small {{ display:block; font-family:var(--body); font-weight:400;
  font-size:11.5px; color:var(--faint); letter-spacing:0; margin-top:3px; }}

/* ---- imbuto del laghetto ---- */
.imbuto {{
  background:var(--sunk); border:1px solid var(--hair); border-radius:3px;
  padding:13px 14px; margin:12px 0 30px;
}}
.imbuto h3 {{
  margin:0 0 9px; font-family:var(--mono); font-size:10.5px;
  letter-spacing:.11em; text-transform:uppercase; color:var(--faint); font-weight:600;
}}
.scala {{ display:flex; align-items:baseline; gap:7px; flex-wrap:wrap;
  font-family:var(--mono); font-size:12.5px; color:var(--mid); }}
.scala b {{ color:var(--ink); font-size:16px; font-weight:600;
  font-variant-numeric:tabular-nums; }}
.scala i {{ color:var(--brass); font-style:normal; }}

/* ---- prima bolla ---- */
.bolla {{ background:var(--surface); border:1px solid var(--hair);
  border-left:3px solid var(--alta); border-radius:3px; padding:16px 15px 14px; }}
.sub2 {{ font-family:var(--mono); font-size:10.5px; letter-spacing:.11em;
  text-transform:uppercase; color:var(--faint); font-weight:600;
  margin:16px 0 3px; }}
.minuta {{ margin:0 0 9px; font-size:12px; color:var(--faint); line-height:1.45; }}
table.bt {{ width:100%; border-collapse:collapse; }}
table.bt th {{ text-align:left; font-family:var(--mono); font-size:10px;
  letter-spacing:.1em; text-transform:uppercase; color:var(--faint);
  font-weight:600; padding:0 0 5px; }}
table.bt th:last-child {{ text-align:right; }}
table.bt td {{ padding:6px 0; border-top:1px solid var(--hair);
  font-family:var(--mono); font-size:13.5px; font-variant-numeric:tabular-nums; }}
td.calo {{ width:4.5em; font-weight:600; }}
td.cop {{ color:var(--mid); font-size:12.5px; }}
td.pre {{ text-align:right; font-weight:600; white-space:nowrap; }}
table.bt tr.ris td {{ color:var(--alta); }}

/* ---- accorgersi ---- */
.acc {{ background:var(--surface); border:1px solid var(--hair);
  border-top:3px solid var(--brass); border-radius:3px; padding:16px 15px 14px; }}
.accTesta {{ display:flex; align-items:baseline; justify-content:space-between;
  gap:12px; }}
.acc h2 {{ margin:0; }}
.accNum {{ font-family:var(--disp); font-weight:800; font-size:40px;
  line-height:1; letter-spacing:-.03em; color:var(--brass);
  font-variant-numeric:tabular-nums; }}
.accNum span {{ font-size:19px; font-weight:600; color:var(--faint); }}
.accBarra {{ height:7px; background:var(--sunk); border-radius:4px;
  margin:12px 0 12px; overflow:hidden; }}
.accBarra i {{ display:block; height:100%; background:var(--brass); }}
ul.passi {{ list-style:none; margin:0; padding:0; display:flex;
  flex-direction:column; gap:9px; }}
ul.passi li {{ display:flex; gap:9px; align-items:flex-start;
  font-size:13.5px; line-height:1.4; }}
.seg {{ font-family:var(--mono); font-size:13px; width:1.1em;
  flex:0 0 auto; text-align:center; }}
.pp em {{ display:block; font-style:normal; font-size:12px;
  color:var(--faint); margin-top:2px; }}
li.st-fatto .seg {{ color:var(--vivo,#3E9B6B); }}
li.st-fatto .pp {{ color:var(--mid); }}
li.st-in-ascolto .seg {{ color:var(--brass); }}
li.st-in-ascolto .pp {{ color:var(--ink); font-weight:600; }}
li.st-da-fare .seg {{ color:var(--faint); }}
li.st-da-fare .pp {{ color:var(--faint); }}

/* ---- il misurato ---- */
.vero {{ background:var(--surface); border:1px solid var(--hair);
  border-top:3px solid var(--brass); border-radius:3px; padding:16px 15px 14px; }}
.vero h2 {{ margin-bottom:4px; }}
table.vt {{ width:100%; border-collapse:collapse; margin:4px 0 12px; }}
table.vt th {{ text-align:left; font-weight:400; font-size:13px; color:var(--mid);
  padding:7px 0; border-bottom:1px solid var(--hair); }}
table.vt td {{ text-align:right; font-family:var(--mono); font-size:14px;
  font-weight:600; font-variant-numeric:tabular-nums; padding:7px 0 7px 10px;
  border-bottom:1px solid var(--hair); white-space:nowrap; }}
table.vt td.gg {{ font-weight:400; font-size:11.5px; color:var(--faint); }}
table.vt tr.ris th {{ color:var(--ink); font-weight:600; }}
table.vt tr.ris td {{ color:var(--brass); font-size:16px; }}
table.vt tr:last-child th, table.vt tr:last-child td {{ border-bottom:0; }}
.avviso {{ margin:0 0 9px; font-size:12.5px; line-height:1.5; color:var(--mid); }}
.avviso:last-child {{ margin-bottom:0; }}
.avviso b {{ color:var(--ink); font-weight:600; }}
.avviso.prod {{ border-left:2px solid var(--brass); padding-left:10px; }}

/* ---- sezioni ---- */
.gruppo {{ margin:0 0 34px; }}
.gruppo h2 {{
  font-family:var(--disp); font-weight:600; font-size:19px;
  margin:0 0 4px; letter-spacing:-.01em;
}}
.spiega {{ margin:0 0 12px; font-size:14px; color:var(--mid); }}
.riga-tot {{
  display:flex; gap:14px; flex-wrap:wrap; padding:9px 0 13px;
  border-top:1px solid var(--hair); border-bottom:1px solid var(--hair);
  margin-bottom:14px; font-family:var(--mono); font-size:11.5px; color:var(--faint);
}}
.riga-tot em {{ font-style:normal; color:var(--ink); font-weight:600;
  font-variant-numeric:tabular-nums; }}

/* ---- carta posizione ---- */
.carta {{
  background:var(--surface); border:1px solid var(--hair);
  border-left:3px solid var(--remota); border-radius:3px;
  padding:14px 15px 13px; margin-bottom:10px;
}}
.f-alta  {{ border-left-color:var(--alta); }}
.f-media {{ border-left-color:var(--media); }}
.f-bassa {{ border-left-color:var(--bassa); }}
.carta header {{ display:flex; justify-content:space-between;
  align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:11px; }}
.id {{ font-family:var(--mono); font-size:12px; color:var(--faint); }}
.coppia {{ display:flex; align-items:center; gap:6px;
  font-family:var(--mono); font-size:12px; }}
.gar,.dbt {{ padding:2px 6px; border-radius:2px; background:var(--sunk);
  border:1px solid var(--hair); color:var(--ink); font-weight:600; }}
.vs {{ color:var(--faint); font-size:10.5px; }}

.prob {{ display:flex; align-items:center; gap:12px; }}
.pnum {{ display:flex; align-items:baseline; gap:1px; }}
.pnum b {{ font-family:var(--disp); font-weight:800;
  font-size:38px; line-height:1; letter-spacing:-.03em;
  font-variant-numeric:tabular-nums; }}
.pnum span {{ font-family:var(--disp); font-weight:600; font-size:17px;
  color:var(--faint); }}
.plab {{ font-size:13px; line-height:1.3; color:var(--mid); }}
.plab .sub {{ font-family:var(--mono); font-size:10.5px; color:var(--faint);
  letter-spacing:.03em; }}
.f-alta  .pnum b {{ color:var(--alta); }}
.f-media .pnum b {{ color:var(--media); }}
.f-bassa .pnum b {{ color:var(--bassa); }}
.f-remota .pnum b {{ color:var(--remota); }}

.barra {{ height:4px; background:var(--sunk); border-radius:2px;
  margin:11px 0 13px; overflow:hidden; }}
.barra i {{ display:block; height:100%; background:var(--remota); }}
.f-alta  .barra i {{ background:var(--alta); }}
.f-media .barra i {{ background:var(--media); }}
.f-bassa .barra i {{ background:var(--bassa); }}

.dati {{ display:grid; grid-template-columns:1fr 1fr; gap:10px 14px; margin:0; }}
.dati dt {{ font-family:var(--mono); font-size:10px; letter-spacing:.1em;
  text-transform:uppercase; color:var(--faint); }}
.dati dd {{ margin:1px 0 0; font-family:var(--mono); font-size:14px;
  font-weight:600; font-variant-numeric:tabular-nums; }}
.dati dd.big {{ font-size:16px; }}
.cap {{ font-family:var(--body); font-size:9.5px; font-weight:500;
  letter-spacing:.06em; text-transform:uppercase; color:var(--brass);
  background:var(--brass-soft); border-radius:2px; padding:1px 4px;
  vertical-align:2px; }}
.nota {{ margin:12px 0 0; padding-top:10px; border-top:1px solid var(--hair);
  font-size:12.5px; color:var(--mid); }}

/* ---- piede ---- */
.piede {{ border-top:1px solid var(--hair); padding-top:16px;
  font-size:12.5px; color:var(--faint); }}
.piede p {{ margin:0 0 8px; }}
.piede b {{ color:var(--mid); font-weight:600; }}
@media (max-width:380px) {{
  .somme {{ grid-template-columns:1fr; }}
  .dati {{ grid-template-columns:1fr; }}
}}
</style>

<div class="wrap">
  <div class="testa">
    <div class="occhio">liquidazioni aave &middot; prima bolla</div>
    <h1>Il Laghetto</h1>
    <div class="quando">letto dalla catena il {D['quando']}</div>
  </div>

  <dl class="somme">
    <div class="somma"><dt>premio se cadessero tutte</dt>
      <dd>&euro;{eur(tot)}<small>{len(POS)} posizioni sorvegliate</small></dd></div>
    <div class="somma ev"><dt>valore atteso 30 giorni</dt>
      <dd>&euro;{eur(atteso)}<small>premio &times; probabilit&agrave;, sommato</small></dd></div>
  </dl>

  <div class="imbuto">
    <h3>da dove arrivano</h3>
    <div class="scala">
      <b>{N_FIN}</b> finestre lette <i>&rarr;</i>
      <b>{eur(N_DEB)}</b> debitori <i>&rarr;</i>
      <b>{N_CORTA}</b> a rischio <i>&rarr;</i>
      <b>{len(POS)}</b> aggredibili
    </div>
  </div>

  {sez_bolla()}

  {sez_accorgersi()}

  {sez_gara()}

  {sez_freq()}

  {sez_vero()}

  {sezione("Possono cadere da sole",
    "Garanzia e debito in valute diverse: basta che il prezzo scenda. "
    "La probabilit&agrave; viene dalla volatilit&agrave; vera dell&rsquo;asset degli ultimi 180 giorni.",
    diverse)}

  {sezione("Cadono solo per uno sganciamento",
    "Garanzia e debito nella stessa valuta: il mercato non le tocca. "
    "Si muovono solo per la deriva fra rendimento della garanzia e costo del debito &mdash; "
    "e dove la deriva &egrave; positiva la salute migliora, quindi non cadranno mai da sole. "
    "Sono i cavalli grossi: premio enorme, probabilit&agrave; piccola.",
    uguali)}

  <div class="piede">
    <p><b>Come si legge la probabilit&agrave;.</b> Per le coppie diverse &egrave; la
    probabilit&agrave; che il prezzo tocchi il calo necessario entro 30 giorni, calcolata
    sulla volatilit&agrave; giornaliera misurata: {', '.join(f'{k} {v}%' for k,v in D['volatilita'].items())}.
    Per le coppie uguali &egrave; il tempo che serve alla deriva per mangiare il margine,
    pi&ugrave; mezzo punto per il rischio di sganciamento.</p>
    <p><b>Premio.</b> Il 7,00% letto dal protocollo sulla met&agrave; del debito che si pu&ograve;
    chiudere. Dove c&rsquo;&egrave; scritto <span class="cap">tetto</span>, la taglia &egrave;
    limitata da quanto quell&rsquo;asset si riesce davvero a vendere, non dalla posizione.</p>
    <p><b>Valore atteso.</b> &Egrave; il numero che conta per decidere dove guardare, non il
    premio: un cavallo da &euro;130.000 allo 0,5% vale meno di uno da &euro;300 all&rsquo;80%.
    Le carte sono ordinate per questo.</p>
    <p>Nessun numero di questa pagina &egrave; scritto a mano: si rigenera dalla catena.
    Quando il laghetto si allarga, si allarga anche la metrica.</p>
  </div>
</div>
"""
open("data/liquidazioni/metrica.html","w").write(PAG)
print(f"   metrica scritta: {len(POS)} posizioni, "
      f"premio EUR {eur(tot)}, atteso EUR {eur(atteso)}")
print(f"   imbuto: {N_FIN} finestre -> {N_DEB} debitori -> {N_CORTA} a rischio -> {len(POS)}")
