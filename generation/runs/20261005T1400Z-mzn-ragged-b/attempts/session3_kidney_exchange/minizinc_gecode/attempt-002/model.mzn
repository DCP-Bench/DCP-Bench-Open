% Kidney exchange: choose donations along a directed compatibility graph so
% that as many people as possible receive a kidney, where anyone who gives a
% kidney must receive one and nobody gives or receives more than one.
include "globals.mzn";

int: num_people;
% compatible[i] lists the people (1-based) to whom i can donate; the rows are
% ragged, so the runner pads them with 0 to the longest row and
% compatible_len[i] says how many entries of row i are real
array[int,int] of int: compatible;
array[int] of int: compatible_len;

set of int: Person = 1..num_people;
% the real entries of compatible[i], without the padding
array[Person] of set of int: can_donate_to =
  [{compatible[i, k] | k in 1..compatible_len[i]} | i in Person];

% transplants[i, j] is true if person i donates to person j
array[Person, Person] of var bool: transplants;

% i can donate to j only if j is among the real entries of compatible[i]
constraint forall(i, j in Person where not (j in can_donate_to[i]))(not transplants[i, j]);

% each person donates to at most one person and receives from at most one person
constraint forall(i in Person)(sum(j in Person)(bool2int(transplants[i, j])) <= 1);
constraint forall(i in Person)(sum(j in Person)(bool2int(transplants[j, i])) <= 1);

% anyone who gives a kidney must receive one
constraint forall(i in Person)(
  exists(j in Person)(transplants[i, j]) -> exists(j in Person)(transplants[j, i])
);

% Implied view, added because Gecode times out on a dense 20-person instance
% with the Boolean matrix alone. The three groups above force the donations to
% form disjoint cycles: every donor receives, each person gives and receives at
% most once, so the number of donors equals the number of receivers and the two
% sets coincide. Such a set of cycles is a permutation of the people, with
% succ[i] the person i donates to and succ[i] = i when i takes no part.
% succ is a function of transplants (one value per assignment of the outputs),
% so it adds no solution and removes none.
array[Person] of var Person: succ;
constraint forall(i in Person)(succ[i] in can_donate_to[i] union {i});
constraint all_different(succ);
% i donates to another person j exactly when succ[i] = j; a donation to oneself,
% if compatible[i] ever allowed it, also leaves succ[i] = i
constraint forall(i, j in Person where i != j)(transplants[i, j] <-> succ[i] = j);
constraint forall(i in Person)(transplants[i, i] -> succ[i] = i);

% maximise the number of transplants; at most one per person, so the
% objective is bounded by num_people
var 0..num_people: objective = sum(i, j in Person)(bool2int(transplants[i, j]));
solve maximize objective;

output ["{\"transplants\": [",
        join(", ", ["[" ++ join(", ", [show(transplants[i, j]) | j in Person]) ++ "]" | i in Person]),
        "]}"];
