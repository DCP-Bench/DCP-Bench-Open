% coins_grid: place coins on an n by n grid (n from the instance).
% Each row holds exactly c coins (c from the instance), each column holds exactly c coins,
% and each cell holds at most one coin. Minimise the sum, over all cells that contain a
% coin, of the quadratic horizontal distance from the main diagonal, (row - column)^2.
% Output x: 0/1 per cell (1 = coin placed); output z: the sum above.

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
    ( for(J, 1, N), param(Rows, N, C) do
        ( foreach(R2, Rows), foreach(X2, Col), param(J) do
            nth1(J, R2, X2)
        ),
        sum(Col) #= C
    ),

    % the sum of the quadratic horizontal distance from the main diagonal of all
    % cells containing a coin is z; z is minimised
    Max is N * C * (N - 1) * (N - 1),
    Z :: 0..Max,
    ( multifor([I, J3], 1, [N, N]), foreach(T, Ts), param(Rows) do
        nth1(I, Rows, RI),
        nth1(J3, RI, X3),
        Sq is (I - J3) * (I - J3),
        T #= X3 * Sq
    ),
    Z #= sum(Ts).
