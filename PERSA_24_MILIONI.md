# La liquidazione da 24 milioni che abbiamo perso — autopsia

**Quando.** 4/11/2026, blocco 26.342.152.
**Posizione.** `0x8d53903625b8e839b9df4bd28b0efb1cd6b8639a` — garanzia USDT, debito WETH.
**Debito chiuso.** $24.048.189. **Garanzia presa.** $24.346.131.
**Premio reale incassato da un altro: $297.942.**
**Chi l'ha preso.** `0xeef1b06e23a39f05b6b34ff1052d7a6ca3a00005`, transazione
`0xf5ff0c7106886a61fddb7a03ab7da7b3ae50cd4ba62e1f418b7a07f98434a3eb`.

## Non abbiamo perso un'asta

Il vincitore ha pagato **1,92 dollari** di gas, con mancia al costruttore
**ZERO** (prezzo effettivo = base del blocco, 1,247 gwei), in seconda
posizione nel blocco. Nessuna gara d'offerta: ha mandato una transazione
normale ed e' arrivato prima. Quindi il nostro limite di offerta (~$22, il
60% di 0,0163 ETH) **non e' la causa**: non c'era niente da battere.

## Cosa sapevamo, e cosa guardavamo

| | |
|---|---|
| in composizione | **sì** |
| ordine di vendita pronto | **sì**, col margine attuale |
| premio che stimavamo | $130.841 |
| la sentinella l'ha messa fra le candidate | **1.140 volte** |
| pacchetti composti e accettati dal relay | 30 per aggiornamento, tutti accettati |
| salute che la sentinella LEGGEVA dalla catena | **1,0217** |
| salute nel nostro ARCHIVIO | **1,1841** |
| era nella lista che il pescatore sorveglia | **NO** |

## Il difetto, in una frase

**I due sistemi non sono d'accordo su quali posizioni contano, e quello che ha
il dato fresco non e' quello che guarda sempre.**

- La **sentinella** legge la salute dalla catena e la sapeva: 1,0217. Ma spara
  solo quando passa un aggiornamento dell'oracolo, e in quei momenti la
  posizione era ancora sopra 1,0: i suoi pacchetti si annullavano, giustamente.
- Il **pescatore** controlla la salute a ogni blocco, ed e' lui che avrebbe
  preso una caduta per scivolamento. Ma la sua lista nasce dall'**archivio**,
  che diceva 1,1841 — sopra la soglia di 1,15 della lista corta, quindi
  **esclusa**.

Un errore di 0,16 in un archivio ha tenuto fuori dalla sorveglianza continua
la posizione piu' preziosa del laghetto.

## Perche' le guardie non l'hanno visto

- La sonda `fuori_dal_recinto.py` esiste proprio per questo: trova le
  posizioni il cui valore in archivio e' vecchio e che in realta' sono molto
  piu' basse. Ma legge **40 posizioni su 11.000** per giro. Questa non e'
  uscita.
- Il controllo "chi sappiamo in pericolo e' nella lista" confronta
  l'**archivio** con la lista: se l'archivio sbaglia, il confronto non vede
  niente. **Un controllo che confronta due cose che vengono dalla stessa
  fonte sbagliata non puo' accorgersi dell'errore.**

## Cosa va cambiato (blocco 6)

1. La lista del pescatore non deve dipendere solo dall'archivio: **le
   candidate che la sentinella legge dal vivo devono entrarci subito**.
2. La sentinella, quando legge una salute molto piu' bassa di quella in
   archivio, deve **correggere l'archivio** invece di tenersela.
3. La verifica deve confrontare la lista con una lettura **viva**, non con
   l'archivio.

## La cosa che conta di piu'

**Per la prima volta siamo stati in una gara vera**, e abbiamo perso per un
motivo che si puo' riparare — non per lentezza, non per soldi, non per
sfortuna. E l'abbiamo scoperto perche' Nicolo' ha chiesto "siamo sicuri che
non ci sono possibilita'?" invece di fidarsi di cinque blocchi al 100%.
