# ⚠️ APERTO — il recupero nascite non raccoglie nulla, e non so ancora perché

*17 settembre 2026, notte · scritto prima di avere la risposta, apposta*

## Il fatto

`agents/recupero_nascite.py` gira da ore e ha fatto **16.837 chiamate raccogliendo ZERO scambi**.
I pool «senza le prime ore» su robinhood restano **270**, fermi.

## Cosa ho già corretto stanotte (tutti difetti veri, nessuno risolutivo)

1. **La chiave del segnalibro era mobile.** I confini dei tratti nascono dalla fusione degli
   intervalli dei pool: basta che lo scopritore ne aggiunga uno e il confine si sposta di qualche
   minuto, quindi la chiave cambia e il lavoro fatto non viene più riconosciuto. Quattro cursori
   aperti su tratti quasi identici. → confini arrotondati a una griglia di sei ore.

2. **Buttavo dati che stavo già guardando.** Scandendo i blocchi del tratto A vedevo passare pool
   che mi servono ma appartenenti al tratto B, e li scartavo. I tratti servono a decidere DOVE
   guardare, non COSA vale. → si tiene qualunque pool della lista completa.

3. **L'istante era interpolato sui nostri dati.** Lo stesso metodo che il 16/09 avevo misurato
   sbagliare fino a **15 ore e mezza**: con una finestra di sei ore, un filtro così non filtra,
   scarta tutto. L'avevo già sostituito con la bisezione per la conversione inversa e mi ero perso
   questa. → due chiamate per lotto danno gli istanti veri dei due estremi.

## Cosa resta senza risposta

Dopo tutte e tre le correzioni: **18 pool cercati visti passare, zero tenuti.** Una sonda mirata
sulla nascita di un pool ha contato **99 scambi di pool cercati, firma perfetta, tutti fuori dalla
finestra di vita dei rispettivi pool**.

Le due spiegazioni ancora in piedi, e non so quale sia:

- **Il cursore è all'inizio di un tratto lungo 266 ore** e i pool che vede passare appartengono a
  finestre che stanno più avanti: sarebbe funzionamento corretto, solo lento.
- **La «nascita» che usiamo viene dalle candele**, non dalla catena. Se le due non coincidono,
  stiamo cercando ogni pool nel posto sbagliato — e il filtro scarterebbe sempre tutto, per sempre.

Il confronto fra nascita-da-candele e nascita-da-catena (evento `Initialize`) è il prossimo
accertamento, ed è quello che decide.

## Perché scrivo questo invece di continuare

Ho fatto sei accertamenti di fila su questo pezzo senza arrivare a una risposta. Continuare al buio
costa più di quanto renda, e il resto del database intanto avanza benissimo. Questo file esiste
perché domani io — o chiunque altro — non debba ricostruire da zero cosa era già stato escluso.

**Un difetto noto e scritto costa un'ora domani. Un difetto noto e taciuto costa una conclusione
sbagliata fra tre settimane.**
