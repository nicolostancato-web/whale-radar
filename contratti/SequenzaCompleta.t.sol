// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/Liquidatore.sol";

/// Il router vuole una STRUTTURA, non campi sciolti: passandoli separati
/// manca il puntatore in testa e il router riceve dati illeggibili
/// (InvalidFEOpcode con 506 di gas). Dichiarando l'interfaccia, il
/// compilatore codifica correttamente.
interface IRouter {
    struct ExactInputParams {
        bytes path;
        address recipient;
        uint256 amountIn;
        uint256 amountOutMinimum;
    }
    function exactInput(ExactInputParams calldata params)
        external payable returns (uint256 amountOut);
}

/// LA PROVA CHE CONTA: la sequenza completa, su copia locale.
///
/// Al blocco scelto la posizione ha salute 1,0043 — non ancora liquidabile.
/// Qui si abbassa il prezzo dell'oracolo quel tanto che basta a farla
/// cadere. Non e' barare: la caduta e' l'evento che nella realta' arriva da
/// solo. Quello che si vuole provare e' TUTTO CIO' CHE VIENE DOPO:
/// prestito istantaneo -> liquidazione -> vendita -> restituzione -> guadagno.
contract SequenzaCompleta is Test {
    address constant POOL    = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;
    address constant ORACOLO = 0x54586bE62E3c3580375aE3723C145253060Ca0C2;
    address constant USDC    = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address constant WSTETH  = 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0;
    address constant WETH    = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address constant ROUTER  = 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45;
    address constant UTENTE  = 0x0Ed0eA598e89765471e86A060bd91F4BB2dc1fB0;

    Liquidatore liq;

    function setUp() public {
        vm.createSelectFork(vm.envString("RPC_ARCHIVIO"), 26198342);
        liq = new Liquidatore(POOL);
    }

    function _salute(address u) internal view returns (uint256 hf) {
        (bool ok, bytes memory r) = POOL.staticcall(
            abi.encodeWithSignature("getUserAccountData(address)", u));
        require(ok, "lettura fallita");
        (, , , , , hf) = abi.decode(r,(uint256,uint256,uint256,uint256,uint256,uint256));
    }

    function _prezzo(address a) internal view returns (uint256 p) {
        (bool ok, bytes memory r) = ORACOLO.staticcall(
            abi.encodeWithSignature("getAssetPrice(address)", a));
        require(ok, "prezzo non letto");
        p = abi.decode(r,(uint256));
    }

    function test_sequenzaCompleta() public {
        uint256 prima = _salute(UTENTE);
        console2.log("salute di partenza (1e18):", prima);

        // si abbassa del 2% il prezzo della garanzia: basta a far cadere
        uint256 p = _prezzo(WSTETH);
        uint256 nuovo = p * 98 / 100;
        vm.mockCall(ORACOLO,
            abi.encodeWithSignature("getAssetPrice(address)", WSTETH),
            abi.encode(nuovo));
        console2.log("prezzo wstETH da", p, "a", nuovo);

        uint256 dopo = _salute(UTENTE);
        console2.log("salute dopo il calo (1e18):", dopo);
        assertLt(dopo, 1e18, "non e' caduta nemmeno col calo");

        // ora la sequenza vera
        uint256 debito = 400_000_000000;   // 400.000 USDC, chiusura parziale

        bytes memory percorso = abi.encodePacked(
            WSTETH, uint24(100), WETH, uint24(500), USDC);
        bytes memory scambio = abi.encodeCall(IRouter.exactInput,
            (IRouter.ExactInputParams({
                path: percorso,
                recipient: address(liq),
                amountIn: 0,            // lo scrive il contratto
                amountOutMinimum: 0
            })));

        // dove sta la quantita' dentro la chiamata exactInput:
        // 4 (selettore) + 32 (offset struct) + 32 (offset percorso)
        // + 32 (destinatario) = 100 byte
        Liquidatore.Piano memory piano = Liquidatore.Piano({
            garanzia: WSTETH,
            utente: UTENTE,
            sede: ROUTER,
            datiScambio: scambio,
            posizioneImporto: 100,
            guadagnoMinimo: 1_000000      // 1 USDC
        });

        uint256 saldoPrima = IERC20(USDC).balanceOf(address(this));
        liq.esegui(USDC, debito, piano);
        uint256 saldoDopo = IERC20(USDC).balanceOf(address(this));

        uint256 guadagno = saldoDopo - saldoPrima;
        console2.log("GUADAGNO in USDC (6 decimali):", guadagno);
        console2.log("cioe' dollari:", guadagno / 1e6);
        assertGt(guadagno, 0, "nessun guadagno");
    }
}
