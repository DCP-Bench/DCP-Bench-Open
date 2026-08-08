
% Nonogram solver

include "globals.mzn";

% Input data
int: rows = 8;
int: cols = 13;
int: row_rule_len = 2;
array[1..rows, 1..row_rule_len] of int: row_rules = 
  [| 0,1,
     0,2,
     4,4,
     0,12,
     0,8,
     0,9,
     3,4,
     2,2 |];
int: col_rule_len = 2;
array[1..cols, 1..col_rule_len] of int: col_rules = 
  [| 0,2,
     2,1,
     3,2,
     0,6,
     1,4,
     0,3,
     0,4,
     0,4,
     0,4,
     0,5,
     0,4,
     1,3,
     0,2 |];

% Decision variables
% sr[i,k]: start column of k-th block in row i (0 if unused)
array[1..rows, 1..row_rule_len] of var 0..cols: sr;
% sc[j,k]: start row of k-th block in column j (0 if unused)
array[1..cols, 1..col_rule_len] of var 0..rows: sc;
% board[r,c]: 1 if cell (r,c) is shaded, else 0
array[1..rows, 1..cols] of var 0..1: board;
% br[i,k,c]: true if row-block k of row i covers column c
array[1..rows, 1..row_rule_len, 1..cols] of var bool: br;
% bc[j,k,r]: true if col-block k of column j covers row r
array[1..cols, 1..col_rule_len, 1..rows] of var bool: bc;

% Row block start constraints
constraint
  forall(i in 1..rows, k in 1..row_rule_len) (
    if row_rules[i,k] > 0 then
      sr[i,k] >= 1 /\
      sr[i,k] <= cols - row_rules[i,k] + 1
    else
      sr[i,k] = 0
    endif
  );

% Enforce ordering and separation of row blocks
constraint
  forall(i in 1..rows, k in 2..row_rule_len) (
    sr[i,k] >= sr[i,k-1] + row_rules[i,k-1] + 1
  );

% Link row-block coverage to board
constraint
  forall(i in 1..rows, k in 1..row_rule_len, c in 1..cols) (
    br[i,k,c] <-> 
      (row_rules[i,k] > 0 /\ sr[i,k] <= c /\ c <= sr[i,k] + row_rules[i,k] - 1)
  );

constraint
  forall(i in 1..rows, c in 1..cols) (
    board[i,c] = sum(k in 1..row_rule_len)(bool2int(br[i,k,c]))
  );

% Column block start constraints
constraint
  forall(j in 1..cols, k in 1..col_rule_len) (
    if col_rules[j,k] > 0 then
      sc[j,k] >= 1 /\
      sc[j,k] <= rows - col_rules[j,k] + 1
    else
      sc[j,k] = 0
    endif
  );

% Enforce ordering and separation of column blocks
constraint
  forall(j in 1..cols, k in 2..col_rule_len) (
    sc[j,k] >= sc[j,k-1] + col_rules[j,k-1] + 1
  );

% Link col-block coverage to board
constraint
  forall(j in 1..cols, k in 1..col_rule_len, r in 1..rows) (
    bc[j,k,r] <-> 
      (col_rules[j,k] > 0 /\ sc[j,k] <= r /\ r <= sc[j,k] + col_rules[j,k] - 1)
  );

constraint
  forall(r in 1..rows, j in 1..cols) (
    board[r,j] = sum(k in 1..col_rule_len)(bool2int(bc[j,k,r]))
  );

solve satisfy;

% Output in JSON format
output [
  "{",
  "\"board\": [",
  concat([
    "[" ++ join(",", [ show(board[i,j]) | j in 1..cols ]) ++ "]"
    ++ if i < rows then "," else "" endif
    | i in 1..rows
  ]),
  "]",
  "}"
];
