"""L'AVVISO: quando una posizione si chiude, arriva una email.

Phantom non notifica in modo affidabile su Ethereum. Questa strada la
controlliamo noi: parte nell'istante in cui la transazione riesce, e
contiene tutto — quale posizione, quanto debito, quanto premio, il link
per verificare sulla chain.
"""
import smtplib, ssl, sys, os
from email.message import EmailMessage
MITTENTE="nicolostancato@gmail.com"
# LA PASSWORD NON STA NEL CODICE. Trovato il 2/11: era scritta in chiaro qui,
# e questo file e' su un repository PUBBLICO -- chiunque poteva scaricarlo
# (verificato: HTTP 200 senza credenziali). Nicolo' ha una regola esplicita su
# questo, e io l'ho violata pubblicando il file.
# Ora si legge da .chiavi/gmail, che il repo NON contiene (verificato: 404).
# NB: toglierla da qui NON basta -- resta nei commit vecchi. La password va
# REVOCATA su Google: e' l'unica cosa che chiude davvero il problema.
def _dal_file_delle_credenziali():
    """LA CARTELLA TEMPORANEA CI CANCELLA LE CHIAVI, QUINDI NON CI VIVONO.
    Il 7/11 il C-CHECK e' morto a meta' perche' .chiavi/gmail era sparito
    (la cartella di lavoro sta sotto /private/tmp e viene ripulita): e la
    morte era INVISIBILE, perche' qui sotto c'e' un SystemExit e il check lo
    avvolgeva in `except Exception` -- che non lo prende. Risultato: 1,6 ore
    in cui le ultime decine di verifiche non sono mai girate, con tutto il
    resto verde.
    La riparazione vera non e' rimettere il file: e' NON tenerlo qui. Nicolo'
    ha una sola fonte di verita' per le credenziali, e questa funzione la
    legge a RUNTIME -- cosi' nessuna pulizia del disco puo' zittire l'avviso.
    Non si stampa, non si copia, non si committa: si legge e si usa."""
    import os, re
    f = os.path.expanduser("~/Documents/b2b-finder-credentials.txt")
    if not os.path.exists(f):
        return None
    try:
        t = open(f, errors="ignore").read()
    except Exception:
        return None
    # una password app Google e' 16 lettere, spesso scritta in 4 gruppi da 4
    for riga in t.splitlines():
        if "gmail" not in riga.lower() and "app password" not in riga.lower():
            continue
        m = re.search(r"\b([a-z]{4}\s?[a-z]{4}\s?[a-z]{4}\s?[a-z]{4})\b",
                      riga)
        if m:
            return m.group(1).replace(" ", "")
    m = re.search(r"App Password[^\n]*?\b([a-z]{4}\s?[a-z]{4}\s?[a-z]{4}"
                  r"\s?[a-z]{4})\b", t, re.I)
    return m.group(1).replace(" ", "") if m else None


def _password():
    import os
    for p in (".chiavi/gmail", os.path.expanduser("~/.chiavi/gmail")):
        if os.path.exists(p):
            v=open(p).read().strip()
            if len(v) >= 16: return v
    v = _dal_file_delle_credenziali()
    if v:
        return v
    raise SystemExit("   password Gmail non trovata: ne' in .chiavi/gmail, "
                     "ne' in ~/.chiavi/gmail, ne' nel file delle credenziali. "
                     "Non mando niente invece di provare a indovinare")
