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
        address sede;             // dove
        bytes   dati;             // la chiamata, preparata fuori
        uint256 posizioneImporto; // dove scrivere la quantita' reale (0 = non scrivere)
    }

    struct Piano {
        address garanzia;      // asset da incassare
        address utente;        // posizione da liquidare
        Passo[] passi;         // come si smonta la garanzia, in ordine
        uint256 guadagnoMinimo; // sotto questo, si annulla tutto
    }

    /// Avvia l'operazione. L'importo e' il debito da coprire.
    function esegui(
        address debito, uint256 importo, Piano calldata p
    ) external soloPadrone {
        pool.flashLoanSimple(address(this), debito, importo, abi.encode(p), 0);
        // qui il prestito e' gia' restituito: cio' che resta e' guadagno
        uint256 resta = IERC20(debito).balanceOf(address(this));
        if (resta > 0) debito.trasferisci(cassa, resta);   // alla cassa, non a chi comanda
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
        for (uint256 i = 0; i < p.passi.length; i++) {
            Passo memory s = p.passi[i];
            uint256 quanto = IERC20(s.gettone).balanceOf(address(this));
            if (quanto == 0) revert ScambioFallito();
            bytes memory dati = s.dati;
            if (s.posizioneImporto > 0) {
                if (s.posizioneImporto + 32 > dati.length) revert ScambioFallito();
                uint256 off = s.posizioneImporto;
                assembly { mstore(add(add(dati, 32), off), quanto) }
            }
            s.gettone.approva(s.sede, quanto);
            (bool ok, ) = s.sede.call(dati);
            if (!ok) revert ScambioFallito();
        }

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

    /// Via d'uscita: se per qualunque motivo restassero gettoni qui, il
    /// padrone li recupera. Non e' una funzionalita', e' una rete.
    function recupera(address gettone) external soloPadrone {
        gettone.trasferisci(cassa, IERC20(gettone).balanceOf(address(this)));
    }
}
