# I portafogli pubblicati su X: prima verifica — 8 ottobre 2026

## Da dove vengono

Il fascicolo di Grok `chi_pubblica_vincite` ha trovato quello che cercavamo da giorni: **indirizzi
pubblicati pubblicamente** con cifre enormi su **$PONS**, il gettone della piattaforma (non un
memecoin della curva).

Il profilo più costante è `@kkashi_yt`, che pubblica il portafoglio di **altri**, non il proprio:

| data | rivendicazione | indirizzo |
|---|---|---|
| 15 lug 2026 | da 29 $ a oltre 133.000 $ (poi corretto in 151.000 $) | `0xd73d6b8b9e875569c0f03c572a3806e619bcbec2` |
| 17 set 2026 | da 2.667 $ a oltre 1.000.000 $ | `0x81b98a0e207726584ce1ac687fcae6059b35ebcf` |
| 30 set 2026 | oltre 1.121.000 $ | `0x82797a749189f3b99556191d395bfbef709a44c4` |

Da `@coromaroco`: da 61 $ a 940 $, `0xfe657a36ceef09011eba0551dae96ae07dd38518`.

Nella sua stessa bio, Kakashi avvisa che parte di quei profitti **può essere di insider**.

## Cosa ho verificato, e cosa no

**Il gettone esiste e è quello giusto.** `0x39dBED3a2bd333467115dE45665cC57F813C4571`: letto dal
contratto, simbolo `PONS`, nome `Pons`, 18 decimali, fornitura 1 miliardo.

**Il primo portafoglio ha davvero toccato PONS.** Sulla storia intera: **10.512.478 gettoni
ricevuti** e 9.622.304 inviati, in 52 transazioni, fra il blocco 8.964.129 e il 74.511.101. Sono
circa l'**1% della fornitura totale**. Quindi la rivendicazione non è inventata di sana pianta.

**Il guadagno NON è verificato.** Delle 52 transazioni, solo **2** passano da un pool di PONS in
nativo presente nel nostro registro: 0,061451 ETH (158 $) di acquisti e **nessuna vendita**
agganciata. Le altre 50 passano per pool che non abbiamo (in USDG, o su altri mercati). Con il
2% delle transazioni coperte, qualunque cifra di profitto sarebbe inventata — e non la scrivo.

## L'errore che ho evitato per un soffio

La prima lettura dei trasferimenti diceva **zero**, e stavo per concludere «la rivendicazione è
falsa». Poi ho controllato la mia stessa query: chiedeva **81 milioni di blocchi in una volta**,
mentre il limite col filtro sull'indirizzo è 10 milioni. L'RPC dava errore, e il mio codice leggeva
l'errore come «nessun trasferimento».

Rifatta a finestre da 10 milioni, con il conteggio degli errori: 52 transazioni, zero finestre in
errore. **È la stessa famiglia di errore che mi perseguita da tre giorni — un'assenza trattata come
un fatto — e questa volta avrebbe prodotto un'accusa di falso contro qualcuno che i gettoni li
aveva davvero.**

## Il prossimo passo, preciso

Registrare i pool di PONS che ci mancano (254 nel registro, ma le transazioni di questo
portafoglio ne usano altri) e rifare il conto del denaro su tutte e 52 le transazioni. Solo allora
si può dire se quei 133.000 $ esistono.

E poi la domanda che conta davvero: **quelle persone hanno ripetuto?** Un portafoglio con l'1%
della fornitura di un gettone di piattaforma assomiglia più a un insider del lancio che a un
operatore abile — ed è esattamente ciò che l'autore dei post ammette nella sua bio.
