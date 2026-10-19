% KenKen puzzle on an N x N grid (N from the instance).
% Fill the grid with the digits 1..N such that:
%   - each row contains exactly one of each digit,
%   - each column contains exactly one of each digit,
%   - each cage (target T, list of cells) achieves its target with an
%     unknown operation (the operator is not given in the data).
% Output x is the solved grid as a list of lists of integers.
:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.   % ic and ic_global both export it

model(Instance, Vars, [x-Rows]) :-
    memberchk(n-N, Instance),
    memberchk(problem-Cages, Instance),
    dim(M, [N,N]),
    M[1..N,1..N] :: 1..N,
    flatten_array(M, Vars),

    % Each row and each column is all different (a Latin square).
    % Digits are 1..N, so all different means a permutation.
    ( for(I, 1, N), param(M, N) do
        collection_to_list(M[I,1..N], RowVars), alldifferent(RowVars),
        collection_to_list(M[1..N,I], ColVars), alldifferent(ColVars)
    ),

    % Each cage: the digits in its cells achieve its target under some operation.
    ( foreach([T, Cells], Cages), param(M) do
        cage_vars(Cells, M, CVs),
        cage(CVs, T)
    ),

    % Output: the grid as rows of variables.
    ( for(I, 1, N), foreach(Row, Rows), param(M, N) do
        collection_to_list(M[I,1..N], Row)
    ).

% Cells are [Row, Col] pairs with 1-based coordinates.
cage_vars([], _, []).
cage_vars([[R,C]|Cs], M, [V|Vs]) :-
    V is M[R,C],
    cage_vars(Cs, M, Vs).

% A single-cell cage holds its target value.
cage([V], T) :-
    V #= T.

% A two-cell cage: sum, difference, product or exact quotient equals the target.
cage([A,B], T) :-
    (   A + B #= T
    or  A - B #= T
    or  B - A #= T
    or  A * B #= T
    or  A #= T * B
    or  B #= T * A
    ).

% A larger cage: sum or product equals the target.
cage(Vs, T) :-
    Vs = [_,_,_|_],
    prod_expr(Vs, P),
    (   sum(Vs) #= T
    or  P #= T
    ).

prod_expr([V], V).
prod_expr([V,W|Ws], V*E) :-
    prod_expr([W|Ws], E).

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
