"""Il campanello: un'email quando la cassa supera un traguardo.

PERCHE' ESISTE (14/10, richiesta di Nicolo'). Dopo tre mesi di costruzione il momento in cui
il numero sale va SENTITO, non letto in fondo a un referto. Quindi: niente email di routine —
solo quando si supera una quota nuova. Un campanello che suona sempre non lo sente piu'
nessuno.

Ogni traguardo suona UNA VOLTA SOLA, anche se la cassa oscilla sopra e sotto: lo stato dice
qual e' il piu' alto gia' festeggiato. E suona anche in discesa, ma solo al pavimento, perche'
quella e' l'unica notizia brutta che richiede di alzarsi dalla sedia.

COSTO ZERO: SMTP di Gmail, gratis.
"""
import json
import os
import re
import smtplib
import ssl
import sys
from email.message import EmailMessage

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bot_curva as B                                          # noqa: E402
import cassa as C                                              # noqa: E402

A_CHI = os.environ.get("EMAIL_A", "nicolostancato@gmail.com")
def _posta():
    """Utenza e parola della posta, dal file delle credenziali. Mai scritte qui dentro."""
    da = os.environ.get("EMAIL_DA", "")
    par = os.environ.get("EMAIL_PAROLA", "")
    if da and par:
        return da, par
    # L'UTENZA BUONA E' QUELLA PERSONALE (14/10, provato). Nel file delle credenziali c'e'
    # anche preventivi.craftlabs@gmail.com, ma la sua parola non viene piu' accettata: Gmail
    # chiude la connessione durante l'accesso. Quella personale entra dalla porta 587.
    for f in ("~/Documents/b2b-finder-credentials.txt", "~/n8n builder/CLAUDE.md"):
        f = os.path.expanduser(f)
        if not os.path.exists(f):
            continue
        t = open(f, encoding="utf-8", errors="ignore").read()
        m = re.search(r"App Password:\s*`?([a-z]{4}\s[a-z]{4}\s[a-z]{4}\s[a-z]{4})`?", t)
        if m:
            return "nicolostancato@gmail.com", m.group(1).replace(" ", "")
    return "", ""


DA, PAROLA = _posta()
QUOTE = [70, 75, 80, 90, 100, 120, 150, 200, 300, 500]
STATO = "data/multichain/robinhood/squillo.json"


def vestito(quota, eur, partenza, variazione, prossima):
    """L'email bella. Tutto in linea, perche' i lettori di posta buttano via i fogli di stile.

    PERCHE' CURARLA (14/10, richiesta di Nicolo'). Dopo tre mesi di lavoro il momento in cui
    il numero supera una quota va visto, non letto. Un'email di testo la scorri; questa la
    guardi.
    """
    fatto = max(0.0, min(1.0, (eur - partenza) / max(prossima - partenza, 1e-9)))
    return f"""\
<div style="margin:0;padding:32px 12px;background:#0b0e14;font-family:-apple-system,
 BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;">
 <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr><td align="center">
   <table role="presentation" width="440" cellpadding="0" cellspacing="0" border="0"
    style="width:440px;max-width:100%;background:#141924;border:1px solid #232a3a;
    border-radius:18px;overflow:hidden;">
    <tr><td style="padding:28px 28px 8px;text-align:center;">
      <div style="font-size:11px;letter-spacing:.22em;color:#5b6b8c;text-transform:uppercase;">
        whale radar &nbsp;&middot;&nbsp; cassa</div>
    </td></tr>
    <tr><td style="padding:4px 28px 0;text-align:center;">
      <div style="font-size:64px;line-height:1.05;font-weight:800;color:#e8edf7;
        letter-spacing:-.03em;">&euro;{eur:,.2f}</div>
      <div style="margin-top:10px;display:inline-block;padding:7px 16px;border-radius:999px;
        background:{'#123524' if variazione >= 0 else '#36161b'};
        color:{'#4ade80' if variazione >= 0 else '#f87171'};font-size:15px;font-weight:700;">
        {variazione:+.1f}% dalla partenza</div>
    </td></tr>
    <tr><td style="padding:26px 28px 0;">
      <div style="background:#0b0e14;border-radius:14px;padding:18px 20px;">
        <div style="font-size:26px;font-weight:800;color:#e8edf7;text-align:center;">
          QUOTA {quota} SUPERATA</div>
        <div style="font-size:13px;color:#7c8aa8;text-align:center;margin-top:6px;">
          partiti da &euro;{partenza:,.2f}</div>
      </div>
    </td></tr>
    <tr><td style="padding:22px 28px 0;">
      <div style="font-size:11px;color:#5b6b8c;letter-spacing:.14em;text-transform:uppercase;
        margin-bottom:9px;">prossima quota &euro;{prossima}</div>
      <div style="height:9px;background:#0b0e14;border-radius:999px;overflow:hidden;">
        <div style="height:9px;width:{fatto*100:.0f}%;background:#4ade80;
          border-radius:999px;"></div>
      </div>
    </td></tr>
    <tr><td style="padding:24px 28px 30px;text-align:center;">
      <div style="font-size:12px;color:#5b6b8c;line-height:1.6;">
        il bot compra e vende da solo dentro la curva<br>
        si ferma da solo se la cassa scende sotto la soglia</div>
    </td></tr>
   </table>
  </td></tr>
 </table>
</div>"""