PASS=_password()
def avvisa(premio_usd, debito_usd, posizione, transazione, garanzia="",
           prova=False, incerto=False):
    """`incerto=True` quando la cifra NON e' il premio della presa ma il
    saldo della cassa, perche' l'accredito non si e' potuto isolare.
    Aggiunto il 3/11 sera: nel ramo di ripiego di conferma_e_avvisa veniva
    passato il saldo intero come se fosse il premio, e l'oggetto avrebbe
    detto "PREMIO INCASSATO - 50.000 dollari" per una presa da 250 euro.
    Un numero gonfiato consegnato a Nicolo' e' la cosa che non si fa mai:
    ritirare un proprio risultato sbagliato vale piu' che consegnarne uno
    bello."""
    m=EmailMessage()
    m["Subject"] = (("[PROVA] " if prova else "") +
                    (f"PRESA FATTA — in cassa ${premio_usd:,.2f} "
                     f"(verifica l'importo)" if incerto
                     else f"PREMIO INCASSATO — ${premio_usd:,.2f}"))
    m["From"]=MITTENTE; m["To"]=MITTENTE
    m.set_content(f"{'PRESA FATTA, saldo in cassa' if incerto else 'PREMIO INCASSATO'}: ${premio_usd:,.2f}")
    avviso = ('<div style="background:#b45309;color:#fff;padding:14px 20px;'
              'border-radius:10px;margin-bottom:24px;font:600 15px system-ui">'
              'QUESTA È UNA PROVA — nessun denaro reale è stato incassato'
              '</div>') if prova else (
          ('<div style="background:#b45309;color:#fff;padding:14px 20px;'
           'border-radius:10px;margin-bottom:24px;font:600 15px system-ui">'
           'La cifra qui sotto è il SALDO della cassa, non il premio di '
           'questa presa: non è stato possibile isolare l\'accredito. '
           'Controlla su Etherscan.'
           '</div>') if incerto else '')
    m.add_alternative(f"""<!doctype html><html><body style="margin:0;padding:32px;
background:#0b0f14;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',system-ui,sans-serif">
<div style="max-width:560px;margin:0 auto;background:#121820;border-radius:18px;
padding:40px 36px;border:1px solid #1f2a36">
{avviso}
<div style="color:#5eead4;font-size:13px;letter-spacing:2.5px;font-weight:600">
LIQUIDAZIONE COMPLETATA</div>
<div style="color:#fff;font-size:56px;font-weight:800;margin:14px 0 4px;
letter-spacing:-1.5px">PREMIO<br>INCASSATO</div>
<div style="color:#4ade80;font-size:52px;font-weight:800;margin:28px 0 36px;
letter-spacing:-1px">${premio_usd:,.2f}</div>
<table style="width:100%;border-collapse:collapse;font-size:15px">
<tr><td style="color:#64748b;padding:11px 0;border-top:1px solid #1f2a36">Debito ripagato</td>
<td style="color:#e2e8f0;text-align:right;border-top:1px solid #1f2a36">${debito_usd:,.2f}</td></tr>
<tr><td style="color:#64748b;padding:11px 0;border-top:1px solid #1f2a36">Garanzia incassata</td>
<td style="color:#e2e8f0;text-align:right;border-top:1px solid #1f2a36">{garanzia or '—'}</td></tr>
<tr><td style="color:#64748b;padding:11px 0;border-top:1px solid #1f2a36">Posizione liquidata</td>
<td style="color:#e2e8f0;text-align:right;border-top:1px solid #1f2a36;
font-family:ui-monospace,monospace;font-size:13px">{posizione[:10]}…{posizione[-6:]}</td></tr>
<tr><td style="color:#64748b;padding:11px 0;border-top:1px solid #1f2a36">Accreditato su</td>
<td style="color:#e2e8f0;text-align:right;border-top:1px solid #1f2a36;
font-family:ui-monospace,monospace;font-size:13px">0x055e75…52eB66</td></tr>
</table>
<a href="https://etherscan.io/tx/{transazione}" style="display:block;margin-top:32px;
background:#4ade80;color:#06281a;text-decoration:none;padding:15px;border-radius:10px;
text-align:center;font-weight:700;font-size:15px">Verifica sulla blockchain</a>
<div style="color:#475569;font-size:12px;margin-top:24px;text-align:center">
Liquidatore · contratto 0xE30b58…D51212</div>
</div></body></html>""", subtype="html")
    ctx=ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ctx) as s:
        s.login(MITTENTE, PASS.replace(" ",""))
        s.send_message(m)
    return True
if __name__=="__main__":
    avvisa(premio_usd=5000.00, debito_usd=71428.57,
           posizione="0x1a557354c5b8d7df38ea914209e416dc7065b158",
           transazione="0xc3001bf7d5208a27572736ddf4ea231867b1c0608ecc2f42ad4edc7bfb6bc7fb",
           garanzia="33,05 weETH", prova=True)
    print("   email di prova inviata a nicolostancato@gmail.com")
