% N-fractions (CSPLib 041): find distinct non-zero digits A, B, C, D, E, F, G, H, I
% such that A / BC + D / EF + G / HI = 1, where BC, EF and HI are the two-digit
% numbers formed by B and C, E and F, and H and I.
% The model is a satisfaction problem with no instance data.

:- lib(ic).
:- lib(ic_global).
:- import alldifferent/1 from ic_global.

model(_Instance, Vars, Outputs) :-
    % Distinct non-zero digits A, B, C, D, E, F, G, H, I.
    Vars = [A, B, C, D, E, F, G, H, I],
    Vars :: 1..9,
    alldifferent(Vars),

    % The two-digit numbers BC, EF and HI.
    BC #= 10*B + C,
    EF #= 10*E + F,
    HI #= 10*H + I,

    % A / BC + D / EF + G / HI = 1, multiplied through by BC * EF * HI.
    % The multiplied form keeps every term an integer.
    A*EF*HI + D*BC*HI + G*BC*EF #= BC*EF*HI,

    Outputs = [
        'A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E,
        'F'-F, 'G'-G, 'H'-H, 'I'-I
    ].
