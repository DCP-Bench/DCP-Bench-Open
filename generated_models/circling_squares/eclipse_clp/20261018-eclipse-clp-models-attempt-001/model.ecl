% Circling the squares: place a different whole number in each of the ten
% squares A, B, C, D, E, F, G, H, I, K arranged in a circle, so that the sum of
% the squares of any two adjacent numbers equals the sum of the squares of the
% two numbers diametrically opposite them. A=16, B=2, F=8, G=14 are given.
% Fractions are not allowed; no number needs more than two figures.

:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.

model(_Instance, [A,B,C,D,E,F,G,H,I,K], Outputs) :-
    Vars = [A,B,C,D,E,F,G,H,I,K],
    Vars :: 1..99,

    % Each of the ten squares holds a different number.
    alldifferent(Vars),

    % The four numbers placed as examples must stand as they are.
    A #= 16,
    B #= 2,
    F #= 8,
    G #= 14,

    % The sum of the squares of any two adjacent numbers shall be equal to the
    % sum of the squares of the two numbers diametrically opposite to them.
    % Positions 0..9 in the circle; opposite of position i is i+5. Each pair of
    % adjacent squares is compared with the opposite pair, for the five distinct
    % pairings (the other five are the same equations reversed).
    A*A + B*B #= F*F + G*G,
    B*B + C*C #= G*G + H*H,
    C*C + D*D #= H*H + I*I,
    D*D + E*E #= I*I + K*K,
    E*E + F*F #= K*K + A*A,

    Outputs = [
        'A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E,
        'F'-F, 'G'-G, 'H'-H, 'I'-I, 'K'-K
    ].
