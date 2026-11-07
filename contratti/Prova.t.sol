// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/Liquidatore.sol";

/// Riproduce una liquidazione VERA gia' avvenuta, su una copia locale della
/// chain. Nessun soldo reale esiste qui dentro.
///
/// Bersaglio: blocco 26198343, premio misurato 79.010 EUR.
/// 1.585.794 USDC di debito ripagati, 576,44 wstETH incassati.
/// Garanzia wstETH: esattamente la nicchia che i professionisti non
/// presidiano.
contract Prova is Test {
    address constant POOL   = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;
    address constant USDC   = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;
    address constant WSTETH = 0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0;
    address constant WETH   = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address constant ROUTER = 0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45; // SwapRouter02
    address constant UTENTE = 0x0Ed0eA598e89765471e86A060bd91F4BB2dc1fB0;
    uint256 constant BLOCCO = 26198342;

    Liquidatore liq;

    function setUp() public {
        vm.createSelectFork(vm.envString("RPC_ARCHIVIO"), BLOCCO);
        liq = new Liquidatore(POOL);
    }

    function _salute(address u) internal view returns (uint256 hf) {
        (bool ok, bytes memory r) = POOL.staticcall(
            abi.encodeWithSignature("getUserAccountData(address)", u));
        require(ok, "lettura salute fallita");
        (, , , , , hf) = abi.decode(r,
            (uint256,uint256,uint256,uint256,uint256,uint256));
    }

    function test_laPosizioneELiquidabile() public view {
        uint256 hf = _salute(UTENTE);
        console2.log("salute della posizione (1e18):", hf);
        assertLt(hf, 1e18, "la posizione non e' liquidabile a questo blocco");
    }

    function test_liquidazioneCompleta() public {
        uint256 hf = _salute(UTENTE);
        if (hf >= 1e18) { console2.log("non liquidabile, salto"); return; }

        uint256 debito = 1_585_794_920_000; // USDC, 6 decimali

        // vendita della garanzia: wstETH -> WETH -> USDC, percorso Uniswap v3
        bytes memory percorso = abi.encodePacked(
            WSTETH, uint24(100), WETH, uint24(500), USDC);
        bytes memory scambio = abi.encodeWithSignature(
            "exactInput((bytes,address,uint256,uint256))",
            percorso, address(liq), uint256(0), uint256(0));

        Liquidatore.Piano memory p = Liquidatore.Piano({
            garanzia: WSTETH,
            utente: UTENTE,
            sede: ROUTER,
            datiScambio: scambio,
            guadagnoMinimo: 1_000_000   // 1 USDC: soglia bassa per la prova
        });

        uint256 prima = IERC20(USDC).balanceOf(address(this));
        liq.esegui(USDC, debito, p);
        uint256 dopo = IERC20(USDC).balanceOf(address(this));

        console2.log("guadagno in USDC (6 decimali):", dopo - prima);
        assertGt(dopo, prima, "nessun guadagno");
    }
}
