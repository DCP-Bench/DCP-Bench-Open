% People in a room: order the arrivals so the ratio of females to males never
% exceeds seven to three. The puzzle states its own thirteen people, so there
% are no parameters. A true entry is a female arrival.
include "globals.mzn";

int: total_people = 13;
int: num_males = 4;

array[1..total_people] of var bool: sequence;

constraint sum(i in 1..total_people) (bool2int(sequence[i]))
         = total_people - num_males;

% Three females per seven males at most, cleared of the fraction. The reference
% checks every prefix before the last arrival.
constraint forall(i in 1..total_people - 1) (
    let { var int: females = sum(j in 1..i) (bool2int(sequence[j])) } in
    3 * females <= 7 * (i - females)
);

solve satisfy;

output ["{\"sequence\": [",
        join(", ", [show(sequence[i]) | i in 1..total_people]), "]}"];
