include "globals.mzn";

% Problem parameters
int: n = 8; % Number of words to find
int: len = 8; % Length of each word
set of int: POS = 1..len;

% Alphabet encoding: A=1, C=2, G=3, T=4
% Complement mapping: A<->T, C<->G
array[1..4] of int: complement = [4, 3, 2, 1];

% Decision variables: words[w,p] in 1..4 representing the letter at position p of word w
array[1..n, POS] of var 1..4: words;

% Constraint 1: Each word has exactly 4 symbols from {C=2, G=3}
constraint
  forall(w in 1..n) (
    sum(p in POS)(bool2int(words[w,p] == 2 \/ words[w,p] == 3)) == 4
  );

% Helper function: Hamming distance between two words
function var int: hamming_distance(array[int] of var int: x, array[int] of var int: y) =
  sum(i in index_set(x)) (bool2int(x[i] != y[i]));

% Compute reverse of a word
function array[int] of var int: reverse_word(array[int] of var int: x) =
  [ x[len - i + 1] | i in 1..len ];

% Compute complement of a word
function array[int] of var int: complement_word(array[int] of var int: x) =
  [ complement[x[i]] | i in 1..len ];

% Constraint 2: Each pair of distinct words differ in at least 4 positions
constraint
  forall(i,j in 1..n where i < j) (
    hamming_distance(words[i,], words[j,]) >= 4
  );

% Constraint 3: For each pair of words x,y (including x=y),
% the reverse of x and complement of y differ in at least 4 positions
constraint
  forall(i,j in 1..n) (
    let {
      array[int] of var int: rev_x = reverse_word(words[i,]),
      array[int] of var int: comp_y = complement_word(words[j,])
    } in
      hamming_distance(rev_x, comp_y) >= 4
  );

solve satisfy;

% Convert integer letter to char
function string: letter_to_char(int: l) =
  if l == 1 then "A"
  elseif l == 2 then "C"
  elseif l == 3 then "G"
  else "T"
  endif;

% Output the set of words as list of strings
output [
  "{\n",
  "  \"words\": [",
  join(",\n", [
    "\"" ++ concat([letter_to_char(fix(words[w,p])) | p in POS]) ++ "\""
    | w in 1..n
  ]),
  "]\n",
  "}"
];