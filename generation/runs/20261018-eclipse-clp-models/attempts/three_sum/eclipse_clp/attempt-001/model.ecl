% Three-sum: given a collection of integers, find a number of elements that
% sum to zero. Output whether each element is selected (indices) as a list
% of booleans. The number of selected elements is the instance's m.

:- lib(ic).

model(Instance, Xs, [indices-Xs]) :-
    memberchk(nums-Nums, Instance),
    memberchk(m-M, Instance),
    length(Nums, N),
    length(Xs, N),
    Xs :: 0..1,

    % find a number of elements that sum to zero
    ( foreach(X, Xs), foreach(V, Nums), fromto(0, A, B, S) do
        B #= A + X * V
    ),
    S #= 0,

    % a number of elements (m of them)
    sum(Xs) #= M.
