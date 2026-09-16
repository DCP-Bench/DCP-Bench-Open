% Arch friends: the order in which Harriet bought four pairs of shoes and where
% she bought each. Every variable holds a stop number from 1 to 4.
include "globals.mzn";

var 1..4: ecruespadrilles; var 1..4: fuchsiaflats;
var 1..4: purplepumps; var 1..4: suedesandals;
var 1..4: footfarm; var 1..4: heelsinahandcart;
var 1..4: theshoepalace; var 1..4: tootsies;

constraint all_different([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]);
constraint all_different([footfarm, heelsinahandcart, theshoepalace, tootsies]);

constraint fuchsiaflats = heelsinahandcart;
constraint purplepumps + 1 != tootsies;
constraint footfarm = 2;
constraint theshoepalace + 2 = suedesandals;

solve satisfy;

output ["{\"ecruespadrilles\": ", show(ecruespadrilles),
        ", \"fuchsiaflats\": ", show(fuchsiaflats),
        ", \"purplepumps\": ", show(purplepumps),
        ", \"suedesandals\": ", show(suedesandals),
        ", \"footfarm\": ", show(footfarm),
        ", \"heelsinahandcart\": ", show(heelsinahandcart),
        ", \"theshoepalace\": ", show(theshoepalace),
        ", \"tootsies\": ", show(tootsies), "}"];
