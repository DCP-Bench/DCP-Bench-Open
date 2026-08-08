
include "globals.mzn";

% Define word indices 0..14
set of int: WORDS = 0..14;

% Length of each word in the sorted list
int: wordLen[WORDS] = 
  [5, 5, 5, 5, 5, 4, 4, 4, 4, 4, 3, 3, 3, 3, 3];

% Letter codes A=1..Z=26, padded with 0 for unused positions
array[WORDS, 1..5] of int: letters = 
  array2d(WORDS, 1..5, [
    % HOSES    LASER    SAILS    SHEET    STEER
      8,15,19, 5,19,  12, 1,19, 5,18,  19, 1, 9,12,19,  19, 8, 5, 5,20,  19,20, 5, 5,18,
    % HEEL     HIKE     KEEL     KNOT     LINE
      8, 5, 5,12, 0,   8, 9,11, 5, 0,    11, 5, 5,12, 0,   11,14,15,20, 0,   12, 9,14, 5, 0,
    % AFT      ALE      EEL      LEE      TIE
      1, 6,20, 0, 0,    1,12, 5, 0, 0,    5, 5,12, 0, 0,     12, 5, 5, 0, 0,   20, 9, 5, 0, 0
  ]);

% Slot lengths for slots 1..8
array[1..8] of int: slotLen = [5, 5, 5, 4, 4, 3, 3, 5];

% Decision variables: which word index is placed in slot s
array[1..8] of var WORDS: E;

% Each slot must get a word of matching length
constraint
  forall(s in 1..8) (
    wordLen[E[s]] = slotLen[s]
  );

% All chosen words must be distinct
constraint
  all_different(E);

% Letter-matching constraints at intersections:
% slot1 p3 = slot2 p1
constraint letters[E[1],3] = letters[E[2],1];
% slot1 p5 = slot3 p1
constraint letters[E[1],5] = letters[E[3],1];
% slot4 p2 = slot2 p3
constraint letters[E[4],2] = letters[E[2],3];
% slot4 p3 = slot5 p1
constraint letters[E[4],3] = letters[E[5],1];
% slot4 p4 = slot3 p3
constraint letters[E[4],4] = letters[E[3],3];
% slot7 p1 = slot2 p4
constraint letters[E[7],1] = letters[E[2],4];
% slot7 p2 = slot5 p2
constraint letters[E[7],2] = letters[E[5],2];
% slot7 p3 = slot3 p4
constraint letters[E[7],3] = letters[E[3],4];
% slot8 p1 = slot6 p2
constraint letters[E[8],1] = letters[E[6],2];
% slot8 p3 = slot2 p5
constraint letters[E[8],3] = letters[E[2],5];
% slot8 p4 = slot5 p3
constraint letters[E[8],4] = letters[E[5],3];
% slot8 p5 = slot3 p5
constraint letters[E[8],5] = letters[E[3],5];

solve satisfy;

output [
  "{",
    "\"E\": [" ++ join(",", [show(E[i]) | i in 1..8]) ++ "]",
  "}"
];
