% Circular table (Averbach 1_2): three players X, Y, Z of different nationalities
% (American, English, French) are seated around a circular table playing Hearts.
% Each passed three cards to the person on their right. Y passed three hearts to the
% American, X passed the queen of spades and two diamonds to the person who passed
% their cards to the Frenchwoman. Determine the nationality of each person.
% Output: x, y, z, american, english, french; the same value denotes the matching
% between a person and their nationality, values 0, 1, 2; 1 is right of 0, 2 is right
% of 1, and so on (circular, so 0 is right of 2).

:- lib(ic).

model(_Instance, [X, Y, Z, American, English, French],
      [american-American, english-English, french-French, x-X, y-Y, z-Z]) :-
    % Players X, Y, Z are three different people, numbered 0..2 around the table.
    [X, Y, Z] #:: 0..2,
    alldifferent([X, Y, Z]),
    % Nationalities American, English, French are a permutation of the people.
    [American, English, French] #:: 0..2,
    alldifferent([American, English, French]),

    % Each passed three cards to the person on their right (the person numbered one higher, circularly).
    % Y passed three hearts to the American: the person on Y's right is the American.
    % The person on the right of person I is (I + 1) mod 3, written without mod on variables:
    % I + 1 - 3 * (I = 2).
    RightOfY #= Y + 1 - 3 * YIs2,
    YIs2 #= (Y #= 2),
    American #= RightOfY,

    % X passed the queen of spades and two diamonds to the person who passed their cards to the Frenchwoman.
    % Let P be the person X passed to; P passed to the Frenchwoman, so the Frenchwoman is on P's right.
    P #:: 0..2,
    RightOfX #= X + 1 - 3 * XIs2,
    XIs2 #= (X #= 2),
    P #= RightOfX,
    RightOfP #= P + 1 - 3 * PIs2,
    PIs2 #= (P #= 2),
    French #= RightOfP.
