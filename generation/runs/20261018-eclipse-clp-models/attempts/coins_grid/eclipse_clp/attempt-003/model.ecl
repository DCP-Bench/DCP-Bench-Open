% coins_grid: place coins on an n by n grid (n from the instance).
% Each row holds exactly c coins (c from the instance), each column holds exactly c coins,
% and each cell holds at most one coin. Minimise the sum, over all cells that contain a
% coin, of the quadratic horizontal distance from the main diagonal, (row - column)^2.
% Output x: 0/1 per cell (1 = coin placed); output z: the sum above.
%
% Encoding notes (not part of the problem): the cost is written once per row and once per
% column, both summing to z. Each row cost and column cost has a lower bound equal to the
% sum of the c smallest distances available in that row or column; these bounds are implied
% by the problem and only make the proof of optimality faster. The search labels the cells
% row by row, so each finished row fixes its cost and tightens the bound on the rest; a coin
% is tried before no coin.

:- lib(ic).
:- lib(listut).

model(Instance, Vars, [x-Rows, z-Z], min(Z)) :-
    memberchk(n-N, Instance),
    memberchk(c-C, Instance),

    % the grid: one 0/1 variable per cell, at most one coin per cell
    length(Rows, N),
    ( foreach(R0, Rows), param(N) do
        length(R0, N),
        R0 :: 0..1
    ),
    flatten(Rows, Vars),

    % in each row exactly c coins must be placed
    ( foreach(R1, Rows), param(C) do
        sum(R1) #= C
    ),

    % in each column exactly c coins must be placed
    ( for(J, 1, N), param(Rows, C) do
        ( foreach(R2, Rows), foreach(X2, Col), param(J) do
            nth1(J, R2, X2)
        ),
        sum(Col) #= C
    ),

    % the sum of the quadratic horizontal distance from the main diagonal of all
    % cells containing a coin is z; z is minimised. The cost is summed by row ...
    Max is N * C * (N - 1) * (N - 1),
    Z :: 0..Max,
    ( for(I, 1, N), foreach(RowCost, RowCosts), param(Rows, N, C) do
        nth1(I, Rows, RI),
        ( for(J1, 1, N), foreach(T1, Ts1), param(RI, I) do
            nth1(J1, RI, X1),
            Sq1 is (I - J1) * (I - J1),
            T1 #= X1 * Sq1
        ),
        % a row with c coins costs at least the c smallest distances in that row
        ( for(J2, 1, N), foreach(D2, Ds2), param(I) do
            D2 is (I - J2) * (I - J2)
        ),
        msort(Ds2, Sorted2),
        length(Small2, C),
        append(Small2, _, Sorted2),
        ( foreach(S2, Small2), fromto(0, A2, B2, LB2) do
            B2 is A2 + S2
        ),
        RowCost #>= LB2,
        RowCost #= sum(Ts1)
    ),
    Z #= sum(RowCosts),

    % ... and by column, which gives the same total
    ( for(J, 1, N), foreach(ColCost, ColCosts), param(Rows, N, C) do
        ( for(I3, 1, N), foreach(T3, Ts3), param(Rows, J) do
            nth1(I3, Rows, RI3),
            nth1(J, RI3, X3),
            Sq3 is (I3 - J) * (I3 - J),
            T3 #= X3 * Sq3
        ),
        % a column with c coins costs at least the c smallest distances in that column
        ( for(I4, 1, N), foreach(D4, Ds4), param(J) do
            D4 is (I4 - J) * (I4 - J)
        ),
        msort(Ds4, Sorted4),
        length(Small4, C),
        append(Small4, _, Sorted4),
        ( foreach(S4, Small4), fromto(0, A4, B4, LB4) do
            B4 is A4 + S4
        ),
        ColCost #>= LB4,
        ColCost #= sum(Ts3)
    ),
    Z #= sum(ColCosts).

% label the cells row by row (Vars is row-major), trying a coin before no coin
search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_max, complete, []).
