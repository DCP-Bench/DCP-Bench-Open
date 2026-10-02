% Ternary Steiner problem (CSPLib 44): find n*(n-1)/6 triples of distinct
% elements from {1..n} such that any two triples have at most one element in
% common. It only exists when n mod 6 is 1 or 3. The answer is a boolean
% matrix with one row per triple and one column per element.

int: n;  % order of the Steiner triple system

constraint assert(n mod 6 = 1 \/ n mod 6 = 3, "n must be 1 or 3 modulo 6");

int: n_sets = n * (n - 1) div 6;  % number of triples
set of int: Triples = 1..n_sets;
set of int: Elements = 1..n;

% sets[i, j] = true iff element j is in triple i
array[Triples, Elements] of var bool: sets;

% every triple has exactly three elements
constraint forall(i in Triples) (sum(j in Elements) (bool2int(sets[i, j])) = 3);

% any two triples have at most one element in common
constraint forall(i1, i2 in Triples where i1 < i2)
    (sum(j in Elements) (bool2int(sets[i1, j] /\ sets[i2, j])) <= 1);

% Implied constraints (every solution satisfies them; they are added because
% Gecode cannot derive them and they prune much earlier). The n_sets triples
% hold 3 * n_sets = n*(n-1)/2 pairs of elements, which is every pair there is,
% and no pair can be in two triples, so each pair of elements lies in exactly
% one triple and each element is therefore in (n-1)/2 triples.
constraint forall(j1, j2 in Elements where j1 < j2)
    (sum(i in Triples) (bool2int(sets[i, j1] /\ sets[i, j2])) = 1);
constraint forall(j in Elements) (sum(i in Triples) (bool2int(sets[i, j])) = (n - 1) div 2);

solve satisfy;

output ["{\"sets\": [", join(", ", ["[" ++ join(", ", [show(sets[i, j]) | j in Elements]) ++ "]" | i in Triples]), "]}"];
