include "globals.mzn";

% We have two unknown ages: m (my age) and h (husband's age)
% Both are positive integers, let's assume a reasonable range for ages
int: min_age = 1;
int: max_age = 120;

var min_age..max_age: m;
var min_age..max_age: h;

% The four operations to apply in some order:
% +2, /8, -3, *7
% We apply all four operations exactly once in some order to m to get h
% and apply all four operations exactly once in some order to h to get m

% We model the operations as functions:
% Since division by 8 must result in an integer, we enforce integer division with no remainder

% We represent the operations as a list of functions and their inverses:
% But since order matters, we will try all permutations of the operations applied to m and h

% Define the operations as identifiers
enum OPERATIONS = {op_add2, op_div8, op_sub3, op_mul7};

% All permutations of the 4 operations
array[1..24, 1..4] of OPERATIONS: all_perms = [
    % generated all permutations of [op_add2, op_div8, op_sub3, op_mul7]
    % For brevity, we list them explicitly:
    [op_add2, op_div8, op_sub3, op_mul7],
    [op_add2, op_div8, op_mul7, op_sub3],
    [op_add2, op_sub3, op_div8, op_mul7],
    [op_add2, op_sub3, op_mul7, op_div8],
    [op_add2, op_mul7, op_div8, op_sub3],
    [op_add2, op_mul7, op_sub3, op_div8],
    [op_div8, op_add2, op_sub3, op_mul7],
    [op_div8, op_add2, op_mul7, op_sub3],
    [op_div8, op_sub3, op_add2, op_mul7],
    [op_div8, op_sub3, op_mul7, op_add2],
    [op_div8, op_mul7, op_add2, op_sub3],
    [op_div8, op_mul7, op_sub3, op_add2],
    [op_sub3, op_add2, op_div8, op_mul7],
    [op_sub3, op_add2, op_mul7, op_div8],
    [op_sub3, op_div8, op_add2, op_mul7],
    [op_sub3, op_div8, op_mul7, op_add2],
    [op_sub3, op_mul7, op_add2, op_div8],
    [op_sub3, op_mul7, op_div8, op_add2],
    [op_mul7, op_add2, op_div8, op_sub3],
    [op_mul7, op_add2, op_sub3, op_div8],
    [op_mul7, op_div8, op_add2, op_sub3],
    [op_mul7, op_div8, op_sub3, op_add2],
    [op_mul7, op_sub3, op_add2, op_div8],
    [op_mul7, op_sub3, op_div8, op_add2]
];

% Function to apply one operation to a value, returns -1 if invalid (e.g. division not exact)
function var int: apply_op(var int: x, OPERATIONS: op) =
    if op = op_add2 then x + 2
    else if op = op_div8 then
        if x mod 8 = 0 then x div 8 else -1 endif
    else if op = op_sub3 then x - 3
    else if op = op_mul7 then x * 7
    else -1 endif endif endif endif;

% Function to apply a sequence of operations to a value
function var int: apply_ops(var int: x, array[int] of OPERATIONS: ops) =
    let {
        var int: r1 = apply_op(x, ops[1]),
        var int: r2 = if r1 >= 0 then apply_op(r1, ops[2]) else -1 endif,
        var int: r3 = if r2 >= 0 then apply_op(r2, ops[3]) else -1 endif,
        var int: r4 = if r3 >= 0 then apply_op(r3, ops[4]) else -1 endif
    } in r4;

% We want to find m, h, and two permutations p1 and p2 such that:
% apply_ops(m, p1) = h
% apply_ops(h, p2) = m
% p1 != p2 (different order)

var 1..24: p1;
var 1..24: p2;

constraint p1 != p2;

constraint
    let {
        var int: res1 = apply_ops(m, all_perms[p1]),
        var int: res2 = apply_ops(h, all_perms[p2])
    } in
    res1 = h /\ res2 = m /\
    m >= min_age /\ m <= max_age /\
    h >= min_age /\ h <= max_age /\
    res1 >= min_age /\ res1 <= max_age /\
    res2 >= min_age /\ res2 <= max_age;

solve satisfy;

output [
    "{",
    "\"m\": ", show(m), ",",
    "\"h\": ", show(h),
    "}"
];