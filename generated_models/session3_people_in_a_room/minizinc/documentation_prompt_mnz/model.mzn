include "globals.mzn";

% Number of people
int: total_people = 13;
int: males = 4;
int: females = total_people - males;

% Decision variable: sequence of people entering the room
% 0 represents male, 1 represents female
array[1..total_people] of var 0..1: sequence;

% Constraints:

% Exactly 4 males and 9 females in the sequence
constraint
    sum([bool2int(sequence[i] == 0) | i in 1..total_people]) == males /\
    sum([bool2int(sequence[i] == 1) | i in 1..total_people]) == females;

% For each prefix of the sequence, the ratio of females to males is no greater than 7/3
% That is, females_in_prefix / males_in_prefix <= 7/3
% Handle the case when males_in_prefix = 0: then females_in_prefix must be 0 (no males yet, so ratio undefined)
% So females_in_prefix == 0 when males_in_prefix == 0
constraint
    forall(i in 1..total_people) (
        let {
            var int: females_in_prefix = sum([bool2int(sequence[j] == 1) | j in 1..i]),
            var int: males_in_prefix = sum([bool2int(sequence[j] == 0) | j in 1..i])
        } in
        (males_in_prefix == 0 -> females_in_prefix == 0) /\
        (males_in_prefix > 0 -> females_in_prefix * 3 <= males_in_prefix * 7)
    );

solve satisfy;

output [
    "{",
    "\"sequence\": ", show(sequence),
    "}"
];