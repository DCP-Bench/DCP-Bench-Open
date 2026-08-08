include "globals.mzn";

% Input data
int: rows = 8;
int: row_rule_len = 2;
array[1..rows, 1..row_rule_len] of int: row_rules = [
    | 0, 1
    | 0, 2
    | 4, 4
    | 0, 12
    | 0, 8
    | 0, 9
    | 3, 4
    | 2, 2
];
int: cols = 13;
int: col_rule_len = 2;
array[1..cols, 1..col_rule_len] of int: col_rules = [
    | 0, 2
    | 2, 1
    | 3, 2
    | 0, 6
    | 1, 4
    | 0, 3
    | 0, 4
    | 0, 4
    | 0, 4
    | 0, 5
    | 0, 4
    | 1, 3
    | 0, 2
];

% Decision variables: board[row, col] = 1 if shaded, 0 otherwise
array[1..rows, 1..cols] of var 0..1: board;

% Helper function to check if a sequence of blocks matches the rule
% We model the row/column as a sequence of 0/1 and want to check if the blocks of 1's match the rule.
% We will extract the blocks of consecutive 1's and compare with the rule ignoring zeros in the rule.

% Extract blocks of consecutive 1's from a line (array of 0/1)
function array[int] of var int: extract_blocks(array[int] of var 0..1: line) =
    let {
        int: n = length(line),
        array[1..n] of var int: block_lengths = [0 | i in 1..n],
        array[1..n] of var bool: start_block = [false | i in 1..n],
        array[1..n] of var bool: end_block = [false | i in 1..n]
    } in
    % start_block[i] = true if line[i] = 1 and (i=1 or line[i-1] = 0)
    % end_block[i] = true if line[i] = 1 and (i=n or line[i+1] = 0)
    % block_lengths[i] = length of block starting at i if start_block[i] = true, else 0
    % We will collect block lengths in order
    let {
        % Define start_block and end_block
        array[1..n] of var bool: s_block = [line[i] = 1 /\ (i = 1 \/ line[i-1] = 0) | i in 1..n],
        array[1..n] of var bool: e_block = [line[i] = 1 /\ (i = n \/ line[i+1] = 0) | i in 1..n]
    } in
    let {
        % For each start_block position, compute block length by counting consecutive 1's
        array[1..n] of var int: lengths = [
            if s_block[i] then
                sum([line[j] | j in i..n where forall(k in i..j-1)(line[k] = 1) /\ (j = n \/ line[j+1] = 0)])
            else 0
            | i in 1..n
        ]
    } in
    % Collect block lengths in order, ignoring zeros
    [lengths[i] | i in 1..n where s_block[i]];

% We cannot use functions with var arrays easily, so we implement block extraction with constraints.

% Instead, we implement a predicate to constrain a line to match a rule.

predicate match_rule(array[int] of var 0..1: line, array[int] of int: rule) =
    let {
        int: n = length(line),
        int: rlen = length(rule),
        % Number of blocks in rule ignoring zeros
        int: num_blocks = sum([if rule[i] > 0 then 1 else 0 endif | i in 1..rlen])
    } in
    % We create arrays for block starts and lengths
    % block_starts[b] = start index of block b in line (1-based)
    % block_lengths[b] = length of block b
    % We enforce blocks are separated by at least one zero
    % The blocks must appear in order and match the rule lengths
    % If num_blocks = 0, then line must be all zeros
    if num_blocks = 0 then
        forall(i in 1..n)(line[i] = 0)
    else
        let {
            array[1..num_blocks] of var 1..n: block_starts,
            array[1..num_blocks] of var int: block_lengths,
            % block_ends[b] = block_starts[b] + block_lengths[b] - 1
            array[1..num_blocks] of var 1..n: block_ends
        } in
        % Constraints on blocks
        % block_lengths[b] = rule length of b-th nonzero block in rule
        % We map rule blocks to block_lengths in order
        % Extract nonzero blocks from rule
        array[1..num_blocks] of int: rule_blocks = [rule[i] | i in 1..rlen where rule[i] > 0];
        % block_lengths fixed to rule_blocks
        forall(b in 1..num_blocks)(block_lengths[b] = rule_blocks[b]) /\
        % block_ends[b] = block_starts[b] + block_lengths[b] - 1
        forall(b in 1..num_blocks)(block_ends[b] = block_starts[b] + block_lengths[b] - 1) /\
        % blocks are within line
        forall(b in 1..num_blocks)(block_ends[b] <= n) /\
        % blocks are ordered and separated by at least one zero
        forall(b in 1..num_blocks-1)(block_ends[b] + 1 < block_starts[b+1]) /\
        % blocks do not overlap and are consecutive 1's
        forall(b in 1..num_blocks)(
            forall(i in block_starts[b]..block_ends[b])(line[i] = 1)
        ) /\
        % outside blocks, line is zero
        forall(i in 1..n)(
            let {
                var bool: in_any_block = exists(b in 1..num_blocks)(i >= block_starts[b] /\ i <= block_ends[b])
            } in
            (in_any_block -> line[i] = 1) /\ (not in_any_block -> line[i] = 0)
        )
    endif;

% Constraints for all rows
constraint
    forall(r in 1..rows)(
        match_rule([board[r,c] | c in 1..cols], row_rules[r])
    );

% Constraints for all columns
constraint
    forall(c in 1..cols)(
        match_rule([board[r,c] | r in 1..rows], col_rules[c])
    );

solve satisfy;

output [
    "{",
    "\"board\": [",
    concat([
        "[" ++ join(",", [show(board[r,c]) | c in 1..cols]) ++ "]" ++ if r < rows then "," else "" endif
        | r in 1..rows
    ]),
    "]",
    "}"
];