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

VERSIONE = "v3-2026-10-05"


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
    """LA DOMANDA E' CAMBIATA (5/10, direttiva di Nicolo'): dal «cosa sta per salire» al
    «come si procurano i gettoni senza comprarli dove guardiamo noi».

    PERCHE'. Misurato il 5/10: il 45-48% delle posizioni e' comprata e mai venduta, e un'altra
    grossa fetta e' «solo uscite» — gettoni VENDUTI che non abbiamo mai visto comprare. Meta' di
    quelli non e' un buco nostro: quegli acquisti **non sono mai avvenuti su un mercato** che
    guardiamo. Quei gettoni sono stati ricevuti.
    Nicolo': «occhio che se non troviamo le X, quel 50% nascosto magari e' un altro metodo per
    fare i soldi — magari quelle cripto si prendono prima, in un altro posto. E' proprio il
    concetto di entrare prima».
    E' una domanda da ricerca esterna, non dai nostri dati: noi vediamo solo cio' che passa dai
    mercati che indicizziamo. Grok ha la ricerca su X e sul web, e costa zero (abbonamento).
    """
    return f"""Cerchi su X e sul web per un sistema che analizza memecoin appena nati su due
chain EVM (Base e una chain minore). NON cercare «quali monete stanno per salire»: quella
domanda e' esclusa, e' rumore e non e' verificabile.

LA DOMANDA, UNA SOLA: **come si procurano i gettoni le persone che poi li vendono sui mercati
decentralizzati, SENZA averli comprati su quei mercati?**

Dati nostri, misurati e non supposti: su circa 172.000 posizioni (portafoglio x moneta), il
45-48% risulta comprata e mai venduta, e una fetta comparabile risulta VENDUTA senza nessun
acquisto osservabile. Di queste ultime, circa la meta' non e' un buco di raccolta: l'acquisto
non e' mai avvenuto su un mercato che guardiamo.

Cerca i MECCANISMI concreti, con nomi propri e link:
1. distribuzioni gratuite (airdrop) al lancio di un gettone: chi le fa, con quali requisiti,
   come si qualifica un portafoglio, e se esistono liste pubbliche di chi riceve;
2. vendite o assegnazioni PRIMA del mercato: prevendite, bonding curve, lanciatori che
   assegnano quote, piattaforme di lancio;
3. mercati o luoghi dove quei gettoni si scambiano PRIMA di comparire sul mercato principale
   (mercati fuori catena, gruppi privati, aste, mercati secondari);
4. trasferimenti fra portafogli dello stesso proprietario come modo di spostare una posizione
   comprata altrove;
5. qualunque altro meccanismo che spieghi «ha gettoni da vendere e non li ha comprati qui».

Per ognuno: **si puo' partecipare noi?** Serve essere invitati, serve capitale, serve storia
sulla chain, e il requisito e' pubblico o discrezionale?

FORMATO: per ogni meccanismo trovato, un blocco con (a) nome e link, (b) come si ottiene il
gettone, (c) quanto prima rispetto al mercato pubblico, (d) il requisito per partecipare,
(e) se esiste un dato pubblico che ci permetta di VEDERE chi ha partecipato.
Scarta tutto cio' che non ha un link verificabile. Meglio tre meccanismi documentati che
quindici nominati.

Cio' che abbiamo gia' trovato, non riportarlo uguale: {_titoli_gia_visti()}

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
