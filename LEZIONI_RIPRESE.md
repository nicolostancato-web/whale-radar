# Tre lezioni dalla notte del 29-30 settembre

## 1. Spento non e' rotto

Trentatre' corsie su sessanta non giravano da un mese. Ho guardato l'esito dell'ultimo giro —
«annullato» — e ne ho dedotto che una cancellazione le avesse uccise. L'ho detto al fondatore
come un fatto.

Erano **disattivate a mano** (`workflow.state: disabled_manually`): una decisione presa il 17
settembre. Lo stato «annullato» era solo l'ultimo giro, interrotto nel momento dello spegnimento.

> **L'esito dell'ultimo giro dice come e' finito quel giro, non perche' non ce ne sono stati
> altri.** Prima di spiegare un silenzio, chiedi se qualcuno ha premuto un interruttore.

Un sistema fermo per scelta e uno fermo per guasto hanno **lo stesso aspetto nei registri** e
richiedono azioni opposte: il primo va lasciato in pace, il secondo riparato.

## 2. Una corsia che smette di esistere non manda niente

Una corsia che fallisce manda una email. Una che smette di girare non manda niente: semplicemente
non appare piu' nei registri, e i registri mostrano solo quello che c'e'.

Per questo il guasto e' durato un mese senza che nessuno lo notasse. **Il censimento va fatto
sulla lista completa delle corsie, non su quelle che si sono viste.**

## 3. Una modifica precedente puo' rendere invisibile la successiva

Stanotte ho aggiunto dei commenti sopra gli orologi delle corsie. Stamattina, spegnendo gli
orologi dei relitti, lo schema cercava «`schedule:` seguito da `- cron:`» — e non combaciava piu',
perche' in mezzo c'erano i miei commenti.

Diciannove corsie sistemate, una ancora sveglia. L'ha trovata la porta contando.

> **Uno schema che cerca un testo esatto smette di funzionare appena qualcuno scrive qualcosa in
> mezzo — compreso te stesso, ieri.**
