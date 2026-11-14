"""LA BANDA: fin dove si guarda. Un numero, un posto.

PERCHE' ESISTE, e costa 353 posizioni invisibili (trovato il 5/11 mattina).
Il limite della banda era scritto DUE volte con DUE valori:
  - prepara_vendite.FINO_A = 1,25   (chi prepariamo)
  - lista_corta             < 1,15   (chi SORVEGLIAMO)
Risultato: le posizioni fra 1,15 e 1,25 non entravano mai nella lista
corta, quindi il pescatore non le guardava e nessun ordine veniva preparato.
Misurato: 353 posizioni con almeno 10.000 $ di debito, 7,38 milioni di
premio lordo stimato, ZERO nella lista corta.

E IL DANNO PEGGIORE era sulla MISURA, non sui soldi: la copertura che
riportavo da giorni ("94% delle vicine") era il 94% della LISTA CORTA, e la
lista corta era il 64% della popolazione in banda. La copertura vera era
circa il 60%, e il numero bello veniva dal fatto che il denominatore era il
nostro recinto invece del mondo.

Regola: un limite che decide CHI GUARDIAMO non puo' stare scritto in due
posti. Se due pezzi devono essere d'accordo, devono leggere lo stesso
numero.
"""

# fin dove si prepara e si sorveglia, in salute (1,0 = soglia di caduta)
BANDA = 1.25

# sotto questo debito in dollari una posizione non paga il gas: il premio e'
# una frazione di meta' del debito, e sotto i 150 $ di debito non resta
# niente dopo il pedaggio del prestito lampo e lo scambio.
# SCESO A 40 $ il 6/11. Il ragionamento dei 150 $ era giusto per il
# profitto, sbagliato per l'OBIETTIVO di oggi: sotto quella soglia il premio
# e' pochi dollari, ma e' anche LA POLVERE CHE NESSUNO CONTENDE -- l'11a
# liquidazione e' rimasta prendibile per due ore. E ci serve attraversare un
# blocco vero almeno una volta.
# A 40 $ di debito il premio e' circa 1 $ e il guadagno minimo preteso 0,40:
# resta positivo dopo il gas (~0,20 $). Sotto i 40 non si scende, perche' li'
# il gas se lo mangia.
# SCESO A 10 $ il 7/11, e questa volta il numero e' MISURATO, non scelto.
# Con lo stato storico (drpc e blastapi servono l'archivio gratis) ho
# ricostruito le 12 liquidazioni perse al blocco PRECEDENTE: 10 su 12 non
# erano liquidabili prima del blocco che le ha liquidate -- sono cadute
# dentro quel blocco, con l'aggiornamento dell'oracolo. Lo «zero liquidabili
# su ~150 misure» del nostro filtro NON e' un guasto: e' la verita', e non
# esiste una corsia lenta verso i premi grossi.
# Delle 2 che ERANO gia' sotto 1 e quindi prendibili senza battere nessuno:
#   debito 33,06 $ -> fuori dalla lista per 7 $ di soglia. Buttata.
#   debito  0,21 $ -> premio 0,01 $, il gas se lo mangia. Giusto escluderla.
# Quindi 10: cattura la prima, esclude la seconda. Costo misurato: la lista
# passa da 2.175 a 2.380 posizioni (+9,4%), e sorvegliare costa poco.
# La guardia economica non sta piu' qui: sta nel pescatore, che dal 7/11
# conosce il gas (vedi agents/gas_ora.py). Sorvegliare largo, sparare
# stretto -- prima erano la stessa soglia e sbagliavano insieme.
# SCESO A 5 il 7/11 pomeriggio, e il motivo e' un rosso da OTTO CENTESIMI.
# Con 10 la soglia di sorveglianza era sopra la convenienza calcolata col gas
# del momento (9,92 $ a 0,046 gwei): cioe' esistevano posizioni che pagavano
# e che non stavamo guardando. La risposta giusta non era allentare il
# controllo -- un controllo allentato per comodita' e' un controllo che non
# serve -- ma sorvegliare piu' largo, perche' guardare costa poco e sparare
# costa gas (vedi la separazione delle due soglie qui sopra).
# Scelto 5 e non 9: la convenienza scende col gas, e col gas piu' basso che
# abbiamo visto (0,03 gwei) arriva a ~7 $. Una soglia che va rincorsa a ogni
# variazione di gas e' una soglia sbagliata; 5 sta sotto tutto l'intervallo
# plausibile. Costo misurato: la lista passa da 2.380 a 2.489 posizioni.
MINIMO_DEBITO = 5


# --------------------------------------------------------------------------
# LA SOGLIA E' UN CONTO, NON UNA COSTANTE.
# Misurato il 7/11 con lo stato storico (drpc e blastapi servono l'archivio
# gratis): delle 12 liquidazioni perse, UNA SOLA era liquidabile nel blocco
# precedente ed era quindi prendibile senza vincere la gara dell'oracolo.
# Debito: 33,06 $. Esclusa dalla lista corta da questa soglia, per 7 $.
# L'unica occasione in 33 ore che non richiedeva di battere nessuno, buttata
# da un numero scritto a mano.
#
# E il 40 e' sbagliato nei DUE versi, perche' non guarda il gas:
#   - col gas di adesso (0,04 gwei) un colpo costa 0,10 $: la soglia giusta
#     e' circa 10 $, e il 40 ci fa perdere le occasioni non contese;
#   - col gas del grappolo che ha prodotto i premi grossi (10 gwei) un colpo
#     costa 24,60 $: la soglia giusta e' circa 2.500 $, e il 40 ci farebbe
#     inseguire posizioni dove il gas si mangia tutto il premio.
# Nicolo' (7/11): «quando cambia il gas noi dobbiamo essere flessibili».
# Questa funzione e' quella flessibilita', scritta dove si decide.
#
# NON CHIAMA LA RETE: prende la base fee da chi ce l'ha gia' e, se non ce
# l'ha, torna alla costante. Un ripiego su una cosa indispensabile sarebbe
# una bugia -- qui non lo e', perche' la costante resta un valore prudente.
PREMIO_SU_DEBITO = 0.03     # meta' del debito x ~6% di bonus, misurato
MARGINE_SUL_GAS = 3.0       # il premio deve valere 3 volte il gas
GAS_PER_COLPO = 1_100_000   # misurato sui nostri piani


def minimo_debito(base_fee_gwei=None, prezzo_eth=None, gas=GAS_PER_COLPO):
    """il debito sotto il quale il gas si mangia il premio, adesso."""
    if not base_fee_gwei or not prezzo_eth or base_fee_gwei <= 0:
        return MINIMO_DEBITO
    costo_usd = gas * base_fee_gwei * 1e-9 * prezzo_eth
    return max(1.0, costo_usd * MARGINE_SUL_GAS / PREMIO_SU_DEBITO)
