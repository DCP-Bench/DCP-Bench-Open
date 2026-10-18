% csplib_039_rehearsal: rehearsal order of a concert.
% A concert consists of pieces of music of different durations, each involving a
% different combination of the players. Players arrive at rehearsals immediately
% before the first piece in which they are involved and depart immediately after
% the last piece in which they are involved. Find an order in which the pieces can
% be rehearsed so as to minimise the total time that players are waiting to play,
% i.e. the total time when players are present but not currently playing.

:- lib(ic).

model(Instance, Ord, [rehearsal_order-Ord], min(Wait)) :-
    memberchk(num_pieces-N, Instance),
    memberchk(duration-Dur, Instance),
    memberchk(rehearsal-R, Instance),

    % The rehearsal order is a permutation of the pieces: rehearsal_order[i] is the
    % piece rehearsed in the i-th slot, a list of num_pieces integers from 0 to
    % num_pieces - 1.
    length(Ord, N),
    Ord :: 0..N-1,
    alldifferent(Ord),

    % Pos is the inverse permutation: piece k is rehearsed in slot Pos[k].
    length(Pos, N),
    Pos :: 0..N-1,
    alldifferent(Pos),
    post_inverse(Ord, Pos, 0),

    % Each piece takes its duration; slot i starts after the pieces in slots 0..i-1.
    slot_starts(Ord, Dur, 0, Starts),

    % The piece k starts at the start of its slot.
    piece_starts(Pos, Starts, STs),

    % Players are present from the start of their first piece to the end of their
    % last piece, and they wait for the time they are present but not playing.
    ends_of(STs, Dur, Ends),
    player_waits(R, Dur, STs, Ends, Waits),
    sum(Waits) #= Wait.

post_inverse([], _, _).
post_inverse([O|Os], Pos, I) :-
    OP #= O + 1,
    element(OP, Pos, I),
    I1 is I + 1,
    post_inverse(Os, Pos, I1).

slot_starts([], _, _, []).
slot_starts([O|Os], Dur, S, [S|Ss]) :-
    OP #= O + 1,
    element(OP, Dur, D),
    S1 #= S + D,
    slot_starts(Os, Dur, S1, Ss).

piece_starts(Pos, Starts, STs) :-
    ( foreach(P, Pos), foreach(ST, STs), param(Starts) do
        PP #= P + 1,
        element(PP, Starts, ST)
    ).

ends_of(STs, Dur, Ends) :-
    ( foreach(ST, STs), foreach(D, Dur), foreach(E, Ends) do
        E #= ST + D
    ).

player_waits([], _, _, _, []).
player_waits([Row|Rows], Dur, STs, Ends, [W|Ws]) :-
    pick(Row, STs, Ends, Dur, SelST, SelEnd, SelD),
    (   SelST == []
    ->  W = 0
    ;   W #= max(SelEnd) - min(SelST) - sum(SelD)
    ),
    player_waits(Rows, Dur, STs, Ends, Ws).

% Keep the start, end and duration of the pieces in which the player is involved.
pick([], [], [], [], [], [], []).
pick([1|Rs], [S|Ss], [E|Es], [D|Ds], [S|Sel], [E|SelE], [D|SelD]) :-
    !,
    pick(Rs, Ss, Es, Ds, Sel, SelE, SelD).
pick([_|Rs], [_|Ss], [_|Es], [_|Ds], Sel, SelE, SelD) :-
    pick(Rs, Ss, Es, Ds, Sel, SelE, SelD).
