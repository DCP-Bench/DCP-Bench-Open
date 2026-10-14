:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).
:- use_module(library(yall)).

% Crew scheduling: assign flight attendants to flights. Each flight needs a
% given number of cabin crew, among them minimum numbers of stewards,
% hostesses and speakers of French, Spanish and German, and an attendant who
% worked a flight has the next two flights off.
model(Instance, Vars, [crew-Crew]) :-
    Attributes = Instance.attributes,       % Attributes[p] = [steward, hostess, french, spanish, german] as 0/1
    RequiredCrew = Instance.required_crew,  % RequiredCrew[f] = [staff, stewards, hostesses, french, spanish, german]

    length(Attributes, NumPersons),
    length(RequiredCrew, NumFlights),

    % Crew[f][p] is 1 when person p works flight f
    length(Crew, NumFlights),
    maplist({NumPersons}/[Row]>>(length(Row, NumPersons), Row ins 0..1), Crew),

    % number of working persons: those assigned to at least one flight
    NumWorking in 1..NumPersons,
    transpose(Crew, CrewByPerson),
    maplist(works_some_flight, CrewByPerson, WorkingFlags),
    sum(WorkingFlags, #=, NumWorking),

    % each flight has the required crew size and at least the required number of
    % attendants having each attribute
    transpose(Attributes, AttributeColumns),
    maplist(flight_staffed(AttributeColumns), Crew, RequiredCrew),

    % after a flight an attendant has the next two flights off: at most one of
    % any three consecutive flights
    no_three_in_a_row(Crew),
    append(Crew, CrewVars),
    append(CrewVars, [NumWorking], Vars).

% Works is 1 when the person is assigned to at least one flight.
works_some_flight(Flights, Works) :-
    sum(Flights, #=, Total),
    Works #<==> (Total #>= 1).

% A flight's row of the crew matrix meets its requirements: [Staff|Minimums]
% gives the crew size and the minimum for each attribute column.
flight_staffed(AttributeColumns, Row, [Staff|Minimums]) :-
    sum(Row, #=, Staff),
    maplist({Row}/[Column, Minimum]>>scalar_product(Column, Row, #>=, Minimum),
            AttributeColumns, Minimums).

no_three_in_a_row([Flight1, Flight2, Flight3|Rest]) :- !,
    maplist([A, B, C]>>(A + B + C #=< 1), Flight1, Flight2, Flight3),
    no_three_in_a_row([Flight2, Flight3|Rest]).
no_three_in_a_row(_).
