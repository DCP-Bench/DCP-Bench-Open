% ACC 1997/98 basketball double round-robin: 9 teams, 18 dates.
% Teams are 0-based: 0 Clem, 1 Duke, 2 FSU, 3 GT, 4 UMD, 5 UNC, 6 NCSt, 7 UVA, 8 Wake.
% config[d][i] = opponent of team i on date d (i itself on a bye); where[d][i] = 0 home, 1 bye, 2 away.
% Dates are 1-based in the comments below, 1..18.

:- lib(ic).
:- lib(ic_global).
:- lib(ic_mdd).
:- lib(listut).
:- import alldifferent/1 from ic_global.

% ---------------------------------------------------------------------------
% Entry point

model(Instance, Vars, Outputs) :-
    memberchk(n_teams-9, Instance),
    memberchk(n_days-18, Instance),
    make_rows(9, Crs, Wrs),
    Crs = [R1,R2,R3,R4,R5,R6,R7,R8,R9],
    Wrs = [Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9],
    mirror(Wrs, Vrs),
    Vrs = [P1,P2,P3,P4,P5,P6,P7,P8,P9],
    % date order 1..18; mirrored dates share the config row and reverse the venues
    % pairs (1,8) (2,9) (3,12) (4,13) (5,14) (6,15) (7,16) (10,17) (11,18)
    Cd = [R1,R2,R3,R4,R5,R6,R7,R1,R2,R8,R9,R3,R4,R5,R6,R7,R8,R9],
    Wd = [Q1,Q2,Q3,Q4,Q5,Q6,Q7,P1,P2,Q8,Q9,P3,P4,P5,P6,P7,P8,P9],
    % the nine first-of-pair dates 1,2,3,4,5,6,7,10,11 carry the free variables
    venue_tuples(Tuples),
    row_rules(Crs, Wrs),
    team_rules(0, Crs, Wrs, Tuples),
    rule6_last_date_rivals(Cd),
    rule7_constrained_matches(Cd),
    rule8_opponent_sequences(Cd, Wd),
    rule9_other_constraints(Cd, Wd),
    team_major(Wrs, WTeam),
    flatten(Crs, CRow),
    append(WTeam, CRow, Vars),
    Outputs = [config-Cd, where-Wd].

search_goal(Vars) :-
    search(Vars, 0, input_order, indomain_min, complete, []).

% ---------------------------------------------------------------------------
% Structure: the nine first-of-pair dates, and the mirror dates

make_rows(0, [], []) :- !.
make_rows(N, [C|Cs], [W|Ws]) :-
    N > 0,
    length(C, 9), C :: 0..8,
    length(W, 9), W :: 0..2,
    N1 is N - 1,
    make_rows(N1, Cs, Ws).

