:- use_module(library(clpfd)).

% Fractions puzzle: find nine different non-zero digits A..I such that
% A/BC + D/EF + G/HI = 1, where BC, EF and HI are two-digit numbers.
%
% The puzzle has no data.
model(_Instance, Digits,
      ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E, 'F'-F, 'G'-G, 'H'-H, 'I'-I]) :-
    Digits = [A, B, C, D, E, F, G, H, I],
    % the nine digits, all different and non-zero
    Digits ins 1..9,
    all_distinct(Digits),

    % the three denominators BC, EF, HI as two-digit numbers
    D1 #= 10 * B + C,
    D2 #= 10 * E + F,
    D3 #= 10 * H + I,

    % Multiplying the equation A/D1 + D/D2 + G/D3 = 1 through by D1*D2*D3 gives
    % A*D2*D3 + D*D1*D3 + G*D1*D2 = D1*D2*D3, which avoids fractions.
    A * D2 * D3 + D * D1 * D3 + G * D1 * D2 #= D1 * D2 * D3.
