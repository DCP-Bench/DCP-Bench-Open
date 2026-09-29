% Flip rows and columns (Einav's puzzle): choose, for every row and column,
% whether to flip its sign so that every row sum and every column sum is
% non-negative, with the smallest possible total of the whole matrix.
% input_matrix(I, J, V): the value in row I and column J.
row(I) :- input_matrix(I,_,_).
col(J) :- input_matrix(_,J,_).
sign(-1;1).

% row_signs(I, S), col_signs(J, S): the sign chosen for a row and for a column, -1 or +1.
1 { row_signs(I,S) : sign(S) } 1 :- row(I).
1 { col_signs(J,S) : sign(S) } 1 :- col(J).

% cell(I, J, X): the value of cell (I, J) once its row and its column are flipped.
cell(I,J,V * RS * CS) :- input_matrix(I,J,V), row_signs(I,RS), col_signs(J,CS).

% Every row and every column sums to at least 0 (the reference declares a sum to lie
% in 0..300, which is mirrored here).
:- row(I), #sum { X,J : cell(I,J,X) } < 0.
:- row(I), #sum { X,J : cell(I,J,X) } > 300.
:- col(J), #sum { X,I : cell(I,J,X) } < 0.
:- col(J), #sum { X,I : cell(I,J,X) } > 300.

% The total of the matrix lies in the declared range 0..1000, and it is minimised.
total(T) :- T = #sum { X,I,J : cell(I,J,X) }.
:- total(T), T < 0.
:- total(T), T > 1000.
#minimize { T : total(T) }.

#show row_signs/2.
#show col_signs/2.
