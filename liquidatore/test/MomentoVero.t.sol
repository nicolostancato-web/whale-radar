// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";
import "../src/Liquidatore.sol";

/// IL MOMENTO VERO: si rifa' l'istante esatto in cui una liquidazione e'
/// NATA, eseguendo la VERA transazione dell'oracolo sulla copia locale.
///
/// Perche' serve: la sentinella sa vedere l'aggiornamento di prezzo mentre e'
/// ancora in attesa e sa comporre il pacchetto [oracolo, nostra liquidazione]
/// in 434 ms. Ma in 40 minuti di ascolto nessuna posizione e' caduta, quindi
/// non c'era modo di dimostrare che la catena arriva fino in fondo.
/// Qui si prende un caso VERO del passato: blocco 26302299, premio $12.319,
/// una liquidazione avvenuta nello stesso blocco dell'aggiornamento di ETH.
/// Si forka al blocco PRECEDENTE, si esegue la transazione dell'oracolo come
/// l'ha eseguita il suo trasmettitore, e si guarda se la posizione cade.
///
/// Se cade, e' dimostrato che:
///   - la transazione che la sentinella intercetta e' davvero quella che
///     crea l'occasione;
///   - metterla come primo elemento del pacchetto produce lo stato in cui
///     la nostra liquidazione puo' andare a segno.
contract MomentoVero is Test {
    address constant POOL = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;
    address constant ORAC = 0x54586bE62E3c3580375aE3723C145253060Ca0C2;
    address constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    function _hf(address u) internal view returns (uint256 h) {
        (bool ok, bytes memory r)=POOL.staticcall(
            abi.encodeWithSignature("getUserAccountData(address)",u));
        if(!ok) return type(uint256).max;
        (,,,,,h)=abi.decode(r,(uint256,uint256,uint256,uint256,uint256,uint256));
    }
    function _prezzo() internal view returns (uint256 p) {
        (bool ok, bytes memory r)=ORAC.staticcall(
            abi.encodeWithSignature("getAssetPrice(address)",WETH));
        require(ok, "oracolo muto");
        p=abi.decode(r,(uint256));
    }
    function test_momentoVero() public {
        uint256 blocco = vm.parseUint(vm.readFile("dati/c_blocco.txt"));
        address u      = vm.parseAddress(vm.readFile("dati/c_utente.txt"));
        address orDa   = vm.parseAddress(vm.readFile("dati/c_or_da.txt"));
        address orA    = vm.parseAddress(vm.readFile("dati/c_or_a.txt"));
        bytes memory orDati = vm.parseBytes(vm.readFile("dati/c_or_dati.txt"));

        // si va al blocco PRIMA: l'occasione non esiste ancora
        vm.createSelectFork(vm.envString("RPC_ARCHIVIO"), blocco - 1);
        uint256 p0 = _prezzo();
        uint256 h0 = _hf(u);
        console2.log("PRIMA: prezzo ETH (centesimi):", p0/1e6);
        console2.log("PRIMA: salute (millesimi):", h0/1e15);

        // si esegue la VERA transazione dell'oracolo, dal suo trasmettitore
        vm.prank(orDa);
        (bool ok, bytes memory ris) = orA.call(orDati);
        console2.log("transazione dell'oracolo eseguita:", ok);
        if (!ok) {
            console2.log("  si e' annullata: lunghezza risposta", ris.length);
        }
        require(ok, "la transazione dell'oracolo non si puo' rieseguire");

        uint256 p1 = _prezzo();
        uint256 h1 = _hf(u);
        console2.log("DOPO: prezzo ETH (centesimi):", p1/1e6);
        console2.log("DOPO: salute (millesimi):", h1/1e15);
        if (h0 > h1) console2.log("la salute e' SCESA di (millesimi):", (h0-h1)/1e15);

        assertTrue(p1 != p0, "il prezzo non e' cambiato: l'oracolo non ha agito");
        assertLt(h1, 1e18, "la posizione non e' caduta dopo l'aggiornamento");

        // ORA LA NOSTRA LIQUIDAZIONE, nello stesso istante: e' il secondo
        // elemento del pacchetto. Se va a segno, la catena e' dimostrata
        // dall'intercettazione fino all'incasso in cassa.
        address CASSA = 0x055e75aEaCF141c3118d039D5E099a821152eB66;
        address PROXY = 0x216B4B4Ba9F3e719726886d34a177484278Bfcae;
        address deb   = vm.parseAddress(vm.readFile("dati/c_deb.txt"));
        uint256 qd    = vm.parseUint(vm.readFile("dati/c_qdebito.txt"));
        Liquidatore liq = new Liquidatore(POOL, CASSA);
        // LA CHIAMATA SI COSTRUISCE QUI DENTRO, non si legge da un file.
        // DIFETTO trovato subito: i dati preparati fuori avevano come
        // destinatario dello scambio il contratto GIA' DISTRIBUITO, mentre
        // la prova ne crea uno nuovo a un altro indirizzo. Lo scambio
        // riusciva e mandava i soldi all'indirizzo sbagliato: incassato 0,
        // servivano 176.070. Qui il destinatario e' address(liq) per
        // costruzione, quindi non puo' essere sbagliato.
        address ROUTER = 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45;
        bytes memory dati = abi.encodeWithSelector(
            bytes4(0x04e45aaf),          // exactInputSingle di SwapRouter02
            WETH, deb, uint24(500), address(liq),
            uint256(1), uint256(0), uint160(0));
        // l'importo e' la quinta parola: 4 + 4*32 = 132
        Liquidatore.Passo[] memory passi = new Liquidatore.Passo[](1);
        passi[0] = Liquidatore.Passo({gettone: WETH, sede: ROUTER,
            daApprovare: ROUTER,     // su Uniswap preleva il router stesso
            dati: dati, posizioneImporto: 132});
        Liquidatore.Piano memory piano = Liquidatore.Piano({
            garanzia: WETH, utente: u, passi: passi, guadagnoMinimo: 1});
        uint256 prima = IERC20(deb).balanceOf(CASSA);
        liq.esegui(deb, qd, piano);
        uint256 dopo = IERC20(deb).balanceOf(CASSA);
        console2.log("GUADAGNO in cassa (unita' grezze):", dopo-prima);
        console2.log("   in dollari circa:", (dopo-prima)/1e6);
        assertGt(dopo, prima, "nessun guadagno in cassa");
    }
}
