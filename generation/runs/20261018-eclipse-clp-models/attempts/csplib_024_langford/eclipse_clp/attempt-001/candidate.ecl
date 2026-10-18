% CSPLib 024, Langford's number problem (satisfaction).
% Two sets of the numbers 1 to k. Arrange the 2k numbers of the two sets into one
% sequence so that the two 1's appear one number apart, the two 2's two numbers
% apart, ..., and the two k's k numbers apart. Output sol is the sequence of 2k
% integers from 1 to k.
:- lib(ic).

model(Instance, Vars, Outputs) :-
    memberchk(k-K, Instance),
    N is 2*K,
    % As[I] is the first position of the two I's (1-based)
    length(As, K),
    % the sequence sol of 2k integers from 1 to k
    length(Sol, N),
    Sol :: 1..K,
    ( foreach(A, As), param(N) do A :: 1..N ),
    % the two i's appear one number apart, the two 2's two numbers apart, ...,
    % and the two k's k numbers apart: the second i sits i+1 positions after the first
    ( for(I, 1, K), foreach(A, As), foreach(B, Bs), param(N, Sol) do
        B :: 1..N,
        B #= A + I + 1,
        element(A, Sol, I),
        element(B, Sol, I)
    ),
    % the 2k numbers of the two sets are arranged into one sequence: every position
    % is the first or second copy of exactly one number
    append(As, Bs, Cells),
    alldifferent(Cells),
    Vars = As,
    Outputs = [sol-Sol].

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
