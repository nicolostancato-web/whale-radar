1. L'impostazione è sbagliata alla radice.  
Con 0,016 ETH di capitale e senza relazione diretta con builder non stai competendo nel mercato che descrivi; stai misurando quanto sei lento a perdere. L'architettura a cinque blocchi + giudice è secondaria finché non risolvi il fatto che il vincitore paga 210 ETH fuori catena per l'ordine.

2. La regola del 101% è una trappola di scope creep.  
Ogni perdita verrà reinterpretata come "mancava una verifica", quindi aggiungerai controlli interni all'infinito mentre il problema è esterno (relazione builder, capitale per mance, accesso esclusivo). Limitala a massimo due iterazioni per perdita; dopo la terza perdita identica devi cambiare ipotesi, non aggiungere sensori.

3. Il vincitore ha un accordo privato con il builder.  
Priority fee zero + pagamento 210 ETH a un indirizzo di payout builder indica direct payment o bundle privato, non un bundle Flashbots pubblico. Con 37 USD non puoi replicare il pagamento; puoi solo sperare di entrare in un relay che abbia già quel tipo di accordo (probabilità prossima allo zero).

4. Con capitale operativo sotto i 5-10 ETH e senza relazioni, la fascia realistica è vuota.  
Le uniche liquidazioni che un nuovo entrante senza capitale prende oggi sono quelle sotto i ~40-60 USD di premio netto dopo gas, e anche quelle vengono prese da bot già dentro i builder con priority fee negativa o zero. Rendimento atteso: zero al mese.

5. Non stai misurando i flussi off-chain.  
Manca completamente la misurazione di: (a) quali builder accettano pagamenti diretti e da chi, (b) quali searcher hanno RPC privati o connessioni esclusive con gli oracoli, (c) la distribuzione reale dei bundle per builder (non solo "accettati dal relay"). Queste tre metriche spiegano la quasi totalità delle tue perdite.