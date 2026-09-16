% Four numbers: find three values whose subsets sum to every given number.
array[int] of int: numbers;

set of int: Targets = index_set(numbers);
array[1..3] of var 1..10: x;
% tmp[i, j] says whether x[j] is part of the subset that makes numbers[i].
array[Targets, 1..3] of var bool: tmp;

constraint forall(i in Targets) (
    sum(j in 1..3) (bool2int(tmp[i, j]) * x[j]) = numbers[i]
);

solve satisfy;

output ["{\"x\": [", join(", ", [show(x[j]) | j in 1..3]), "]}"];
