% Guards and apples: a boy passes num_gates gates. Each guard is bribed with half
% of his apples plus one. Output apples: the number of apples before each gate,
% plus the number after the last gate (num_gates + 1 numbers in total).

:- lib(ic).
:- lib(lists).

model(Instance, Vars, [apples-As], none) :-
    memberchk(num_gates-N, Instance),
    N1 is N + 1,
    Max is 2^(N + 2),
    length(As, N1),
    As :: 0..Max,
    length(Hs, N),
    Hs :: 0..Max,
    % He bribes each guard with half of his apples, plus one.
    % The boy does not have a knife, therefore he gives the guard an integer number of apples.
    gates(As, Hs),
    % After he's given the apple to the girl, he has no apples left.
    append(_, [Last], As),
    Last #= 1,
    append(As, Hs, Vars).

% Each gate: the guard takes H + 1 where 2*H is the apples before the gate.
gates([_], []).
gates([A, B | Rest], [H | Hs]) :-
    2 * H #= A,
    B #= A - H - 1,
    gates([B | Rest], Hs).
