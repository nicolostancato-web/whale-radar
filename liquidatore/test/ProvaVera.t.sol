// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
import "forge-std/Test.sol";
import "../src/Liquidatore.sol";

/// LA PROVA, per QUALUNQUE garanzia, su posizione vera al blocco attuale.
/// Generalizza WethVera: una prova per asset significa sei prove che si
/// somigliano e nessuna aggiornata. I dati li prepara agents/prepara_prova.py.
///
/// Un asset si arma SOLO se questa passa. Regola stabilita il 31/10 dopo che
/// WETH -- il 60% del mercato reale -- e' stato ammesso solo dopo la prova.
contract ProvaVera is Test {
    address constant POOL  = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;
    address constant ORAC  = 0x54586bE62E3c3580375aE3723C145253060Ca0C2;
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
    function test_provaVera() public {
        address u   = vm.parseAddress(vm.readFile("dati/p_utente.txt"));
        address gar = vm.parseAddress(vm.readFile("dati/p_garanzia.txt"));
        address deb = vm.parseAddress(vm.readFile("dati/p_debito.txt"));
        uint256 qd  = vm.parseUint(vm.readFile("dati/p_qdebito.txt"));
        uint256 pos = vm.parseUint(vm.readFile("dati/p_posizione.txt"));
        bool stesso = vm.parseUint(vm.readFile("dati/p_stesso.txt")) == 1;

        console2.log("salute prima (millesimi):", _hf(u)/1e15);
        if (stesso) {
            // STESSO GETTONE: abbassare il prezzo non la fa cadere (garanzia e
            // debito scalano insieme). Ma su queste coppie il debito costa piu'
            // di quanto rende la garanzia, quindi cadono col TEMPO. Si fa
            // passare il tempo sulla copia locale finche' non cade davvero.
            // Non e' un trucco: e' il meccanismo vero con cui cadono, solo
            // accelerato. Nessun prezzo falsificato.
            uint256 giorni;
            for (giorni = 90; giorni <= 365*6; giorni += 90) {
                vm.warp(block.timestamp + 90 days);
                vm.roll(block.number + 90*7200);
                if (_hf(u) < 1e18) break;
            }
            console2.log("giorni di interessi necessari:", giorni);
        }
        if (!stesso) {
            (bool ok, bytes memory pr)=ORAC.staticcall(
                abi.encodeWithSignature("getAssetPrice(address)",gar));
            require(ok, "oracolo muto");
            uint256 p0 = abi.decode(pr,(uint256));
            // il calo MINIMO che la fa cadere, a scatti di mezzo punto:
            // forzarne uno grosso renderebbe la prova piu' facile del vero.
            // CROLLO FORZATO: si parte dal calo richiesto via variabile
            // d'ambiente, per provare che un ordine preparato PRIMA del
            // crollo regge anche a -10%. La ragione: l'importo incassato e'
            // fissato in DOLLARI (107% del debito), quindi se il prezzo
            // scende si incassano PIU' token e vendendone piu' al prezzo
            // piu' basso si ottengono gli stessi dollari. Il minimo scritto
            // nell'ordine era calcolato per meno token a prezzo piu' alto.
            // E' un ragionamento, e i ragionamenti sul SEGNO si sbagliano:
            // per questo si prova.
            uint256 minimo = vm.envOr("CALO_MINIMO", uint256(5));
            uint256 giu;
            for (giu = minimo; giu <= 300; giu += 5) {
                vm.mockCall(ORAC,
                  abi.encodeWithSignature("getAssetPrice(address)",gar),
                  abi.encode(p0*(1000-giu)/1000));
                if (_hf(u) < 1e18) break;
            }
            console2.log("calo necessario (decimi di %):", giu);
        }
        console2.log("salute al momento del colpo (millesimi):", _hf(u)/1e15);
        require(_hf(u) < 1e18, "non caduta: scegliere un'altra posizione");

        Liquidatore.Passo[] memory passi;
        if (stesso) {
            passi = new Liquidatore.Passo[](0);
        } else {
            passi = new Liquidatore.Passo[](1);
            passi[0] = Liquidatore.Passo({gettone: gar,
                sede: vm.parseAddress(vm.readFile("dati/p_sede.txt")),
                // CHI AUTORIZZARE lo dice il file, non e' piu' fisso:
                // con l'aggregatore e' il suo proxy, con il ripiego su
                // Uniswap e' il router stesso (si passa zero e il
                // contratto autorizza la sede).
                daApprovare: vm.parseAddress(vm.readFile("dati/p_approvare.txt")),
                dati: vm.parseBytes(vm.readFile("dati/p_dati.txt")),
                posizioneImporto: pos});
        }
        Liquidatore.Piano memory piano = Liquidatore.Piano({
            garanzia: gar, utente: u, passi: passi,
                // il guadagno preteso lo scrive chi prepara i dati, NELLA MONETA
                // del debito: passarlo come numero grezzo da fuori ha fatto
                // fallire la prova il 4/11 (8,17e17 su un debito a 6 decimali).
                guadagnoMinimo: vm.parseUint(vm.readFile("dati/p_guadagno.txt"))});

        uint256 prima = IERC20(deb).balanceOf(CASSA);
        liq.esegui(deb, qd, piano);
        uint256 dopo = IERC20(deb).balanceOf(CASSA);
        console2.log("GUADAGNO in CASSA, unita' grezze:", dopo-prima);
        assertGt(dopo, prima, "nessun guadagno in cassa");
    }
}
