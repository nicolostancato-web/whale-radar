// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";
import "../src/Liquidatore.sol";

/// LA PROVA SU GARANZIA WETH, al blocco di adesso.
/// Nasce da una misura del 31/10: il 60% delle liquidazioni vere di Aave
/// (53 su 93 in 9 giorni) e' su garanzia WETH, e il pescatore non la
/// ammetteva. Prima di ammetterla si prova su una posizione vera, come si
/// e' fatto per weETH: prezzo abbassato quel tanto che serve, dati di
/// vendita freschi dall'aggregatore, e si guarda la CASSA.
contract WethVera is Test {
    address constant POOL  = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;
    address constant ORAC  = 0x54586bE62E3c3580375aE3723C145253060Ca0C2;
    address constant WETH  = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address constant PROXY = 0x216B4B4Ba9F3e719726886d34a177484278Bfcae;
    address constant CASSA = 0x055e75aEaCF141c3118d039D5E099a821152eB66;
    Liquidatore liq;
    function setUp() public {
        vm.createSelectFork(vm.envString("RPC_ARCHIVIO"));
        liq = new Liquidatore(POOL, CASSA);
    }
    function _hf(address u) internal view returns (uint256 h) {
        (bool ok, bytes memory r)=POOL.staticcall(
            abi.encodeWithSignature("getUserAccountData(address)",u));
        if(!ok) return type(uint256).max;
        (,,,,,h)=abi.decode(r,(uint256,uint256,uint256,uint256,uint256,uint256));
    }
    function test_wethVera() public {
        address u   = vm.parseAddress(vm.readFile("dati/utente_weth.txt"));
        address deb = vm.parseAddress(vm.readFile("dati/debito_weth.txt"));
        uint256 qd  = vm.parseUint(vm.readFile("dati/qdebito_weth.txt"));
        address sede= vm.parseAddress(vm.readFile("dati/sede_weth.txt"));
        bytes memory dati = vm.parseBytes(vm.readFile("dati/dati_weth.txt"));
        // la posizione dell'importo viene CERCATA fuori, non assunta: la
        // costante 132 era misurata su una rotta sola e su questa cadeva
        // sull'importo atteso in uscita.
        uint256 pos = vm.parseUint(vm.readFile("dati/posizione_weth.txt"));
        console2.log("posizione dell'importo:", pos);

        console2.log("salute prima (millesimi):", _hf(u)/1e15);
        (bool ok, bytes memory pr)=ORAC.staticcall(
            abi.encodeWithSignature("getAssetPrice(address)",WETH));
        require(ok, "oracolo muto");
        uint256 p0 = abi.decode(pr,(uint256));
        // si cerca il calo MINIMO che la fa cadere, a scatti di mezzo punto:
        // forzare un calo grosso renderebbe la prova piu' facile del vero.
        uint256 giu;
        for (giu = 5; giu <= 150; giu += 5) {
            vm.mockCall(ORAC,
              abi.encodeWithSignature("getAssetPrice(address)",WETH),
              abi.encode(p0*(1000-giu)/1000));
            if (_hf(u) < 1e18) break;
        }
        console2.log("calo necessario (decimi di %):", giu);
        console2.log("salute dopo (millesimi):", _hf(u)/1e15);
        require(_hf(u) < 1e18, "non caduta nemmeno al -15%");

        Liquidatore.Passo[] memory passi = new Liquidatore.Passo[](1);
        passi[0] = Liquidatore.Passo({gettone: WETH, sede: sede,
            daApprovare: PROXY, dati: dati, posizioneImporto: pos});
        Liquidatore.Piano memory piano = Liquidatore.Piano({
            garanzia: WETH, utente: u, passi: passi, guadagnoMinimo: 1});

        uint256 prima = IERC20(deb).balanceOf(CASSA);
        liq.esegui(deb, qd, piano);
        uint256 dopo = IERC20(deb).balanceOf(CASSA);
        console2.log("GUADAGNO in CASSA, unita' grezze del debito:", dopo-prima);
        console2.log("   in dollari circa:", (dopo-prima)/1e6);
        assertGt(dopo, prima, "nessun guadagno in cassa");
    }
}
