% Thick as thieves: six suspects were interviewed after a robbery. The getaway
% car held at most two, so at most two are guilty. The innocent tell the truth
% and the guilty lie; each suspect made one statement. Find who is guilty.
include "globals.mzn";

% guilty status of each suspect
var bool: artie;
var bool: bill;
var bool: crackitt;
var bool: dodgy;
var bool: edgy;
var bool: fingers;
array[1..6] of var bool: suspects = [artie, bill, crackitt, dodgy, edgy, fingers];

% at most two are guilty because the getaway car was barely big enough for two
constraint sum(s in suspects) (bool2int(s)) <= 2;

% A suspect is guilty exactly when his statement is false (the guilty lie, the innocent
% tell the truth), so each suspect below is equated with the negation of his statement.

% Artie: "It wasn't me." (his statement is "not guilty", so the equation says guilty = guilty
% and leaves him free; the clues about the others and the car size decide)
constraint artie = not (not artie);

% Bill: "Crackitt was in it up to his neck."
constraint bill = not crackitt;

% Crackitt: "No I wasn't." (same shape as Artie's statement, so again no restriction by itself)
constraint crackitt = not (not crackitt);

% Dodgy: "If Crackitt did it, Bill did it with him."
constraint dodgy = not (crackitt -> bill);

% Edgy: "Nobody did it alone." (more than one person is guilty)
constraint edgy = not (sum(s in suspects) (bool2int(s)) > 1);

% Fingers: "That's right: it was Artie and Dodgy together."
constraint fingers = not (artie /\ dodgy);

solve satisfy;

output ["{\"artie\": ", show(artie), ", \"bill\": ", show(bill), ", \"crackitt\": ", show(crackitt),
        ", \"dodgy\": ", show(dodgy), ", \"edgy\": ", show(edgy), ", \"fingers\": ", show(fingers), "}"];
