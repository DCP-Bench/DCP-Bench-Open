% Kidney exchange: choose donations along a directed compatibility graph so
% that as many people as possible receive a kidney, where anyone who gives a
% kidney must receive one and nobody gives or receives more than one.

int: num_people;
% compatible[i] lists the people (1-based) to whom i can donate; the rows are
% ragged, so the runner pads them with 0 to the longest row and
% compatible_len[i] says how many entries of row i are real
array[int,int] of int: compatible;
array[int] of int: compatible_len;

set of int: Person = 1..num_people;

% transplants[i, j] is true if person i donates to person j
array[Person, Person] of var bool: transplants;

% i can donate to j only if j is among the real entries of compatible[i]
constraint forall(i, j in Person
                  where not exists(k in 1..compatible_len[i])(compatible[i, k] = j))(
  not transplants[i, j]
);

% each person donates to at most one person and receives from at most one person
constraint forall(i in Person)(sum(j in Person)(bool2int(transplants[i, j])) <= 1);
constraint forall(i in Person)(sum(j in Person)(bool2int(transplants[j, i])) <= 1);

% anyone who gives a kidney must receive one
constraint forall(i in Person)(
  exists(j in Person)(transplants[i, j]) -> exists(j in Person)(transplants[j, i])
);

% maximise the number of transplants
var int: objective = sum(i, j in Person)(bool2int(transplants[i, j]));
solve maximize objective;

output ["{\"transplants\": [",
        join(", ", ["[" ++ join(", ", [show(transplants[i, j]) | j in Person]) ++ "]" | i in Person]),
        "]}"];
