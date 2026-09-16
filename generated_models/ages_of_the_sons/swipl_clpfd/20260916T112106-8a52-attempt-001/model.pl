:- use_module(library(clpfd)).

% Ages of the sons: the product is 36, the sum is ambiguous, and there is a
% unique oldest.  The second triple B is what makes the sum ambiguous: another
% factorisation of 36 with the same sum and a different eldest.
model(_Instance, Vars, ['A1'-A1, 'A2'-A2, 'A3'-A3]) :-
    Ages = [A1, A2, A3, B1, B2, B3],
    Ages ins 0..36,
    [ASum, BSum] ins 0..1000,
    append(Ages, [ASum, BSum], Vars),

    A1 #> A2, A2 #>= A3,
    36 #= A1 * A2 * A3,

    B1 #>= B2, B2 #>= B3,
    A1 #\= B1,
    36 #= B1 * B2 * B3,

    ASum #= A1 + A2 + A3,
    BSum #= B1 + B2 + B3,
    ASum #= BSum.