% A mirror date reverses the venue of its partner (home <-> away, bye stays a bye).
mirror([], []).
mirror([W|Ws], [V|Vs]) :-
    length(V, 9), V :: 0..2,
    ( foreach(Wi, W), foreach(Vi, V) do Vi #= 2 - Wi ),
    mirror(Ws, Vs).

team_major(Rows, Flat) :- team_major(0, Rows, Flat).
team_major(9, _, []) :- !.
team_major(I, Rows, Flat) :-
    column(I, Rows, Col),
    I1 is I + 1,
    team_major(I1, Rows, Rest),
    append(Col, Rest, Flat).

column(_, [], []).
column(I, [R|Rs], [X|Xs]) :-
    nth0(I, R, X),
    column(I, Rs, Xs).

% ---------------------------------------------------------------------------
% Per-date structure: a config row is a matching (an involution, with byes as fixed points)
% and the venues agree with it: a match gives one home and one away side, a bye is 1.

row_rules([], []).
row_rules([C|Cs], [W|Ws]) :-
    % each team meets one opponent or has a bye on this date
    alldifferent(C),
    row_cells(0, C, W),
    % per date: one bye, four home, four away (the 4 matches of the 8 teams that play)
    occurrences(1, W, 1),
    occurrences(0, W, 4),
    occurrences(2, W, 4),
    row_rules(Cs, Ws).

row_cells(9, _, _) :- !.
row_cells(I, C, W) :-
    nth0(I, C, Ci),
    nth0(I, W, Wi),
    JP1 #= Ci + 1,
    % the opponent of my opponent is me
    element(JP1, C, IV), IV #= I,
    % the opponent's venue is the reverse of mine
    element(JP1, W, Wj),
    Wi + Wj #= 2,
    % a bye is exactly a self-opponent
    (Wi #= 1) <=> (Ci #= I),
    I1 is I + 1,
    row_cells(I1, C, W).

% Each team meets each opponent once over the nine first-of-pair dates; a bye is the team itself.
% Each team's venue pattern over those dates is one of the sequences that satisfy the
% pattern rules 2 to 5 (table computed from the rules below).
team_rules(9, _, _, _) :- !.
team_rules(I, Crs, Wrs, Tuples) :-
    column(I, Crs, Col),
    alldifferent(Col),
    column(I, Wrs, WCol),
    table([WCol], Tuples),
    I1 is I + 1,
    team_rules(I1, Crs, Wrs, Tuples).

% ---------------------------------------------------------------------------
% Venue patterns (rules 2, 3, 4, 5), enumerated in Prolog over the nine first-of-pair dates.
% Venue values: 0 home, 1 bye, 2 away.

venue_tuples(Tuples) :-
    findall(S, (gen_seq(9, S), ok_pattern(S)), Tuples).

gen_seq(0, []) :- !.
gen_seq(N, [V|Vs]) :-
    N > 0,
    member(V, [0,1,2]),
    N1 is N - 1,
    gen_seq(N1, Vs).

ok_pattern([S1,S2,S3,S4,S5,S6,S7,S8,S9]) :-
    M1 is 2 - S1, M2 is 2 - S2, M3 is 2 - S3, M4 is 2 - S4, M5 is 2 - S5,
    M6 is 2 - S6, M7 is 2 - S7, M8 is 2 - S8, M9 is 2 - S9,
    F = [S1,S2,S3,S4,S5,S6,S7,M1,M2,S8,S9,M3,M4,M5,M6,M7,M8,M9],
    % rule 2: no team plays away on both last dates (17 and 18)
    \+ (M8 =:= 2, M9 =:= 2),
    % rule 3: at most two away in a row, at most two home in a row,
    % at most three away-or-bye in a row, at most four home-or-bye in a row
    no_run(F, [2], 3),
    no_run(F, [0], 3),
    no_run(F, [1,2], 4),
    no_run(F, [0,1], 5),
    % rule 4: the weekends (even dates) hold four home, four away and one bye
    E = [S2,S4,S6,M1,S8,M3,M5,M7,M9],
    cnt(0, E, 4),
    cnt(2, E, 4),
    cnt(1, E, 1),
    % rule 5: home or bye on at least two of the first five weekends (dates 2,4,6,8,10)
    F5 = [S2,S4,S6,M1,S8],
    cnt(0, F5, H5),
    cnt(1, F5, B5),
    H5 + B5 >= 2.

no_run(L, Set, K) :-
    \+ ( append(_, T, L), append(P, _, T), length(P, K), all_in(P, Set) ).

all_in([], _).
all_in([X|Xs], Set) :-
    memberchk(X, Set),
    all_in(Xs, Set).

cnt(_, [], 0).
cnt(V, [X|Xs], N) :-
    (   X =:= V
    ->  cnt(V, Xs, N1), N is N1 + 1
    ;   cnt(V, Xs, N)
    ).

% ---------------------------------------------------------------------------
% Rule 6: Rival matches. Every team except FSU plays its rival on the last date,
% unless it plays against FSU or has a bye.
% Rivals: Duke-UNC, Clem-GT, NCSt-Wake, UMD-UVA.

rival(0, 3).
rival(3, 0).
rival(1, 5).
rival(5, 1).
rival(6, 8).
rival(8, 6).
rival(4, 7).
rival(7, 4).

rule6_last_date_rivals(Cd) :-
    rule6_teams([0,1,3,4,5,6,7,8], Cd).

rule6_teams([], _).
rule6_teams([I|Is], Cd) :-
    rival(I, J),
    cell(18, I, Cd, X),
    ( X #= J ) or ( X #= 2 ) or ( X #= I ),
    rule6_teams(Is, Cd).

% ---------------------------------------------------------------------------
% Rule 7: Constrained matches. Wake-UNC, Wake-Duke, GT-UNC and GT-Duke occur at least
% once in dates 11 to 18.

rule7_constrained_matches(Cd) :-
    constrained_pair(8, 5, Cd),
    constrained_pair(8, 1, Cd),
    constrained_pair(3, 5, Cd),
    constrained_pair(3, 1, Cd).

constrained_pair(A, B, Cd) :-
    ( for(D, 11, 18), foreach(Bool, Bools), param(A, B, Cd) do
        cell(D, A, Cd, X),
        Bool #= (X #= B)
    ),
    sum(Bools) #>= 1.

% ---------------------------------------------------------------------------
% Rule 8: Opponent sequence constraints.
% No team plays in two consecutive dates away against UNC and Duke.
% No team plays in three consecutive dates against UNC, Duke and Wake (independent of home/away).

rule8_opponent_sequences(Cd, Wd) :-
    ( for(I, 0, 8), param(Cd, Wd) do
        ( for(D, 1, 17), param(I, Cd, Wd) do
            cell(D, I, Cd, C1), cell(D, I, Wd, W1),
            D1 is D + 1,
            cell(D1, I, Cd, C2), cell(D1, I, Wd, W2),
            ( C1 #\= 5 ) or ( W1 #\= 2 ) or ( C2 #\= 1 ) or ( W2 #\= 2 ),
            ( C1 #\= 1 ) or ( W1 #\= 2 ) or ( C2 #\= 5 ) or ( W2 #\= 2 )
        )
    ),
    ( for(I, 0, 8), param(Cd) do
        ( for(D, 1, 16), param(I, Cd) do
            cell(D, I, Cd, A), D1 is D + 1, D2 is D + 2,
            cell(D1, I, Cd, B), cell(D2, I, Cd, C),
            ( A #\= 5 ) or ( B #\= 1 ) or ( C #\= 8 ),
            ( A #\= 5 ) or ( B #\= 8 ) or ( C #\= 1 ),
            ( A #\= 1 ) or ( B #\= 5 ) or ( C #\= 8 ),
            ( A #\= 1 ) or ( B #\= 8 ) or ( C #\= 5 ),
            ( A #\= 8 ) or ( B #\= 5 ) or ( C #\= 1 ),
            ( A #\= 8 ) or ( B #\= 1 ) or ( C #\= 5 )
        )
    ).

% ---------------------------------------------------------------------------
% Rule 9: Other constraints.

rule9_other_constraints(Cd, Wd) :-
    % UNC plays its rival Duke in the last date, and in date 11 (same config row)
    cell(18, 5, Cd, X18), X18 #= 1,
    cell(11, 5, Cd, X11), X11 #= 1,
    % UNC plays Clem in the second date
    cell(2, 5, Cd, X2), X2 #= 0,
    % Duke has a bye in date 16
    cell(16, 1, Wd, V16), V16 #= 1,
    % Wake does not play home in date 17
    cell(17, 8, Wd, V17), V17 #\= 0,
    % Wake has a bye in the first date
    cell(1, 8, Wd, V1w), V1w #= 1,
    % Clem, Duke, UMD and Wake do not play away in the last date
    forall_teams([0,1,4,8], 18, Wd, 2),
    % Clem, FSU, GT and Wake do not play away in the first date
    forall_teams([0,2,3,8], 1, Wd, 2),
    % Neither FSU nor NCSt have a bye in the last date
    forall_teams([2,6], 18, Wd, 1),
    % UNC does not have a bye in the first date
    cell(1, 5, Wd, V1u), V1u #\= 1.

forall_teams([], _, _, _).
forall_teams([I|Is], D, Wd, V) :-
    cell(D, I, Wd, X),
    X #\= V,
    forall_teams(Is, D, Wd, V).

% ---------------------------------------------------------------------------
% Access to a date (1-based) and a team (0-based) in a 18-date list of rows.

cell(D, I, Lst, X) :-
    nth1(D, Lst, Row),
    I1 is I + 1,
    nth1(I1, Row, X).
