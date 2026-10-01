"""Le domande che facciamo a Grok — versionate, perche' devono migliorare ogni giorno.

L'IDEA CHE LE FA NASCERE (Nicolo, 27/09): «se io mi chiedessi ogni giorno come faccio a dire a Grok
di fare ancora meglio quello che sta facendo, allora anche Grok diventa sempre piu' bravo».
E' il punto piu' sottile di tutto il metodo: **non miglioriamo lo strumento, miglioriamo la domanda**.
La stessa intelligenza, dopo un mese di domande affinate, trova cose che il primo giorno non avrebbe
mai trovato — e non e' cambiato niente tranne cio' che le chiediamo.

COSA SOSTITUISCONO. La domanda precedente era ferma al 16 settembre e chiedeva *«quali memecoin
mostrano una crescita anomala di attenzione»* — cioe' «cosa sta per esplodere», che e' proprio la
domanda che Nicolo aveva escluso: e' rumore, e la risposta non e' verificabile. Passava per di piu'
dall'API a pagamento mentre l'abbonamento era gia' pagato.

LA REGOLA DI OGNI DOMANDA QUI DENTRO — una sola, e vale piu' del testo:
**la risposta deve nominare un file NOSTRO e la riga che cambierebbe.** Una ricerca che produce
"interessante, da approfondire" non si puo' ne' usare ne' giudicare, quindi non migliora mai. Una
che dice «in `agents/insieme.py` l'uscita non guarda la taglia» si puo' verificare in trenta
secondi — e se sbaglia, si vede.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERSIONE = "v2-2026-09-27"


def _titoli_gia_visti(quanti=25):
    """Cosa abbiamo gia' trovato, per non farcelo riportare uguale domani."""
    fuori = []
    for f in ("RICERCA_GITHUB.md", "RICERCA_GROK_24_09.md"):
        if not os.path.exists(f):
            continue
        for l in open(f, encoding="utf-8", errors="ignore"):
            if l.startswith(("## ", "### ")):
                fuori.append(l.strip("# \n"))
    return fuori[:quanti]


def su_x():
    return f"""Cerchi su X per un sistema che analizza memecoin appena nati su due chain EVM.

**NON cercare cosa sta per esplodere.** Le previsioni su quale token salira' sono rumore e non sono
verificabili. Cerca le persone che SPIEGANO COME FUNZIONANO LE COSE:

 · chi smonta in pubblico un meccanismo di truffa, con indirizzi o transazioni alla mano;
 · chi pubblica un'analisi con NUMERI e dice su quanti casi l'ha fatta;
 · chi mette il link al proprio codice;
 · chi spiega come si costruisce un sistema di agenti che non cade (architettura, flussi, guasti
   silenziosi, code di lavoro) — questa parte vale quanto quella di trading.

Cosa abbiamo GIA' trovato, non riportarcelo uguale:
{chr(10).join('  - ' + t for t in _titoli_gia_visti()) or '  (niente ancora)'}

**REGOLA SULLA RISPOSTA.** Ogni cosa che riporti deve dire:
 1. il link;
 2. che meccanismo descrive, in due righe;
 3. **quale file NOSTRO toccherebbe e cosa cambierebbe li' dentro**. Se non sai dire quale file
    nostro riguarda, non riportarla: vuol dire che non sappiamo ancora usarla.

Se in tutta la giornata non c'e' niente che superi questa asticella, **dillo**. «Oggi niente» e'
una risposta utile; un elenco riempito per non tornare a mani vuote non lo e'.

(versione della domanda: {VERSIONE})"""


def su_github():
    return f"""Cerchi su GitHub per lo stesso sistema. Due filoni, pari importanza:

 1. **come si misura** un mercato di memecoin senza ingannarsi: prezzi, profondita', uscite vere,
    trappole. Ci interessa il METODO, non la strategia;
 2. **come si costruiscono** sistemi di agenti automatici che non cadono: chi scrive, chi pubblica,
    come si accorgono di essere fermi, come si riprendono da soli.

Quello che abbiamo gia' guardato:
{chr(10).join('  - ' + t for t in _titoli_gia_visti()) or '  (niente ancora)'}

**REGOLA SULLA RISPOSTA**, identica: link, meccanismo in due righe, e **quale nostro file
cambierebbe**. Niente "interessante da approfondire": o si puo' verificare, o non serve.

Preferisci UNA cosa che possiamo provare oggi a dieci che possiamo solo leggere.

(versione della domanda: {VERSIONE})"""


def file_citati(risposta):
    """I file nostri nominati nella risposta, per scartare cio' che non e' verificabile."""
    return sorted({m for m in re.findall(r"[\w/]+\.(?:py|yml|sh|md)", risposta or "")
                   if os.path.exists(m)})


if __name__ == "__main__":
    quale = sys.argv[1] if len(sys.argv) > 1 else "x"
    print(su_x() if quale == "x" else su_github())
