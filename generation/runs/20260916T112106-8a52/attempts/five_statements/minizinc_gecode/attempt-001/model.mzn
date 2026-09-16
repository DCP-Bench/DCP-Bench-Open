% Five self-referential statements, the i-th claiming that exactly i of them
% are false.
array[1..5] of var bool: statements;

constraint forall(i in 1..5) (
    statements[i] <-> (sum(j in 1..5) (bool2int(not statements[j])) = i)
);

solve satisfy;

output ["{\"statements\": [",
        join(", ", [show(statements[i]) | i in 1..5]), "]}"];
