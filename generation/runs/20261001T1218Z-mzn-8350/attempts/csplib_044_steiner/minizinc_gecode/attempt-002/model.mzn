% Ternary Steiner problem (CSPLib 44): find n*(n-1)/6 triples of distinct
% elements from {1..n} such that any two triples have at most one element in
% common. It only exists when n mod 6 is 1 or 3. The answer is a boolean
% matrix with one row per triple and one column per element.
include "globals.mzn";

int: n;  % order of the Steiner triple system

constraint assert(n mod 6 = 1 \/ n mod 6 = 3, "n must be 1 or 3 modulo 6");

int: n_sets = n * (n - 1) div 6;  % number of triples
set of int: Triples = 1..n_sets;
set of int: Elements = 1..n;

% sets[i, j] = true iff element j is in triple i (the answer)
array[Triples, Elements] of var bool: sets;

% A triple is written down with its three elements in increasing order:
% member[i, 1] < member[i, 2] < member[i, 3]. The boolean row of the triple is
% read off from them, so each answer matrix has exactly one such writing, and
% the integer form lets the "at most one common element" condition be stated
% as a condition on pairs of elements, which Gecode propagates better than
% sums of products of booleans.
array[Triples, 1..3] of var Elements: member;
constraint forall(i in Triples) (member[i, 1] < member[i, 2] /\ member[i, 2] < member[i, 3]);

% every triple has exactly three elements: those of its row
constraint forall(i in Triples, j in Elements)
    (sets[i, j] <-> (member[i, 1] = j \/ member[i, 2] = j \/ member[i, 3] = j));

% Any two triples have at most one element in common, i.e. no pair of elements
% lies in two triples. A pair (a, b) with a < b is numbered (a - 1) * n + b;
% the three pairs of every triple must all have different numbers.
constraint all_different([ (member[i, a] - 1) * n + member[i, b] | i in Triples, a in 1..2, b in a + 1..3 ]);

% Implied constraint (every solution satisfies it; Gecode cannot derive it).
% The n_sets triples hold 3 * n_sets = n*(n-1)/2 pairs of elements, which is
% every pair there is, so each element x lies with each of the other n-1
% elements in exactly one triple, hence in (n-1)/2 triples.
constraint global_cardinality([member[i, a] | i in Triples, a in 1..3], [j | j in Elements],
                              [(n - 1) div 2 | j in Elements]);

solve satisfy;

output ["{\"sets\": [", join(", ", ["[" ++ join(", ", [show(sets[i, j]) | j in Elements]) ++ "]" | i in Triples]), "]}"];
