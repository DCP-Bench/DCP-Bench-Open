% Graph colouring: assign a colour to each of the six countries (Belgium, Denmark,
% France, Germany, Netherlands, Luxembourg) so that neighbouring countries get
% different colours, minimising the number of colours used. Colours are 1, 2, ...
% Neighbours come from the instance's graph field (1-based country indices).

:- lib(ic).
:- lib(listut).

model(Instance, Colors, [colors-Colors], min(NumColors)) :-
    memberchk(graph-Graph, Instance),
    length(Colors, 6),
    Colors :: 1..6,

    % Two neighbouring countries cannot have the same colour.
    ( foreach([A, B], Graph), param(Colors) do
        nth1(A, Colors, CA),
        nth1(B, Colors, CB),
        CA #\= CB
    ),

    % Minimise the number of colours used: the highest colour index in use.
    NumColors #= max(Colors).
