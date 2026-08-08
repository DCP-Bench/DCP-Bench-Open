
% Suspects: 1 = guilty (liar), 0 = innocent (truth‐teller)
var 0..1: artie;
var 0..1: bill;
var 0..1: crackitt;
var 0..1: dodgy;
var 0..1: edgy;
var 0..1: fingers;

% Exactly two guilty (getaway car held two)
constraint artie + bill + crackitt + dodgy + edgy + fingers = 2;

% BILL: "Crackitt was in it up to his neck."
% If Bill is innocent (0) then crackitt=1; if Bill is guilty (1) then crackitt=0
constraint crackitt = 1 - bill;

% DODGY: "If Crackitt did it, Bill did it with him."
% sD = (crackitt -> bill)
constraint
  if dodgy = 0 then 
    (not (crackitt = 1) \/ (bill = 1))
  else 
    ((crackitt = 1) /\ not (bill = 1))
  endif;

% EDGY: "Nobody did it alone."
% sE = (total_guilty != 1)
% If Edgy is innocent (0) then sE true; if guilty (1) then sE false
constraint
  let { int: total = artie + bill + crackitt + dodgy + edgy + fingers } in
    if edgy = 0 then total != 1 else total = 1 endif;

% FINGERS: "It was Artie and Dodgy together."
% sF = (artie=1 /\ dodgy=1 /\ bill=0 /\ crackitt=0 /\ edgy=0 /\ fingers=0)
% If Fingers is innocent (0) then sF true; if guilty (1) then sF false
constraint
  let {
    bool: sF = (artie = 1 /\ dodgy = 1 /\ bill = 0 /\ crackitt = 0 /\ edgy = 0 /\ fingers = 0)
  } in
    if fingers = 0 then sF else not sF endif;

solve satisfy;

output [
  "{",
    "\"artie\": " ++ show(artie) ++ ",",
    "\"bill\": " ++ show(bill) ++ ",",
    "\"crackitt\": " ++ show(crackitt) ++ ",",
    "\"dodgy\": " ++ show(dodgy) ++ ",",
    "\"edgy\": " ++ show(edgy) ++ ",",
    "\"fingers\": " ++ show(fingers),
  "}"
];