def manda(oggetto, corpo, html=None):
    if not DA or not PAROLA:
        print(f"SQUILLO | manca l'accesso alla posta: non mando. [{oggetto}]")
        return False
    m = EmailMessage()
    m["Subject"] = oggetto
    m["From"] = DA
    m["To"] = A_CHI
    m["X-Priority"] = "1"
    m["Importance"] = "high"
    m.set_content(corpo)
    if html:
        m.add_alternative(html, subtype="html")
    # porta 587 con STARTTLS: la 465 viene chiusa durante l'accesso, provato il 14/10
    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as s:
        s.ehlo()
        s.starttls(context=ssl.create_default_context())
        s.ehlo()
        s.login(DA, PAROLA)
        s.send_message(m)
    print(f"SQUILLO | mandata: {oggetto}")
    return True


def main():
    prova = "--prova" in sys.argv
    c = C.saldo()
    if c is None:
        print("SQUILLO | non leggo la cassa")
        return 1
    eur = c * C.CAMBIO
    st = json.load(open(STATO)) if os.path.exists(STATO) else {"massima": 0, "pavimento": False}
    if prova:
        manda("** PROVA — quota 70 **",
              f"Questa e' una prova del campanello.\n\n"
              f"Cassa adesso: {eur:.2f} EUR ({c:.6f} nativi)\n"
              f"Partenza: {C.PARTENZA * C.CAMBIO:.2f} EUR\n"
              f"Variazione: {(c / C.PARTENZA - 1) * 100:+.1f}%\n\n"
              f"Quando la cassa superera' davvero 70, 75, 80 EUR ti arrivera' un'email come "
              f"questa, una sola volta per quota.")
        return 0
    nuove = [q for q in QUOTE if eur >= q > st["massima"]]
    if nuove:
        q = max(nuove)
        st["massima"] = q
        prossima = next((x for x in QUOTE if x > q), q * 2)
        var = (c / C.PARTENZA - 1) * 100
        manda(f"\U0001F680 QUOTA {q} SUPERATA \u2014 \u20ac{eur:,.2f}",
              f"La cassa ha superato {q} EUR.\n\n"
              f"Adesso: {eur:.2f} EUR ({c:.6f} nativi)\n"
              f"Partenza: {C.PARTENZA * C.CAMBIO:.2f} EUR\n"
              f"Variazione dalla partenza: {var:+.1f}%\n",
              html=vestito(q, eur, C.PARTENZA * C.CAMBIO, var, prossima))
    if c < B.PAVIMENTO and not st.get("pavimento"):
        st["pavimento"] = True
        manda("** PAVIMENTO RAGGIUNTO: il bot ha smesso di comprare **",
              f"La cassa e' scesa a {eur:.2f} EUR, sotto la soglia di "
              f"{B.PAVIMENTO * C.CAMBIO:.0f} EUR.\n"
              f"Il bot non apre piu' posizioni. Serve una decisione.\n")
    elif c >= B.PAVIMENTO:
        st["pavimento"] = False
    os.makedirs(os.path.dirname(STATO), exist_ok=True)
    tmp = STATO + ".tmp"
    with open(tmp, "w") as f:
        json.dump(st, f)
    os.replace(tmp, STATO)
    return 0


if __name__ == "__main__":
    sys.exit(main())
