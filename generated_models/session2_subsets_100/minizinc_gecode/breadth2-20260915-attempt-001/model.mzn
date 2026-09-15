include "globals.mzn";

array[int] of int: A;

set of int: Items = index_set(A);
array[Items] of var bool: in_S;
array[Items] of var bool: in_T;

constraint sum(i in Items) (A[i] * bool2int(in_S[i]))
         = sum(i in Items) (A[i] * bool2int(in_T[i]));
% No element lies in both subsets.
constraint forall(i in Items) (not (in_S[i] /\ in_T[i]));
constraint sum(i in Items) (bool2int(in_S[i])) > 0;
constraint sum(i in Items) (bool2int(in_T[i])) > 0;

solve satisfy;

output ["{\"in_S\": [", join(", ", [show(in_S[i]) | i in Items]),
        "], \"in_T\": [", join(", ", [show(in_T[i]) | i in Items]), "]}"];
