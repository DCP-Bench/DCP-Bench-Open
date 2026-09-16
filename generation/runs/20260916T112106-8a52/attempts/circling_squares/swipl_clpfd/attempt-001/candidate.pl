:- use_module(library(clpfd)).

% Circling the squares: ten different numbers around a circle where any two
% adjacent squares sum to the same as the two diametrically opposite.
model(_Instance, Xs,
      ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E,
       'F'-F, 'G'-G, 'H'-H, 'I'-I, 'K'-K]) :-
    Xs = [A, B, C, D, E, F, G, H, I, K],
    Xs ins 1..99,
    all_distinct(Xs),
    % The four numbers given as examples.
    A #= 16, B #= 2, F #= 8, G #= 14,
    balanced(A, B, F, G),
    balanced(B, C, G, H),
    balanced(C, D, H, I),
    balanced(D, E, I, K),
    balanced(E, F, K, A).

balanced(P, Q, R, S) :-
    P * P + Q * Q #= R * R + S * S.
