# MomentoVero.t.sol — parcheggiata il 5/11/2026

**Perché**: con l'aggiunta del campo `mancia` alla struct `Piano`, quella funzione di prova
sfora la pila del compilatore («stack too deep») e **blocca l'intera compilazione** — quindi
nessuna prova gira, nemmeno quelle buone. Una prova che non compila non è un controllo: è un
freno a mano.

**Cosa copriva**: liquidazione su una posizione reale col prezzo spinto giù a mano, vendita
WETH su Uniswap v3, verifica dell'accredito in cassa.

**Chi la sostituisce oggi**: `DaCapoAFondo.t.sol` fa la stessa cosa in modo più forte —
legge la **calldata vera** dal cassetto invece di costruire il piano in Solidity.

**Come riprenderla**: spezzare la funzione in due (le variabili locali sono troppe nella
stessa), oppure abilitare `viaIR = true` nel profilo delle prove — più lento ma risolve la pila.

**Non è un abbandono silenzioso**: sta scritto qui perché la copertura persa si veda.
