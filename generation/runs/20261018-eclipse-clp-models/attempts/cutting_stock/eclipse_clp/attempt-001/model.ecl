% Cutting stock: decide how many rolls to cut with each cutting pattern.
% A roll of width RollWidth is cut into pieces of the given widths; each width
% has a number of orders. There are NumPatterns patterns and each pattern has a
% number of rolls of each width.
% The problem minimises the total number of raw rolls cut.

:- lib(ic).
:- lib(listut).

model(Instance, Used, [patterns_used-Used, min_rolls_cut-Total], min(Total)) :-
    memberchk(num_patterns-P, Instance),
    memberchk(orders-Orders, Instance),
    memberchk(num_rolls_width-Rows, Instance),
    length(Orders, W),
    sum(Orders, Demand),
    length(Used, P),
    % How many rolls are cut with each pattern.
    Used :: 0..Demand,
    % For each width, the total number of rolls cut meets the total orders.
    width_orders(Orders, 1, W, Rows, Used),
    % The total number of raw rolls cut.
    Total #= sum(Used).

width_orders([], _, _, _, _).
width_orders([Ord|Ords], I, W, Rows, Used) :-
    ( foreach(Row, Rows), foreach(C0, Col), param(I) do nth1(I, Row, C0) ),
    ( foreach(C, Col), foreach(U, Used), foreach(T, Terms) do T #= C*U ),
    sum(Terms) #>= Ord,
    I1 is I + 1,
    width_orders(Ords, I1, W, Rows, Used).
