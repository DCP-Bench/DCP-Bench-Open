:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).
:- use_module(library(pairs)).

% Progressive party: choose as few host boats as possible and timetable the
% crews of the other boats so that in every period each guest crew visits one
% host, no host is overfull, no guest crew visits a host twice and no two crews
% meet more than once.
model(Instance, Vars, [is_host-IsHost, visits-Visits], min(NHosts)) :-
    NBoats = Instance.n_boats,
    NPeriods = Instance.n_periods,
    Capacity = Instance.capacity,    % most people allowed aboard each boat
    CrewSize = Instance.crew_size,   % people in each boat's crew

    Top is NBoats - 1,
    numlist(0, Top, Boats),
    % IsHost[b] is 1 when boat b is a host
    length(IsHost, NBoats),
    IsHost ins 0..1,
    % Visits[p][b] = the boat (numbered from 0) that the crew of boat b is on in period p
    length(Visits, NPeriods),
    maplist({NBoats, Top}/[Row]>>(length(Row, NBoats), Row ins 0..Top), Visits),

    % the crews of host boats stay on their own boat in every period
    maplist(stays_home(Visits), Boats, IsHost),

    % in each period the people aboard a boat never exceed its capacity
    maplist(within_capacity(Boats, CrewSize, Capacity), Visits),

    % a guest crew never visits the same boat twice
    transpose(Visits, VisitsOfBoat),
    maplist(no_revisit(NBoats), VisitsOfBoat, IsHost),

    % boats that are not hosts are never visited
    maplist(visited_only_if_host(Visits), Boats, IsHost),

    % two crews meet at most once: boats c1 < c2 are on the same boat in at
    % most one period
    findall(C1-C2, (between(0, Top, C1), Next is C1 + 1, between(Next, Top, C2)), Pairs),
    maplist(meet_at_most_once(Visits), Pairs),

    % implied: the crews of all boats are aboard hosts in every period, so the
    % hosts' capacities together hold the total crew (follows from the
    % constraints above; it lets the search discard host sets that are too small)
    sum_list(CrewSize, TotalCrew),
    scalar_product(Capacity, IsHost, #>=, TotalCrew),

    % objective: the number of host boats
    sum(IsHost, #=, NHosts),

    % Search order: decide the hosts first, trying the boats with the largest
    % capacity as hosts first, then the visits. Guests[b] = 1 - IsHost[b] is
    % chosen, so that trying 0 first makes a boat a host. Deciding hosts by
    % boat number instead lets the search settle on a set of small boats whose
    % visits it cannot schedule, and it spends all its time inside that set.
    maplist([Host, Guest]>>(Guest #= 1 - Host), IsHost, Guests),
    maplist({Capacity}/[Boat, MinusCapacity-Boat]>>(nth0(Boat, Capacity, Cap), MinusCapacity is -Cap),
            Boats, Keyed),
    keysort(Keyed, Sorted),
    pairs_values(Sorted, Preferred),
    maplist({Guests}/[Boat, Guest]>>nth0(Boat, Guests, Guest), Preferred, OrderedGuests),
    append(Visits, VisitVars),
    append(OrderedGuests, VisitVars, Vars).

% A host crew is on its own boat in every period.
stays_home(Visits, Boat, Host) :-
    maplist({Boat, Host}/[Row]>>(nth0(Boat, Row, At), Host #==> (At #= Boat)), Visits).

% In one period (Row = where each crew is), boat Boat holds the crews that are
% on it, whose sizes add up to at most its capacity.
within_capacity(Boats, CrewSize, Capacity, Row) :-
    maplist({Row, CrewSize}/[Boat, Cap]>>(
                maplist({Boat}/[At, Aboard]>>(Aboard #<==> (At #= Boat)), Row, Flags),
                scalar_product(CrewSize, Flags, #=<, Cap)),
            Boats, Capacity).

% The stops of a guest crew (the boats it visits in successive periods) are
% pairwise different. A host crew never moves, so it is exempt. all_distinct
% cannot be made conditional, hence it runs on a copy of the stops in which a
% host's entry is pushed above every boat number by a different amount in each
% period, which makes the copy distinct for a host and equal to the stops for a
% guest.
no_revisit(NBoats, Stops, Host) :-
    length(Stops, NPeriods),
    Last is NPeriods - 1,
    numlist(0, Last, Periods),
    maplist({NBoats, Host}/[At, P, Copy]>>(Copy #= At + Host * (NBoats + P)),
            Stops, Periods, Copies),
    all_distinct(Copies).

% A boat that is not a host has no visitors in any period.
visited_only_if_host(Visits, Boat, Host) :-
    maplist({Boat, Host}/[Row]>>(
                maplist({Boat, Host}/[At]>>(Host #= 0 #==> (At #\= Boat)), Row)),
            Visits).

% Crews of boats C1 and C2 are together in at most one period.
meet_at_most_once(Visits, C1-C2) :-
    maplist({C1, C2}/[Row, Meet]>>(
                nth0(C1, Row, At1), nth0(C2, Row, At2),
                Meet #<==> (At1 #= At2)),
            Visits, Meets),
    sum(Meets, #=<, 1).
