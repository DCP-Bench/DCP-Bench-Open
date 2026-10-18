% Problem: among.
% Requires exactly m values in x to take one of the values in v. All other values
% may be anything larger than or equal to 0 and less than or equal to 7.
% Print the array x.

:- lib(ic).

model(Instance, X, [x-X]) :-
    memberchk(n-N, Instance),
    memberchk(m-M, Instance),
    memberchk(v-V, Instance),
    length(X, N),
    % All other values may be anything larger than or equal to 0 and less than or equal to 7.
    X :: 0..7,
    % Bits[K+1] is 1 when the value K (0..7) is one of the values in v.
    ( for(K, 0, 7), param(V), foreach(Bit, Bits) do
        ( memberchk(K, V) -> Bit = 1 ; Bit = 0 )
    ),
    length(B, N),
    B :: 0..1,
    % Requires exactly m values in x to take one of the values in v.
    ( foreach(Xi, X), foreach(Bi, B), param(Bits) do
        Xi1 #= Xi + 1,
        element(Xi1, Bits, Bi)
    ),
    sum(B) #= M.
