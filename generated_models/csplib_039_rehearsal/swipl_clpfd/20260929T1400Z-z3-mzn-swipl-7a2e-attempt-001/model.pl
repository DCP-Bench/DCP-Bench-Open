:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Rehearsal problem: order the pieces of a concert for rehearsal so that the
% total time players spend present but not playing is minimal. A player arrives
% just before the first piece they play in and leaves after the last one.
model(Instance, Vars, [rehearsal_order-Order], min(Waiting)) :-
    NPieces = Instance.num_pieces,
    NPlayers = Instance.num_players,
    Duration = Instance.duration,        % rehearsal time of each piece
    Rehearsal = Instance.rehearsal,      % Rehearsal[p][j] = 1 if player p plays in piece j
    Top is NPieces - 1,

    % Order[i] = the piece (numbered from 0) rehearsed in slot i; each piece is rehearsed exactly once
    length(Order, NPieces),
    Order ins 0..Top,
    all_distinct(Order),

    % the length of the piece in each slot, read from the data with element/3 (counts from 1)
    maplist({Duration}/[Piece, Length]>>(Index #= Piece + 1, element(Index, Duration, Length)), Order, Lengths),

    % Arrival[p] / Departure[p] = first / last slot in which player p is present
    length(Arrival, NPlayers), Arrival ins 1..NPieces,
    length(Departure, NPlayers), Departure ins 1..NPieces,

    % waiting = present but not playing, which costs the length of the piece in that slot
    numlist(1, NPieces, Slots),
    maplist({Order, Lengths, Slots}/[Plays, First, Last, Costs]>>(
                maplist({Plays}/[Piece, Plays1]>>(Index #= Piece + 1, element(Index, Plays, Plays1)), Order, Played),
                maplist({First, Last}/[Slot, Played1, Length, Cost]>>(
                            % a player who plays in slot i must be present in it
                            Played1 #==> (First #=< Slot #/\ Slot #=< Last),
                            Wait #<==> (First #=< Slot #/\ Slot #=< Last #/\ Played1 #= 0),
                            Cost #= Wait * Length), Slots, Played, Lengths, Costs)),
            Rehearsal, Arrival, Departure, CostLists),
    append(CostLists, AllCosts),
    sum_list(Duration, DurationSum),
    Bound is DurationSum * NPlayers,
    Waiting in 0..Bound,
    sum(AllCosts, #=, Waiting),
    append([Order, Arrival, Departure, AllCosts, Lengths, [Waiting]], Vars).
