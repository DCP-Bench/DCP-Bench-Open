% Curious set of integers: the integers 1, 3, 8 and 120 form a set in which the
% product of any two integers is one less than a perfect square. Find a fifth
% number Number (larger than or equal to 0) that can be added to the set without
% destroying this property. The instance gives max_val, the upper bound of Number.

:- lib(ic).

model(Instance, [Number | Roots], [number-Number], none) :-
    memberchk(max_val-MaxVal, Instance),
    Number :: 0..MaxVal,
    % Each product of a set member with Number is one less than a perfect square.
    % The square roots Root are auxiliary variables, labelled after Number.
    Hi is 120 * MaxVal + 1,
    square_plus_one(1, Number, Hi, R1),
    square_plus_one(3, Number, Hi, R2),
    square_plus_one(8, Number, Hi, R3),
    square_plus_one(120, Number, Hi, R4),
    Roots = [R1, R2, R3, R4].

% Root * Root is one more than A * X.
square_plus_one(A, X, Hi, Root) :-
    Root :: 0..Hi,
    Root * Root #= A * X + 1.
