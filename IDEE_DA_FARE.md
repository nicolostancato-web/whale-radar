# Idee in attesa — si applicano IN BLOCCO, non una ogni mezz'ora

Regola (5/11, con Nicolò): il sistema è provato e quello che manca è
un'occasione. Ogni modifica rimette in coda centinaia di ordini, quindi le
idee si accumulano qui e si applicano insieme, quando il cassetto è pieno e
stabile o quando Nicolò lo chiede.

## Autorizzate solo da un fatto di sorveglianza

- [ ] **La mancia va calcolata dentro il contratto**, come frazione di ciò che
  resta davvero, invece di stimarla da fuori. Oggi stimiamo il guadagno vero
  dividendo il premio dichiarato per 2,6 — un divisore misurato su UN caso.
  Richiede una nuova distribuzione (~0,11 $). *Valore: toglie una classe
  intera di errore.*
- [ ] **Il divisore 2,6 va cercato su altri casi** e rifiutato se non
  ricompare. Si misura a ogni prova da capo a fondo, senza modifiche.
- [ ] **L'aggregatore resta fuori** finché non lo vediamo incassare in una
  prova. Se serve, si riapre con `PROVA_AGGREGATORE=1`.
- [ ] **Uniswap v4 sulle uscite in ether** per i debiti non in WETH: oggi
  lì la mancia resta a zero.
- [ ] **rsETH→WETH e sUSDe→USDC** (3,4 M$ di premio) restano invendibili:
  il primo non ha pozze da nessuna parte, il secondo è un deposito con
  sette giorni di attesa. Nessuna strada nota.

## Trovate dalla sorveglianza, in attesa

- [ ] **`MustNotLeaveDust()` su una posizione v4** (5/11): il piano a due
  passaggi su weETH→ether nativo fallisce *dentro il nostro contratto* con
  questo errore di Uniswap v4, mentre lo **stesso scambio da solo funziona**
  (provato: 0,2 weETH → 0,2206 ETH). Quindi non è la codifica del
  pagamento: il mio sospetto era sbagliato, e la codifica "esatta"
  alternativa fallisce anche lei. Riguarda una posizione da 47 $ di premio,
  quindi non vale fermarsi ora. *Da riprendere se capita su una posizione
  che conta.*
- [ ] **Le 173 liquidazioni di cui non sappiamo niente** (su 213 in 30 giorni):
  non abbiamo la loro salute prima della caduta, quindi non possiamo dire se
  le avremmo viste. Si potrebbe ricostruire leggendo la salute al blocco
  precedente — ma lo stato storico lo servono solo drpc e blastapi, e su 173
  casi sono tante chiamate. *Valore: direbbe se la fascia basta davvero.
  Alternativa gratuita: aspettare che il live accumuli, con la fotografia.*

## Dalla prima autopsia del live (5/11) — Astra e Grok concordi

- [ ] **Classifica per valore atteso** invece che per premio: `premio reale ×
  probabilità di cadere`, con la probabilità stimata dalla distanza in punti
  base dalla soglia, **per asset** (non la mediana globale dello 0,507%).
  Entrambi lo indicano come la riparazione vera; il tetto per coppia è solo
  la medicazione. *Serve una distribuzione dei movimenti per feed, che non
  abbiamo ancora.*
- [ ] **Penalità di persistenza**: una posizione ferma a salute 1,0006-1,012
  da 48 ore ha pericolosità reale bassa. Decadimento esponenziale del
  punteggio. (Astra)
- [ ] **Misurare la latenza da capo a fondo**: dal prezzo pubblicato al
  pacchetto arrivato al costruttore. È il punto cieco che Grok ha nominato e
  che non misuriamo: se perdiamo 800-1200 ms, nessuna selezione ci salva.
- [ ] **Più di 30 pacchetti e più costruttori**: entrambi dicono che il
  vincolo è il tempo di composizione, non il rifiuto dei relay. Precalcolare
  in continuo e scendere sotto 250 ms, poi salire a 60-100 pacchetti e
  aggiungere porte (rsync, builder0x69, Aestus).
- [ ] **Sui casi a distanza 1**: misurare nel blocco vincente la posizione
  esatta del vincitore e il suo pagamento totale. Se perdiamo col 15% contro
  un 12,3% mediano, o lui stima un ricavato migliore (rotta migliore) o ha un
  canale più veloce.
