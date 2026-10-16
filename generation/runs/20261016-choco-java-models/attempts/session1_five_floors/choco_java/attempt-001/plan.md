five people live on the first five floors -> B, C, F, M, S in 1..5
they all live on different floors -> allDifferent(B, C, F, M, S)
Baker does not live on the fifth floor -> B != 5
Cooper does not live on the first floor -> C != 1
Fletcher does not live on either the fifth or the first floor -> F != 1, F != 5
Miller lives on a higher floor than does Cooper -> M > C
Smith does not live on a floor adjacent to Fletcher -> |S - F| != 1
Fletcher does not live on a floor adjacent to Cooper -> |F - C| != 1
objective: none (satisfaction); outputs B, C, F, M, S
