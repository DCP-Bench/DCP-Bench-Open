% Word design for DNA computing: find num_words words of length n over the
% alphabet {A, C, G, T} that are far enough apart from each other, and from
% each other's reversed Watson-Crick complements, to avoid mismatched hybridisation.
include "globals.mzn";

int: n;          % length of each word
int: num_words;  % how many words to find

% The letters are coded 1 = A, 2 = C, 3 = G, 4 = T, as in the printed output.
int: A = 1;
int: C = 2;
int: G = 3;
int: T = 4;

% The problem fixes both numbers below: every word has 4 letters from {C, G},
% and the required Hamming distances are at least 4 (constants of the problem, not the instance).
int: n_cg = 4;
int: min_distance = 4;

set of int: WordIds = 1..num_words;
set of int: Positions = 1..n;

% words[i, j] = the j-th letter of the i-th word
array[WordIds, Positions] of var A..T: words;

% each word has exactly 4 letters from {C, G}
constraint forall(i in WordIds)
    (sum(j in Positions) (bool2int(words[i, j] = C \/ words[i, j] = G)) = n_cg);

% two distinct words differ in at least 4 positions
constraint forall(x, y in WordIds where x < y)
    (sum(j in Positions) (bool2int(words[x, j] != words[y, j])) >= min_distance);

% For every pair of words x and y (x and y may be the same word), x read
% backwards and the Watson-Crick complement of y (A <-> T, C <-> G, which is 5 minus
% the code) differ in at least 4 positions.
constraint forall(x, y in WordIds)
    (sum(j in Positions) (bool2int(words[x, n + 1 - j] != 5 - words[y, j])) >= min_distance);

solve satisfy;

output ["{\"words\": [",
        join(", ", ["[" ++ join(", ", [show(words[i, j]) | j in Positions]) ++ "]" | i in WordIds]),
        "]}"];
