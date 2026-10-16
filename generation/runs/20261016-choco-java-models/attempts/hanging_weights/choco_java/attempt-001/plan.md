Each weight is an integer between 1 and 13 -> IntVar with domain 1..13 for A..M
the weights on either side of a pivot must be equal when weighted by distance -> one scalar equation per bar, distances in units of three columns
a bar hanging beneath another contributes its total weight -> m.sum over the bar's weights and its sub-bars
bottom right bar: 5*C = D -> scalar(C, D; 5, -1) = 0
bar above it: 3*G = 2*(C+D) -> scalar(G, CD; 3, -2) = 0
bar with A and B: 4*A = B (B is 4 units from the pivot, A is 1 unit) -> scalar(A, B; 4, -1) = 0
bar with E and F: 3*E = 2*F -> scalar(E, F; 3, -2) = 0
bar with H and I, hung from the bar with L, M: 3*H = 3*I + 2*(E+F) -> scalar(H, I, EF; 3, -3, -2) = 0
bar with L and M: (H+I+E+F) = L + 4*M -> scalar(X, L, M; 1, -1, -4) = 0
right bar under the top bar: 3*(A+B) + 2*J = K + 2*(G+C+D) -> scalar(AB, J, K, GBtot; 3, 2, -1, -2) = 0
top bar: 4 * (weight of the left bar) = 3 * (weight of the right bar) -> scalar(left, right; 4, -3) = 0
objective: none, satisfaction problem; outputs a..m are the weights of A..M
