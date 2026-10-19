% Five brigands (Alfonso, Benito, Carlos, Diego, Esteban) count their spoils.
% A, B, C, D, E are the doubloons of Alfonso, Benito, Carlos, Diego and Esteban.
% Outputs: A, B, C, D, E.

:- lib(ic).

model(_Instance, [A, B, C, D, E], ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E]) :-
    [A, B, C, D, E] #:: 1..200,

    % they had captured altogether exactly 200 doubloons
    A + B + C + D + E #= 200,

    % if Alfonso had twelve times as much, Benito three times as much, Carlos the same
    % amount, Diego half as much and Esteban one-third as much, they would still have
    % altogether just 200 doubloons.
    % Multiplied by 6 to keep the coefficients integral:
    % 6*(12A + 3B + C + D/2 + E/3) = 6*200
    72*A + 18*B + 6*C + 3*D + 2*E #= 1200,

    % no brigand had less than one doubloon.
    A #>= 1, B #>= 1, C #>= 1, D #>= 1, E #>= 1.
