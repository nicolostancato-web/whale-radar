# Audit dell'auto-learning — 28 settembre 2026

*Richiesto da Nicolò: «prima di modificare qualsiasi cosa, fai un audit di ciò che esiste già.
Non cercare di confermare le mie idee: cerca di migliorare il sistema.»*
**Verificato sui file, non a memoria.** 152 agenti, 59 corsie.

---

## A. Già presente e funzionante

**Errori → prevenzione con i denti.** `pubblica.sh` ha **tre porte che bloccano**: il codice deve
compilare; il metro congelato (`agents/prova_metro.py`) deve dare le sei risposte note; nessuna
corsia può nascere senza riarmo. Tutte e tre provate rompendole apposta.
È già il livello *«esiste un controllo che impedisce di ripeterlo»*, non *«ricordiamoci»*.

**Ipotesi registrate prima dei dati.** `IPOTESI_H6.md`, `IPOTESI_H7.md` con condizioni di morte
scritte in anticipo, e `agents/verdetto_h7.py` che **si rifiuta di mostrare** i terzi sotto i 600
pool. Copre gran parte dei punti 5 e 10: la soglia è fissata prima, non adattabile al risultato.

**Memoria degli esperimenti falliti.** Otto verdetti con la causa della morte.

**Lezioni scritte nel punto che le userà**, come commenti dentro il codice che può ripetere l'errore.

**Ciclo osservazione → azione → stato**: `piu_intelligente.py` → `data/azioni_miglioramento.json`.

## B. Parzialmente presente

**Il ciclo si ferma prima della verifica.** Oggi: osservazione → ipotesi → modifica → «fatta».
Mancano **critica** e **verifica indipendente** (punto 12). Propongo, eseguo e dichiaro chiusa io.

**Memoria metodologica in prosa, non strutturata.** Niente record a otto campi, niente `STATO`
(ipotesi / in verifica / verificata / smentita / obsoleta). Conseguenza: **tratto come verità anche
le lezioni mai riverificate.**

**Astra non è collegato all'auto-learning**: la domanda quotidiana chiama solo Grok (punto 14 non
implementato).

**Un solo banco di prova, scritto da me per funzioni scritte da me.**

## C. Mancante

- **Critic che può rifiutare** una modifica: non esiste alcun percorso in cui una mia proposta venga
  respinta.
- **Limite di modifiche per ciclo**: nessuno (oggi sei in tre ore).
- **Pruning**: niente rimuove regole obsolete. Un parametro rimasto dopo la cancellazione della sua
  ragione l'ho trovato a mano, per caso.
- **Meta-learning**: si chiede *cosa* ho imparato, mai *come ho provato a impararlo*.
- **Valutazione su casi indipendenti**: nessuna modifica è mai stata provata su qualcosa di diverso
  dal caso da cui è nata.
- **`strategy.yaml` non esiste più**: doveva essere la fonte unica delle decisioni leggibile dal
  codice. Le decisioni vivono in prosa, che è il difetto che quel file doveva risolvere.

## D. Non consigliato

**Il ciclo completo per OGNI modifica**: ucciderebbe il ritmo. Meglio **tre livelli per raggio
d'azione**: una corsia → basta che il lavoro avanzi; una misura → banco di prova + confronto
obbligatori; i criteri di validazione → Astra obbligatorio, e mai durante un'ipotesi in corso.

**Astra quotidiano**: no, e per un motivo più forte del costo — **due revisori che parlano ogni
giorno smettono di essere indipendenti**: cominciano a discutere del mio racconto invece dei fatti.

## E. Quello che aggiungerei io

### Il banco degli incidenti veri (la cosa più importante)

Abbiamo una settimana di guasti reali e documentati: verso dei prezzi invertito, finestra di
osservazione, criterio di scarto che eliminava i morti, il 10x da 32 dollari, tre corsie nate senza
riarmo, la guardia che accettava il cron rotto. Per ognuno sappiamo **come si manifestava**.

Il test è: *«il sistema di oggi avrebbe pescato quell'incidente?»*, sui dati di allora. Se un
controllo non riconosce l'errore storico che dice di prevenire, **è teatro** e va buttato.

È l'unica difesa vera contro la trappola del punto 6, perché quei casi **non li ho progettati io per
passare**: sono successi prima delle difese.

### Due misure che cambierebbero il giudizio
- **quota di rilievi che vengono da FUORI** (revisore, dati, realtà) contro quelli dai miei controlli.
  Se scende verso zero, ci stiamo solo confermando.
- **costo in tempo macchina di ogni miglioramento**. Il 28/09 due corsie mie giravano 23 volte
  l'ora per non fare niente: nessun controllo l'avrebbe mai segnalato.

## F. Dove rischiamo l'auto-overfitting — concretamente

1. **Scrivo io sia il test sia il codice che deve passarlo.** Il metro verifica sei casi scelti da me
   conoscendo l'implementazione.
2. **Il 28/09 ho fatto letteralmente la cosa del paper**: ho modificato **due volte** il codice che
   raccoglie le prove su cui la domanda giudica se stiamo migliorando. Le modifiche erano giuste
   (misurava i file in ordine alfabetico), ma **ho aggiustato lo strumento che misura il mio
   miglioramento e nessuno l'ha controllato**.
3. **La metrica di apprendimento è auto-dichiarata**: «quanto in fretta riconosco un errore» — decido
   io cosa conta come errore e quando me ne sono accorto. Non è falsificabile.
4. **Le porte sono facili da soddisfare per chi le ha costruite**: so cosa controllano, quindi il mio
   codice le passa per costruzione. È la definizione dello studente che ha visto le domande.
5. **L'anello è chiuso**: la domanda produce azioni, io le eseguo, io le segno «fatta» scrivendo io
   perché sono riuscite. Nessun passaggio esce dalle mie mani.

---

## Proposta di ordine

1. **Banco degli incidenti passati** — porta prove che non ho scelto io.
2. **`STATO` sulle lezioni** — smette di trattare come verità ciò che non è stato riverificato.
3. *Poi* critic e limite di modifiche: senza una prova indipendente, un critic diventa solo un'altra
   cosa che discute col mio racconto.

*Nulla di questo è stato implementato: l'audit viene prima, come richiesto.*
