// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// Liquidatore con prestito istantaneo.
///
/// La sequenza, tutta dentro UNA transazione:
///   1. chiede in prestito ad Aave l'asset del debito
///   2. liquida la posizione e riceve la garanzia scontata
///   3. vende la garanzia per riavere l'asset del debito
///   4. restituisce il prestito piu' lo 0,05% di commissione
///   5. se cio' che resta e' sotto la soglia, ANNULLA TUTTO
///
/// La riga 5 e' la ragione per cui questo si puo' provare con 52 euro: il
/// caso peggiore di un errore, di una gara persa o di un prezzo che si
/// muove a meta' operazione e' una transazione annullata che costa
/// centesimi di gas. Il contratto non tiene fondi fra un'operazione e
/// l'altra, quindi non c'e' niente da rubargli.

interface IPool {
    function flashLoanSimple(
        address receiver, address asset, uint256 amount,
        bytes calldata params, uint16 referralCode
    ) external;
    function liquidationCall(
        address collateralAsset, address debtAsset, address user,
        uint256 debtToCover, bool receiveAToken
    ) external;
}

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function transfer(address to, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IWETH {
    function withdraw(uint256 amount) external;
    function deposit() external payable;
}

/// USDT non rispetta lo standard: non restituisce il valore atteso da
/// transfer e approve. Nei nostri dati USDT e' l'asset di debito di 24
/// occasioni su 288, quindi usarlo «normalmente» romperebbe proprio dove
/// c'e' piu' lavoro. Si accetta sia chi risponde sia chi tace, e si
/// rifiuta solo chi risponde «no».
library Sicuro {
    error ChiamataGettoneFallita();
    function _chiama(address gettone, bytes memory dati) private {
        (bool ok, bytes memory ris) = gettone.call(dati);
        if (!ok) revert ChiamataGettoneFallita();
        if (ris.length > 0 && !abi.decode(ris, (bool))) revert ChiamataGettoneFallita();
    }
    function trasferisci(address gettone, address a, uint256 q) internal {
        _chiama(gettone, abi.encodeWithSelector(IERC20.transfer.selector, a, q));
    }
    function approva(address gettone, address a, uint256 q) internal {
        // alcuni gettoni (USDT) rifiutano di cambiare un permesso non nullo:
        // si azzera prima.
        _chiama(gettone, abi.encodeWithSelector(IERC20.approve.selector, a, 0));
        _chiama(gettone, abi.encodeWithSelector(IERC20.approve.selector, a, q));
    }
}

/// Scambio generico: l'indirizzo e i dati arrivano da fuori, cosi' si puo'
/// cambiare sede di scambio senza ridistribuire il contratto. Solo il
/// padrone puo' chiamare, quindi non e' una porta aperta.
contract Liquidatore {
    address constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    using Sicuro for address;
    /// chi puo' comandare il contratto: il portafoglio operativo, quello
    /// la cui chiave sta sul computer e contiene solo gas
    address public immutable padrone;
    /// dove finisce il GUADAGNO: un indirizzo di cui la chiave ce l'ha solo
    /// Nicolo'. Cosi' il portafoglio operativo non accumula mai valore, e
    /// se quella chiave venisse compromessa si perderebbe solo il gas.
    address public immutable cassa;
    IPool   public immutable pool;

    error NonSeiIlPadrone();
    error NonEIlPool();
    error GuadagnoInsufficiente(uint256 ottenuto, uint256 richiesto);
    error ScambioFallito();
    error IndirizzoNullo();

    constructor(address _pool, address _cassa) {
        if (_pool == address(0) || _cassa == address(0)) revert IndirizzoNullo();
        padrone = msg.sender;
        cassa = _cassa;
        pool = IPool(_pool);
    }

    modifier soloPadrone() {
        if (msg.sender != padrone) revert NonSeiIlPadrone();
        _;
    }

    /// Un passaggio di vendita. Servono piu' passaggi perche' certe
    /// garanzie non si vendono in un colpo solo: sUSDe esce su Curve verso
    /// DOLA, e da DOLA bisogna arrivare all'asset del debito. Invece di un
    /// trucco per quel caso, il contratto accetta una CATENA di passaggi:
    /// vale per qualunque garanzia, anche quelle che non abbiamo ancora visto.
    struct Passo {
        address gettone;          // cosa si vende in questo passaggio
        address sede;             // CHI SI CHIAMA
        address daApprovare;      // CHI PRELEVA (spesso diverso!)
        bytes   dati;             // la chiamata, preparata fuori
        uint256 posizioneImporto; // dove scrivere la quantita' reale (0 = non scrivere)
    }

    struct Piano {
        address garanzia;      // asset da incassare
        address utente;        // posizione da liquidare
        Passo[] passi;         // come si smonta la garanzia, in ordine
        uint256 guadagnoMinimo; // sotto questo, si annulla tutto
        /// QUANTO SI PAGA A CHI COSTRUISCE IL BLOCCO, in wei di ETH, preso
        /// DAL RICAVATO di questa stessa operazione.
        ///
        /// PERCHE' ESISTE, ed e' il muro che ci teneva fuori (misurato il
        /// 4/11). Finora offrivamo solo la priority fee, che si paga in ETH
        /// dal portafoglio operativo: con 39 dollari di saldo il massimo
        /// offribile era 23,68 dollari, cioe' lo 0,018% di un premio da
        /// 130.841 dollari. Il vincitore studiato aveva priority fee ZERO e
        /// la liquidazione in posizione 2 dopo l'aggiornamento dell'oracolo:
        /// pagava per vie interne, dal ricavato.
        /// LA REGOLA GENERALE: un'offerta legata al PORTAFOGLIO non puo'
        /// competere con un'offerta legata al PREMIO. Con 52 euro di
        /// capitale non e' una questione di tarare meglio una soglia: e' un
        /// canale su cui non si vince per costruzione.
        /// Si paga solo se tutto e' andato a buon fine, perche' se la
        /// transazione si annulla il pacchetto non entra e non si paga
        /// niente.
        uint256 mancia;
    }

    error ManciaOltreIlGuadagno(uint256 resta, uint256 mancia);
    /// serve per ricevere l'ETH dallo scarto del WETH prima di pagare
    receive() external payable {}

    /// Avvia l'operazione. L'importo e' il debito da coprire.
    function esegui(
        address debito, uint256 importo, Piano calldata p
    ) external soloPadrone {
        pool.flashLoanSimple(address(this), debito, importo, abi.encode(p), 0);
        // qui il prestito e' gia' restituito: cio' che resta e' guadagno
        uint256 resta = IERC20(debito).balanceOf(address(this));
        if (p.mancia > 0) {
            // La mancia si paga in ETH, quindi il guadagno deve essere in
            // WETH: e' il caso dominante (26 delle 27 posizioni a tiro hanno
            // debito WETH). Sulle altre coppie non si paga, invece di
            // inventare uno scambio in piu' dentro il momento che conta.
            if (debito != WETH) revert ManciaOltreIlGuadagno(resta, p.mancia);
            if (resta <= p.mancia) revert ManciaOltreIlGuadagno(resta, p.mancia);
            IWETH(WETH).withdraw(p.mancia);
            (bool ok, ) = block.coinbase.call{value: p.mancia}("");
            if (!ok) revert ManciaOltreIlGuadagno(resta, p.mancia);
            resta -= p.mancia;
        }
        if (resta > 0) debito.trasferisci(cassa, resta);   // alla cassa, non a chi comanda
    }

    /// COME `esegui`, MA SI PUO' PAGARE IL COSTRUTTORE ANCHE QUANDO IL
    /// GUADAGNO NON E' IN WETH.
    ///
    /// PERCHE' ESISTE (5/11). Chi costruisce il blocco vuole ETH, e il
    /// guadagno di una liquidazione e' nell'asset del DEBITO. Quando il
    /// debito e' WETH basta scartarlo; quando e' una stablecoin il contratto
    /// non sapeva trasformarne una fetta, quindi su quelle coppie andavamo
    /// all'asta MUTI. Misurato: solo 7 ordini su 302 con coppia diversa
    /// portavano un'offerta, e i debiti in stablecoin sono la maggior parte
    /// del mercato. Non era una soglia da tarare: era un canale su cui non
    /// si vinceva per costruzione, e l'ho lasciato aperto troppi giorni.
    ///
    /// PERCHE' UNA FUNZIONE NUOVA E NON UN CAMPO IN PIU' NEL PIANO:
    /// cambiare la firma di `esegui` avrebbe invalidato in un colpo tutti i
    /// 985 ordini pronti, e si rigenerano a 29 per passata -- ore di
    /// cecita' proprio mentre cerchiamo la prima presa. Questa e' aggiunta,
    /// non sostituzione: i vecchi ordini continuano a funzionare identici.
    ///
    /// `passiMancia` e' la catena che porta il guadagno in WETH, preparata
    /// fuori come tutte le altre: il contratto non sceglie nessuna sede da
    /// se'. Si converte TUTTO il residuo, non una fetta: la quantita' esatta
    /// che serve per ottenere `mancia` wei non si puo' sapere prima dello
    /// scambio, e tirare a indovinare qui vorrebbe dire annullare
    /// l'operazione proprio quando ha funzionato. Il resto va in cassa in
    /// WETH invece che in stablecoin: e' lo stesso valore.
    function eseguiConMancia(
        address debito, uint256 importo, Piano calldata p,
        Passo[] calldata passiMancia
    ) external soloPadrone {
        pool.flashLoanSimple(address(this), debito, importo, abi.encode(p), 0);
        if (p.mancia == 0) {
            // niente offerta: ci si comporta come `esegui`
            uint256 soloResta = IERC20(debito).balanceOf(address(this));
            if (soloResta > 0) debito.trasferisci(cassa, soloResta);
            return;
        }
        if (debito != WETH) {
            if (passiMancia.length == 0) {
                revert ManciaOltreIlGuadagno(0, p.mancia);
            }
            Passo[] memory catena = passiMancia;
            _vendi(catena);
            _avvolgi();          // l'ultimo passaggio puo' uscire in ether nudo
        }
        uint256 resta = IERC20(WETH).balanceOf(address(this));
        if (resta <= p.mancia) revert ManciaOltreIlGuadagno(resta, p.mancia);
        IWETH(WETH).withdraw(p.mancia);
        (bool ok, ) = block.coinbase.call{value: p.mancia}("");
        if (!ok) revert ManciaOltreIlGuadagno(resta, p.mancia);
        resta -= p.mancia;
        if (resta > 0) WETH.trasferisci(cassa, resta);
    }

    /// Avvolge l'ether nudo che il contratto si trovasse in mano.
    /// Non e' una comodita': senza questo, le pozze di Uniswap v4 sul
    /// nativo -- cioe' le migliori per WBTC e wstETH -- sono inutilizzabili,
    /// perche' la catena dei passaggi sa leggere solo saldi di gettoni.
    function _avvolgi() private {
        uint256 nudo = address(this).balance;
        if (nudo > 0) IWETH(WETH).deposit{value: nudo}();
    }

    /// Chiamata da Aave dentro il prestito istantaneo.
    function executeOperation(
        address asset, uint256 amount, uint256 premium,
        address, bytes calldata params
    ) external returns (bool) {
        if (msg.sender != address(pool)) revert NonEIlPool();
        Piano memory p = abi.decode(params, (Piano));

        asset.approva(address(pool), amount);
        pool.liquidationCall(p.garanzia, asset, p.utente, amount, false);

        // Vendita della garanzia. La sede e i dati sono preparati fuori,
        // cosi' si usa il percorso migliore del momento.
        //
        // PERO' la QUANTITA' non si puo' sapere prima: si scopre solo qui,
        // dentro l'operazione. Quindi il contratto la scrive da se' nella
        // chiamata, alla posizione indicata. (Prima passavo zero e lo
        // scambio falliva: era il mio errore di progetto, trovato dalla
        // prova su copia locale.)
        _vendi(p.passi);

        _avvolgi();   // l'uscita dell'ultimo passaggio puo' essere ether
        uint256 daRestituire = amount + premium;
        uint256 ho = IERC20(asset).balanceOf(address(this));

        // LA RIGA CHE RENDE TUTTO PROVABILE CON 52 EURO:
        // se non copro il prestito piu' il guadagno minimo, annullo.
        if (ho < daRestituire + p.guadagnoMinimo) {
            revert GuadagnoInsufficiente(ho, daRestituire + p.guadagnoMinimo);
        }

        asset.approva(address(pool), daRestituire);
        return true;
    }

    /// LA CATENA DI VENDITA, una volta sola per tutti.
    /// Era dentro executeOperation; adesso serve anche DOPO il prestito, per
    /// trasformare in ETH la fetta che va a chi costruisce il blocco quando
    /// il guadagno non e' gia' in WETH.
    function _vendi(Passo[] memory passi) private {
        for (uint256 i = 0; i < passi.length; i++) {
            Passo memory s = passi[i];
            // L'ETHER NUDO SI AVVOLGE SUBITO (aggiunto il 5/11).
            // Misurato: su Uniswap v4 l'ether NON e' avvolto, e le pozze
            // migliori di WBTC (100,21%) e wstETH (99,67%) stanno proprio
            // sul nativo. Ma ogni passaggio qui legge il saldo di un
            // GETTONE: l'ether che arriva da quelle pozze era invisibile a
            // tutta la catena, quindi quelle rese non si potevano prendere.
            // Si avvolge all'inizio di ogni passaggio (cosi' funziona anche
            // a metà catena) e di nuovo alla fine del ciclo.
            _avvolgi();
            uint256 quanto = IERC20(s.gettone).balanceOf(address(this));
            if (quanto == 0) revert ScambioFallito();
            bytes memory dati = s.dati;
            if (s.posizioneImporto > 0) {
                if (s.posizioneImporto + 32 > dati.length) revert ScambioFallito();
                uint256 off = s.posizioneImporto;
                assembly { mstore(add(add(dati, 32), off), quanto) }
            }
            // LEZIONE 31/10: gli aggregatori non prelevano col contratto che
            // si chiama — ne usano un altro dedicato ai trasferimenti.
            // Autorizzare quello sbagliato dava «transfer amount exceeds
            // allowance» e sembrava un difetto dei dati. E' come dare la
            // delega al direttore quando a ritirare viene il cassiere.
            address chiPreleva = s.daApprovare == address(0) ? s.sede : s.daApprovare;
            s.gettone.approva(chiPreleva, quanto);
            (bool ok, ) = s.sede.call(dati);
            if (!ok) revert ScambioFallito();
        }
    }

    /// Via d'uscita: se per qualunque motivo restassero gettoni qui, il
    /// padrone li recupera. Non e' una funzionalita', e' una rete.
    function recupera(address gettone) external soloPadrone {
        gettone.trasferisci(cassa, IERC20(gettone).balanceOf(address(this)));
    }
}
