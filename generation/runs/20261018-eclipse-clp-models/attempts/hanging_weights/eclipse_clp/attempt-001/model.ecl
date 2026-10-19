% Hanging weights puzzle: weights A-M (outputs a-m), each an integer 1..13, hang
% from a system of bars. Each bar is a pivot with weights or bars at its holes.

:- lib(ic).

model(_Instance, Vars, Outputs) :-
    Vars = [A, B, C, D, E, F, G, H, I, J, K, L, M],
    Vars :: 1..13,
    % The weights on either side of a given pivot point must be equal, when weighted
    % by the distance from the pivot.
    % Bar with E and F: E is 3 holes from the pivot, F is 2 holes from it.
    3*E #= 2*F,
    % Bar with H, I and the E-F bar: H is 3 holes from the pivot, the E-F bar hangs
    % 2 holes from it on one side and I is 3 holes on the other side.
    % A bar hanging beneath another contributes its total weight as though it were a single weight.
    3*H #= 2*(E + F) + 3*I,
    % Bar with the H-bar (total H+I+E+F) on one side and L and M on the other:
    % the H-bar is 1 hole from the pivot, L is 1 hole, M is 4 holes.
    H + I + E + F #= L + 4*M,
    % Top bar: the left bar (H, I, E, F, L, M) is 4 holes from the pivot, the right bar
    % (J, K, A, B, C, D, G) is 3 holes from the pivot.
    4*(H + I + E + F + L + M) #= 3*(J + K + A + B + C + D + G),
    % Bar with J and K and the bars below it: J is 2 holes from the pivot, the A-B bar
    % hangs 3 holes from it on the left, K is 1 hole on the right, the G bar is 2 holes.
    % A bar hanging beneath another contributes its total weight as though it were a single weight.
    2*J + 3*(A + B) #= K + 2*(G + C + D),
    % Bar with A and B: A is 4 holes from the pivot and B is 1 hole.
    4*A #= B,
    % The bar on the bottom right must have 5*C=D.
    5*C #= D,
    % The bar above it must have 3*G=2*(C+D).
    3*G #= 2*(C + D),
    Outputs = [a-A, b-B, c-C, d-D, e-E, f-F, g-G, h-H, i-I, j-J, k-K, l-L, m-M].

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
