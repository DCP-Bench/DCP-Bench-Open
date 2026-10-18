% Problem: session5_hardy_1729_square
% Find a combination of 4 different numbers between 1 and 100 such that the
% sum of the squares of the two first numbers equals the sum of the squares of
% the other two, a^2 + b^2 = c^2 + d^2. Print the numbers (a, b, c, d).
% The instance carries no fields; the model is the same for every instance.

:- lib(ic).

model(_Instance, [A, B, C, D], [a-A, b-B, c-C, d-D]) :-
    % Find a combination of 4 different numbers between 1 and 100
    [A, B, C, D] #:: 1..100,

    % such that ... the 4 numbers are different
    alldifferent([A, B, C, D]),

    % the sum of the squares of the two first numbers is equal to the sum of the squares of the other two numbers, a^2 + b^2 = c^2 + d^2
    A*A + B*B #= C*C + D*D.
