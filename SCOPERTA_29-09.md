# Il primo numero positivo — e tutto quello che ancora non dimostra

**29/09, sera. Trovato misurando, non cercando: e' uscito da un controllo su un'altra cosa.**

## Il numero

Comprare **$25** in **ogni** pool, al suo **25° scambio**, e liquidare dentro la settimana
successiva. Nessuna selezione: si compra tutto. Al netto dell'1,8% di costo di giro.

| | robinhood | base |
|---|---|---|
| media (= portafoglio in parti uguali) | **+6,0%** | −0,1% |
| mediana | +0,8% | −0,4% |
| pool giudicati | 16.634 | 12.192 |

Su robinhood, per periodo di nascita: **−1,3% / +2,8% / +11,1% / +6,5% / +10,7%**. Quattro
periodi su cinque positivi, e la mediana positiva in quattro su cinque — **non lo fanno solo
pochi pool fortunati**. Togliendo l'1% migliore resta positivo in tre periodi su cinque.

## Da dove veniva l'errore che ce lo nascondeva

Per settimane abbiamo misurato entrando **due ore** dopo la nascita. Quella regola richiede che
il pool abbia ancora uno scambio a due ore — e **scarta tutti gli altri, in silenzio**.

Sono **due terzi dei pool**. E sono quelli che guadagnano:

| robinhood | N | media | mediana | in pari |
|---|---|---|---|---|
| visti anche dalla regola delle 2 ore | 4.611 | −4,5% | −1,8% | 32% |
| **scartati dalla regola delle 2 ore** | **10.336** | **+11,1%** | **+8,3%** | **65%** |

Misuravamo il terzo sbagliato. I pool ancora scambiati due ore dopo sono quelli che hanno gia'
pompato e stanno scendendo; quelli che concentrano la vita nelle prime ore salgono.

> **Una condizione d'ingresso e' anche un filtro sulla popolazione. «Compro a due ore» sembra
> una scelta di tempismo: era una selezione che teneva solo i sopravvissuti lenti.**

## Non e' un rimbalzo meccanico — verificato

Sospetto obbligatorio: se il 25° scambio e' una vendita, il prezzo d'ingresso e' depresso dal
suo impatto, e il rimbalzo immediato darebbe un guadagno finto.

Smentito: il guadagno misurato sul **prezzo mediano dell'intera finestra** e' PIU' grande
(+22,9% medio, +18,1% mediana) di quello preso vendendo subito (+11,1%). Il prezzo resta sopra,
non rimbalza e basta.

## Cosa questo NON dimostra — i limiti, per intero

1. **La capienza e' minuscola.** A $500 il vantaggio sparisce: +0,3% su robinhood, −8,6% su
   base. Esiste a $25–$100. Un portafoglio vero richiede di comprare MOLTI pool, non uno grande.
2. **Su base non funziona** (−0,1%). Una chain sola non e' una strategia.
3. **Il costo d'acquisto non e' modellato.** Simuliamo la vendita dentro il flusso reale, ma
   l'acquisto lo assumiamo al prezzo di quello scambio, senza impatto ne' gas. A $25 l'impatto
   e' piccolo, il gas no: su una catena EVM puo' mangiarsi il margine da solo.
4. **Bisogna accorgersi del pool al 25° scambio e comprare li'.** Quel tempo di reazione non
   e' in nessuno di questi numeri.
5. **E' misura del passato.** Non c'e' adattamento — non abbiamo scelto niente, quindi non c'e'
   sovra-adattamento — ma l'epoca resta un sospetto: quattro dei cinque periodi positivi sono
   di settembre.

## La prova in avanti, registrata ADESSO

Perche' valga, deve sopravvivere su pool **nati dopo oggi**, che non esistono mentre scrivo.

- **Regola fissa, senza parametri da scegliere:** $25 su ogni pool al suo 25° scambio,
  liquidazione entro 168 ore, su robinhood e su base separatamente.
- **Serve almeno 1.500 pool nuovi** per chain prima di guardare il risultato.
- **Soglia:** media sopra **+3%** al netto dell'1,8% di costo. Sotto, non si procede.
- **Si guarda una volta sola, a fine finestra.** Nessuno sbirciare prima: guardare presto e
  fermarsi quando piace e' il modo classico di comprare rumore.
- **Se passa su robinhood e non su base**, non e' bocciata: si annota che vale dove il mercato
  e' abbastanza spesso, e la prova continua su robinhood.

**Nessun euro rischiato finche' questa prova non e' chiusa.**
