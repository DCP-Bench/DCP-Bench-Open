% Cryptarithmetic puzzle (crypta): solve the addition
%
%   B A I J J A J I I A H F C F E B B J E A
% + D H F G A B C D I D B I F F A G F E J E
% = G J E G A C D D H F A F J B F I H E E F
%
% where all letters are distinct digits from 0 to 9, and the first letter of each
% number cannot be zero. Output the digit of each letter A, B, C, D, E, F, G, H, I, J.

:- lib(ic).
:- lib(lists).

model(_Instance, Vars, Outputs) :-
    % all letters are distinct digits from 0 to 9
    [A,B,C,D,E,F,G,H,I,J] :: 0..9,
    alldifferent([A,B,C,D,E,F,G,H,I,J]),

    % the first letter of each number cannot be zero
    B #\= 0,
    D #\= 0,
    G #\= 0,

    % the three numbers as digit lists, most significant digit first
    L1 = [B,A,I,J,J,A,J,I,I,A,H,F,C,F,E,B,B,J,E,A],
    L2 = [D,H,F,G,A,B,C,D,I,D,B,I,F,F,A,G,F,E,J,E],
    S  = [G,J,E,G,A,C,D,D,H,F,A,F,J,B,F,I,H,E,E,F],
    reverse(L1, R1),
    reverse(L2, R2),
    reverse(S, RS),

    % carries between columns, from the rightmost column leftwards;
    % no carry enters the rightmost column and none leaves the leftmost one
    length(Init, 19),
    Init :: 0..1,
    append(Init, [0], Couts),
    Cins = [0|Init],

    % column sums: digit of the first number + digit of the second + carry in
    % = digit of the sum + 10 * carry out
    ( foreach(X,R1), foreach(Y,R2), foreach(Z,RS), foreach(Ci,Cins), foreach(Co,Couts) do
        X + Y + Ci #= Z + 10*Co
    ),

    Vars = [A,B,C,D,E,F,G,H,I,J | Init],
    Outputs = ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E, 'F'-F, 'G'-G, 'H'-H, 'I'-I, 'J'-J].

% the letters are labelled most-constrained first
search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
