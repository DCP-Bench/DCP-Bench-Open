At the hospital n people are on a waiting list -> people 0..n-1 (instance people 1..n), one Bool per ordered pair x[i][j] for "i donates to j" (n*n Bools)
compatible[i] is the set of people to which i can donate -> ~x[i][j] for every j not in compatible[i] (and for i == j); pairs in the list stay free
no person receives more than one kidney -> sum_i x[i][j] <= 1 per column j
anyone who gives a kidney must receive one -> sum_j x[i][j] <= 1 per row i, and sum_j x[i][j] - sum_k x[k][i] <= 0 (giving implies receiving)
Print the transplants as a list of lists, transplants[i][j] is 1 if person i donates to person j -> output transplants[i][j] = x[i][j] (Bool)
maximize the number of people that receive a new kidney -> objective: maximize sum of all x[i][j] (each receiver has exactly one incoming Bool set)
