% Nonogram: shade squares of a grid so that the runs of shaded squares in each
% row and each column have exactly the lengths listed in that line's rule, in
% that order, with at least one unshaded square between two runs.
include "globals.mzn";

int: rows;
int: cols;
int: row_rule_len;  % width of the padded row rules
int: col_rule_len;  % width of the padded column rules
array[1..rows, 1..row_rule_len] of int: row_rules;  % run lengths of each row; 0 is padding
array[1..cols, 1..col_rule_len] of int: col_rules;  % run lengths of each column; 0 is padding

% board[r, c] = 1 if the square is shaded, 0 otherwise
array[1..rows, 1..cols] of var 0..1: board;

% A line obeys its rule when the sequence of squares is accepted by a finite
% automaton that reads the runs in order. The automaton has one state per
% position in "run 1, gap, run 2, gap, ..., run k, trailing gap":
%   - the state where run k may start loops on an unshaded square (waiting
%     for the run) and moves on when it reads a shaded square;
%   - inside a run only shaded squares are allowed;
%   - after a run exactly one unshaded square must follow, and it leads to
%     the start state of the next run;
%   - after the last run, any number of unshaded squares may follow.
% Rule entries equal to 0 are padding and are ignored. States are numbered
% from 1 and the symbols are 1 = unshaded, 2 = shaded; a transition to 0 is a failure.
predicate line_matches_rule(array[int] of var int: line, array[int] of int: rule) =
    let {
        array[int] of int: runs = [rule[k] | k in index_set(rule) where rule[k] > 0];
        int: nr = length(runs);                        % number of runs
        int: last = sum(runs) + nr;                    % number of the last state (states are 0..last)
        % first state of run k, counted from 0: all earlier runs plus a mandatory gap after each
        array[1..nr] of int: first = [sum(j in 1..k - 1) (runs[j] + 1) | k in 1..nr];
        % what an unshaded / shaded square leads to from each state (0 = not allowed)
        array[0..last] of int: on_unshaded = array1d(0..last,
            [ if s = last then s + 1
              elseif exists(k in 1..nr) (s = first[k]) then s + 1
              elseif exists(k in 1..nr) (s = first[k] + runs[k]) then s + 2
              else 0 endif | s in 0..last ]);
        array[0..last] of int: on_shaded = array1d(0..last,
            [ if exists(k in 1..nr) (s >= first[k] /\ s < first[k] + runs[k]) then s + 2 else 0 endif | s in 0..last ]);
        array[1..last + 1, 1..2] of int: transitions =
            array2d(1..last + 1, 1..2, [ if sym = 1 then on_unshaded[s] else on_shaded[s] endif | s in 0..last, sym in 1..2 ]);
        % accepting: the state after the last run (or its trailing gap); with
        % no runs at all the single state, which only accepts unshaded squares
        set of int: accepting = if nr = 0 then {1} else {last, last + 1} endif;
    } in regular([line[i] + 1 | i in index_set(line)], last + 1, 2, transitions, 1, accepting);

% the shaded runs in each row match the row's rule
constraint forall(r in 1..rows) (line_matches_rule([board[r, c] | c in 1..cols], [row_rules[r, k] | k in 1..row_rule_len]));

% the shaded runs in each column match the column's rule
constraint forall(c in 1..cols) (line_matches_rule([board[r, c] | r in 1..rows], [col_rules[c, k] | k in 1..col_rule_len]));

solve satisfy;

output ["{\"board\": [",
        join(", ", ["[" ++ join(", ", [show(board[r, c]) | c in 1..cols]) ++ "]" | r in 1..rows]),
        "]}"];
