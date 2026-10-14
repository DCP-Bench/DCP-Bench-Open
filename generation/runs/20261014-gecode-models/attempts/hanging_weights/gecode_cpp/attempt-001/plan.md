Reading of the diagram (3 characters = 1 unit of bar length; a bar's pivot is the point where its string hangs):
top bar: pivot 4 units from left end, left arm LM (4 units), right arm Q (3 units).
LM bar: pivot at its left plug; P hangs 1 unit left, L 1 unit right, M 4 units right.
P bar: pivot at its midpoint; H 3 units left, I 3 units right, EF bar 2 units right.
EF bar: pivot 3 units right of E, F 2 units right of pivot.
Q bar: AB bar 3 units left, J 2 units left, K 1 unit right, G bar 2 units right.
AB bar: A 4 units left of pivot, B 1 unit right.
G bar: G 3 units left of pivot, C+D bar 2 units right.
C+D bar: C 5 units left of pivot, D 1 unit right.
Requirement lines:
the bar on the bottom right must have 5*C=D -> rel(5*C == D)
the bar above it must have 3*G=2*(C+D) -> rel(3*G == 2*C + 2*D)
the bottom-left bar: 4*A=B -> rel(4*A == B)
the bar with E and F: 3*E=2*F -> rel(3*E == 2*F)
the bar with H, I and the E-F bar: 3*H = 3*I + 2*(E+F) -> rel(3*H == 3*I + 2*E + 2*F)
the bar with L, M and the P subtree: (H+I+E+F) = L + 4*M -> rel(H+I+E+F == L + 4*M)
the top bar: 4*(L+M+H+I+E+F) = 3*(A+B+J+K+G+C+D) -> rel
the bar with J, K, AB and G: 3*(A+B) + 2*J = K + 2*(G+C+D) -> rel
Branching: all 13 weights, first fail, min value. Objective: none (satisfaction).
