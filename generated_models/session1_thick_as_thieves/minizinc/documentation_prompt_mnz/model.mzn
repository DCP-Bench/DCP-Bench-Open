include "globals.mzn";

% We have six suspects
enum SUSPECTS = {artie, bill, crackitt, dodgy, edgy, fingers};

% Decision variables: whether each suspect is guilty (true) or innocent (false)
array[SUSPECTS] of var bool: guilty;

% At least four are innocent, so at most two are guilty
constraint sum([bool2int(guilty[s]) | s in SUSPECTS]) <= 2;

% The innocent tell the truth, the guilty lie
% Define the statements as boolean expressions

% ARTIE: "It wasn't me."
% Artie says he is not guilty
var bool: artie_statement = not guilty[artie];

% BILL: "Crackitt was in it up to his neck."
% Bill says Crackitt is guilty
var bool: bill_statement = guilty[crackitt];

% CRACKITT: "No I wasn't."
% Crackitt denies being guilty
var bool: crackitt_statement = not guilty[crackitt];

% DODGY: "If Crackitt did it, Bill did it with him."
% If Crackitt guilty then Bill guilty
var bool: dodgy_statement = (guilty[crackitt] -> guilty[bill]);

% EDGY: "Nobody did it alone."
% No one did it alone means if someone is guilty, at least one other is guilty
% So the number of guilty is not 1
var bool: edgy_statement = (sum([bool2int(guilty[s]) | s in SUSPECTS]) != 1);

% FINGERS: "That’s right: it was Artie and Dodgy together."
% Fingers confirms Edgy's statement and says it was Artie and Dodgy together
% So Fingers says guilty[artie] and guilty[dodgy] and no others
var bool: fingers_statement = (guilty[artie] /\ guilty[dodgy] /\
                              sum([bool2int(guilty[s]) | s in SUSPECTS]) == 2);

% For each suspect:
% If innocent, their statement is true
% If guilty, their statement is false
constraint
  (guilty[artie] -> not artie_statement) /\ (not guilty[artie] -> artie_statement) /\
  (guilty[bill] -> not bill_statement) /\ (not guilty[bill] -> bill_statement) /\
  (guilty[crackitt] -> not crackitt_statement) /\ (not guilty[crackitt] -> crackitt_statement) /\
  (guilty[dodgy] -> not dodgy_statement) /\ (not guilty[dodgy] -> dodgy_statement) /\
  (guilty[edgy] -> not edgy_statement) /\ (not guilty[edgy] -> edgy_statement) /\
  (guilty[fingers] -> not fingers_statement) /\ (not guilty[fingers] -> fingers_statement);

solve satisfy;

output [
  "{",
  join(",", [
    "\"artie\": " ++ show(bool2int(guilty[artie])),
    "\"bill\": " ++ show(bool2int(guilty[bill])),
    "\"crackitt\": " ++ show(bool2int(guilty[crackitt])),
    "\"dodgy\": " ++ show(bool2int(guilty[dodgy])),
    "\"edgy\": " ++ show(bool2int(guilty[edgy])),
    "\"fingers\": " ++ show(bool2int(guilty[fingers]))
  ]),
  "}"
];