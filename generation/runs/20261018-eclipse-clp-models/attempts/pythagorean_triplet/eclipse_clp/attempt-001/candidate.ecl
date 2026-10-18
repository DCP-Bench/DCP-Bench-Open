% Pythagorean triplet: find the natural numbers a < b < c with a^2 + b^2 = c^2
% and a + b + c = 1000, and report a, b and c.
:- lib(ic).

model(_Instance, [A, B, C], [a-A, b-B, c-C]) :-
    % a, b, c are natural numbers (the description); the strict order a < b < c is
    % the usual reading of a triplet and is what makes the solution unique.
    [A, B, C] #:: 1..998,
    A #< B,
    B #< C,
    % a^2 + b^2 = c^2
    A*A + B*B #= C*C,
    % a + b + c = 1000
    A + B + C #= 1000.
