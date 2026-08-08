include "globals.mzn";

% We have 4 shoes and 4 stores, each bought in a unique order from 1 to 4
% Shoes: ecruespadrilles, fuchsiaflats, purplepumps, suedesandals
% Stores: footfarm, heelsinahandcart, theshoepalace, tootsies

% Decision variables: the order in which each shoe was bought (1..4)
var 1..4: ecruespadrilles;
var 1..4: fuchsiaflats;
var 1..4: purplepumps;
var 1..4: suedesandals;

% Decision variables: the order in which each store was visited (1..4)
var 1..4: footfarm;
var 1..4: heelsinahandcart;
var 1..4: theshoepalace;
var 1..4: tootsies;

% All shoes bought at different times
constraint alldifferent([ecruespadrilles, fuchsiaflats, purplepumps, suedesandals]);

% All stores visited at different times
constraint alldifferent([footfarm, heelsinahandcart, theshoepalace, tootsies]);

% 1. Harriet bought fuchsia flats at Heels in a Handcart.
constraint fuchsiaflats == heelsinahandcart;

% 2. The store she visited just after buying her purple pumps was not Tootsies.
% Let the order of purple pumps be p, then the store visited at p+1 is not tootsies
% We need to find which store was visited at order p+1
% So for each store s, if s == p+1 then s != tootsies
constraint
  forall(i in 1..3) (
    (purplepumps == i) -> (tootsies != i+1)
  );

% 3. The Foot Farm was Harriet's second stop.
constraint footfarm == 2;

% 4. Two stops after leaving The Shoe Palace, Harriet bought her suede sandals.
% If theshoepalace is at order s, then suedesandals is at order s+2
constraint suedesandals == theshoepalace + 2;

solve satisfy;

output [
  "{",
  join(",", [
    "\"ecruespadrilles\": " ++ show(ecruespadrilles),
    "\"fuchsiaflats\": " ++ show(fuchsiaflats),
    "\"purplepumps\": " ++ show(purplepumps),
    "\"suedesandals\": " ++ show(suedesandals),
    "\"footfarm\": " ++ show(footfarm),
    "\"heelsinahandcart\": " ++ show(heelsinahandcart),
    "\"theshoepalace\": " ++ show(theshoepalace),
    "\"tootsies\": " ++ show(tootsies)
  ]),
  "}"
];