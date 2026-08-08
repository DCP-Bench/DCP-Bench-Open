include "globals.mzn";

% Letters involved (excluding Q and Z)
% Alphabet letters except Q and Z: 24 letters total
% Letters appearing in the words:
% BAKE ONYX ECHO OVAL
% GIRD SMUG JUMP TORN
% LUCK VINY LUSH WRAP

% Extract unique letters from all words:
% Letters: A B C D E G H I J K L M N O P R S T U V W X Y
% Total 24 letters

% Map letters to indices 1..24
enum LETTERS = {A,B,C,D,E,G,H,I,J,K,L,M,N,O,P,R,S,T,U,V,W,X,Y};

int: num_letters = 24;
int: num_blocks = 4;
int: faces_per_block = 6;

% Words to be spelled
array[1..12] of array[int] of LETTERS: words = [
    [B,A,K,E],
    [O,N,Y,X],
    [E,C,H,O],
    [O,V,A,L],
    [G,I,R,D],
    [S,M,U,G],
    [J,U,M,P],
    [T,O,R,N],
    [L,U,C,K],
    [V,I,N,Y],
    [L,U,S,H],
    [W,R,A,P]
];

% Decision variables:
% For each letter, which block it is assigned to (0..3)
array[LETTERS] of var 0..3: dice;

% Each block has exactly 6 letters
constraint
    forall(b in 0..3) (
        sum([bool2int(dice[l] == b) | l in LETTERS]) == faces_per_block
    );

% For each word, the letters must be on distinct blocks (one letter per block)
constraint
    forall(w in 1..12) (
        alldifferent([dice[l] | l in words[w]])
    );

solve satisfy;

output [
    "{",
    join(",", [show(dice[l]) | l in LETTERS]),
    "}"
];