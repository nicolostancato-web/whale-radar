# 🧭 I due revisori esterni — Astra (max 3/giorno) e Grok (illimitato)

*Regola fissata il 21 settembre 2026. Non si cambia senza registrarlo in `DECISIONS.md`.*

## La regola, in una riga

## IL PROTOCOLLO (deciso da Nicolò il 24/09/2026)

| quando | chi si chiama | costo |
|---|---|---|
| revisioni 1, 2, 3 del giorno | **Astra E Grok**, la stessa domanda a entrambi | ~$0,11 (solo Astra) |
| dalla quarta in poi | **solo Grok** | **zero** |

**Ogni volta che si chiede ad Astra si chiede anche a Grok.** Due pareri indipendenti al prezzo di
uno. Grok è nell'abbonamento Plus di Nicolò (~35 €/mese già pagati) e si usa **sempre via OAuth,
mai con la chiave API** — la chiave esiste nel file delle credenziali e usarla significherebbe
pagare a consumo *in aggiunta* all'abbonamento. `agents/consulta_grok.py` toglie ogni chiave
dall'ambiente prima di chiamare, come cintura di sicurezza.

**Perché due e non uno.** Il 24/09, alla sua prima revisione, Grok ha trovato un errore logico che
Astra non aveva visto: avevo spiegato una variazione del mercato con «la quota variabile di pool
trappola», e lui ha notato che nel primo periodo l'effetto aveva **segno opposto** — una quota
variabile di un effetto costante non può cambiare segno, quindi la mia spiegazione era impossibile.
Ragionano in modo diverso. Quando concordano per strade diverse il risultato vale molto di più;
quando si contraddicono, si è imparato dove scavare.

**Tre revisioni al giorno sono abbastanza** (parole di Nicolò): non si chiede un parere ogni due
ore. Si chiede quando c'è qualcosa di vero da far giudicare — un risultato nuovo, una decisione di
metodo presa da soli, un numero su cui si sta per costruire.

---

**Astra: fino a TRE volte al giorno** (alzato il 23/09/2026 da Nicolò, prima era una).

*Motivo, con le sue parole:* «dato che ci costa solo 10 cent a chiamata, facciamo che in sta fase
molto delicata quando abbiamo bisogno di una revisione come si deve possiamo chiamarlo».

**Tre e' il massimo, non l'obiettivo.** Si chiama quando c'e' qualcosa di vero da far giudicare —
un risultato nuovo, una decisione di metodo presa da soli, un numero su cui stiamo per costruire.
Non per tenere compagnia, non per conferme. Costo: ~$0,11 a chiamata, al massimo ~$10/mese.

## Il modello è uno solo

Il consulente è **`gpt-6-astra`**, il modello più potente di OpenAI. Nessun altro.

Il modello è **scritto nel codice**, non dietro una variabile d'ambiente: prima bastava una
variabile sbagliata in una corsia per consultare in silenzio un modello più debole, e la
consulenza sarebbe tornata lo stesso — solo peggiore. **Un mentore scambiato non dà errore: dà
consigli mediocri che crediamo suoi.**

E non basta chiederlo: `consulta_astra.py` **controlla chi ha risposto**. Se il servizio serve un
modello diverso da quello chiesto — ripieghi, alias, deprecazioni — la consulenza viene trattata
come **non fatta**. A occhio quella differenza non si vedrebbe: cambierebbe solo la qualità del
consiglio, ed è il tipo di errore che qui scopriamo sei settimane dopo.

## Cosa fa, e cosa non fa

> *«Noi costruiamo, lui ci dà qualche consiglio in più — oppure ci toglie quell'illusione.»*
> — Nicolò, 21/09/2026

Astra **non costruisce e non corregge**. Il suo mestiere è uno solo: trovare dove ci stiamo
raccontando una storia. Il brief gli vieta esplicitamente di toccare il codice — e non è una
formalità:

- due agenti che scrivono gli stessi file si cancellano il lavoro a vicenda (successo tre volte in
  una settimana, una volta ha buttato tre giri interi di riparazione);
- **un revisore che può aggiustare smette di cercare**: trova il primo difetto, lo sistema, si
  sente a posto. Uno che può solo indicare è costretto ad andare avanti.

## Perché esiste

Due mesi fa abbiamo costruito un database, ci abbiamo cercato sopra un vantaggio per un mese e
mezzo, e solo alla fine abbiamo scoperto che i dati non erano accurati. Quel lavoro è stato buttato.

I difetti che fanno male sono quelli dentro le cose che abbiamo scritto noi, convinti che
andassero bene. **Per definizione non possiamo cercarli da soli.**

Alla prima consulenza vera, il 21/09, ne ha trovati subito tre:

| rilievo | esito della verifica |
|---|---|
| un totale che non quadrava in `DEFINIZIONE.md` | **vero** — 184 pool di scarto, erano due estrazioni diverse spacciate per una |
| la soglia contata al contrario («oltre 20» invece di «almeno 20») | **vero** — 528 pool che la regola includeva e la tabella buttava |
| la sonda che certificava 300 record dopo averne letti 3 | **vero nel codice**, ma misurato: zero contaminazione nei dati |

Nessuna delle tre sarebbe emersa da sola.

## Come si lancia

```
python3 agents/fascicolo_astra.py     # prepara le misure vere (costo zero)
python3 agents/consulta_astra.py      # Astra (~$0,11, max 3 al giorno)
python3 agents/consulta_grok.py       # Grok  (ZERO, abbonamento, illimitato)
```

Il tetto giornaliero è **nel codice**, non nella buona volontà: `MAX_AL_GIORNO = 1`.

## I freni prima del portafoglio

1. **Tetto dei token.** Oltre 272.000 token in ingresso, Astra ripreza *l'intera* richiesta al
   doppio — non il sovrapprezzo sull'eccedenza: tutto. Il fascicolo viene tagliato a 250.000
   **prima** di partire, così quel confine non lo attraversiamo per distrazione.
2. **Contatore giornaliero nel repo.** Il cap sul fornitore è l'ultima linea, non la prima: un
   ciclo che si riarma male spedisce cento volte in un'ora, e il cap se ne accorge a soldi spesi.
3. **Il contatore si segna solo se la chiamata è partita.** Un errore di rete non deve mangiarci
   una consulenza — è il genere di scambio fra fallimento ed esito che in questo progetto è già
   successo otto volte.
4. **Tariffa flex**, metà del listino: una consulenza la leggiamo dopo, non serve pagare la fretta.

## Il silenzio si misura

`agents/silenzio_revisione.py` dice da quanti giorni nessuno ci guarda da fuori, e il numero
compare accanto a quelli del database a ogni aggiornamento.

Serve perché il 17/09 la revisione esterna era ferma **da sei giorni** e nessuno se n'era accorto:
era prevista, e **una cosa prevista che non accade non fa rumore**. La soglia d'allarme è a due
giorni, bassa di proposito.

## Codex resta, in più — non al posto

Codex è incluso nell'abbonamento ChatGPT Plus e **legge il codice vero**, non solo le misure che
gli prepariamo noi: è la revisione più profonda delle due, e costa zero. Brief in
`BRIEF_CODEX_REVISORE.md`.

Ma va lanciato a mano, perché è agganciato all'account del fondatore e nessuno può pilotarlo da
fuori. Astra è il battito quotidiano che garantisce di non restare mai ciechi; Codex è
l'approfondimento quando c'è tempo.
