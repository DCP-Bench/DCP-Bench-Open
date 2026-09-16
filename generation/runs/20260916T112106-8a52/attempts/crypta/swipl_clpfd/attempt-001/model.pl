:- use_module(library(clpfd)).

% Crypta: a twenty-letter cryptarithmetic addition over ten distinct digits.
% The addition is checked seven digits at a time, with two carries between
% blocks, exactly as the reference splits it.
model(_Instance, Vars,
      ['A'-A, 'B'-B, 'C'-C, 'D'-D, 'E'-E,
       'F'-F, 'G'-G, 'H'-H, 'I'-I, 'J'-J]) :-
    Letters = [A, B, C, D, E, F, G, H, I, J],
    Letters ins 0..9,
    all_distinct(Letters),
    [Carry1, Carry2] ins 0..1,
    append(Letters, [Carry1, Carry2], Vars),

    % No number may start with a zero.
    B #>= 1, D #>= 1, G #>= 1,

    A + 10 * E + 100 * J + 1000 * B + 10000 * B + 100000 * E
      + 1000000 * F + E + 10 * J + 100 * E + 1000 * F + 10000 * G
      + 100000 * A + 1000000 * F
      #= F + 10 * E + 100 * E + 1000 * H + 10000 * I + 100000 * F
         + 1000000 * B + 10000000 * Carry1,

    C + 10 * F + 100 * H + 1000 * A + 10000 * I + 100000 * I
      + 1000000 * J + F + 10 * I + 100 * B + 1000 * D + 10000 * I
      + 100000 * D + 1000000 * C + Carry1
      #= J + 10 * F + 100 * A + 1000 * F + 10000 * H + 100000 * D
         + 1000000 * D + 10000000 * Carry2,

    A + 10 * J + 100 * J + 1000 * I + 10000 * A + 100000 * B + B
      + 10 * A + 100 * G + 1000 * F + 10000 * H + 100000 * D + Carry2
      #= C + 10 * A + 100 * G + 1000 * E + 10000 * J + 100000 * G.
