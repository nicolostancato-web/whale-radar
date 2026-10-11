# Ricerca Grok — tassa_e_esenti

Modello grok-4.7. Costo: ZERO (abbonamento, nessuna chiave API). Tempo: 595s. 4/4 sotto-domande con risposta.

---

### Sulla curva di Pons di Robinhood Chain: esiste una tassa anti-snipe nei primi secondi dopo il lancio? Dimmi la percentuale e per quanti secondi vale, col link alla fonte.

Cerco la specifica ufficiale della curva di Pons su Robinhood Chain, in particolare la tassa anti-snipe dei primi secondi.Le fonti secondarie non coincidono su durata e curva. Vado alla documentazione ufficiale di Pons e, se serve, ai parametri on-chain della factory.La doc ufficiale dice 5 secondi, ma letture on-chain parlano di 3. Controllo i parametri della factory, a costo zero.

### Sulla curva di Pons: esistono indirizzi ESENTATI dalla tassa anti-snipe? Quanti per lancio, chi li scegle, e come si leggono dalla transazione di creazione? Col link.

Cerco nella documentazione di Pons se la curva prevede indirizzi esentati dalla tassa anti-snipe, quanti sono per lancio e dove compaiono nella transazione di creazione.

### Sulla curva di Pons: qual e' la commissione normale di acquisto e di vendita, e chi la incassa? Col link alla fonte ufficiale.

Cerco la commissione ufficiale di acquisto e vendita sulla curva di Pons e chi la incassa.Le pagine secondarie citano l’1%, ma il dettaglio sta nei docs ufficiali. Li apro adesso.

### Sulla curva di Pons: quale soglia fa 'graduare' una moneta e cosa succede esattamente alla graduazione? Col link.

Cerco la soglia di graduazione sulla curva di Pons e cosa cambia esattamente al momento della graduation.Le fonti secondarie concordano sulla soglia da 4,2 ETH, ma divergono sul dettaglio della graduation. Cerco la documentazione ufficiale.Sulla curva di Pons v2 la moneta gradua quando la curva ha incassato **4,2 ETH reali**. Il riserva virtuale di 1,68 ETH che fissa il prezzo di apertura non conta. Per un lancio prezzato in un altro asset approvato (stablecoin, azione tokenizzata) la soglia è un importo di quell’asset, non 4,2 ETH.

Fonte: [docs.ponsfamily.com/v2](https://docs.ponsfamily.com/v2#graduation). La soglia è il campo `graduationThreshold` della launch config; sulla config ETH standard vale 4,2 ETH e il progresso è `realQuoteReserve / graduationThreshold`. Le due letture (ETH raccolti e token ancora vendibili) arrivano a zero insieme.

A quel punto, dentro l’acquisto che chiude la curva:

1. La curva smette di vendere. Se l’ultimo buy è più grande del residuo, compri solo ciò che resta e il resto ti torna nella stessa transazione. Da quel momento non si può più vendere alla curva.
2. La curva consegna i 4,2 ETH raccolti più i token tenuti da parte fin dall’inizio. Con supply da 1 miliardo e config standard sono **2/7** della supply, circa 285,7 milioni. I **5/7** (circa 714,3 milioni) sono già nei wallet di chi ha comprato. Il prezzo è **12,25×** quello di apertura e la market cap è circa **20,6 ETH**.
3. Nasce un pool Uniswap v4 full-range, con l’hook di Pons. La posizione viene mintata direttamente nel launch locker (`0x267444D099b10fB5Ed7c3Cc7B7c767AdcA574952` su Robinhood Chain). Non esiste una funzione di unlock: né il creator né Pons possono prelevare la liquidità.
4. Nel pool entrano i 4,2 ETH e **10/49** della supply (circa 204 milioni), così il prezzo del pool coincide con quello di chiusura della curva. Il fantasma da 1,68 ETH non è denaro vero, quindi i **4/49** rimanenti (circa 82 milioni) non possono entrare nel pool e restano bloccati per sempre nello stesso locker.
5. I token che hai già in wallet non cambiano. Da lì si compra e si vende solo sul pool. La fee resta quella di Pons; Uniswap non ne aggiunge una sua.

Se l’ultimo buy non riesce a creare il pool (di solito per gas), chiunque può chiamare `createGraduatedPool`. Se il lancio resta fermo fra i due passaggi per 7 giorni, Pons può restituire quanto raccolto, e quel lancio resta marcato. La graduation dice solo che la curva è sold out: non è un giudizio sulla moneta.
