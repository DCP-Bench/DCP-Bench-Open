You have a number of bowls, all placed in a line at exact intervals of 1 meter -> bowls numbered 1..n, occupied Bool occ[i] per bowl
You also have a number of oranges; place all the oranges in the bowls, no more than one orange in each bowl -> one-hot pos[k][i] for the k-th orange at bowl i; sum over i == 1 per k; occ[i] <-> OR_k pos[k][i] (each bowl holds at most one by the strict ordering)
no three oranges A, B, C such that the distance between A and B is equal to the distance between B and C -> for each bowl i and step d >= 1 with i+2d <= n: not (occ[i] and occ[i+d] and occ[i+2d])
Print the bowls in which the oranges are placed, in ascending order (x) -> X_k = sum(i * pos[k][i]); X_k + 1 <= X_{k+1} for consecutive k; outputs x = [X_k]
objective: satisfaction
