% N-puzzle: slide tiles on a square grid, one move per step, to get from the start board to the
% end board in exactly n_steps boards (start and end included). The board must change every step.
% Instance facts: n_STEPS(N); puzzle_start(I,J,V) and puzzle_end(I,J,V): tile V (0 = empty) at row I, column J.
cell(I,J) :- puzzle_start(I,J,_).
time(0..N-1) :- n_STEPS(N).

% Two cells are neighbours when they are one row or one column apart.
neighbour(I,J,I+DI,J+DJ) :- cell(I,J), cell(I+DI,J+DJ), |DI| + |DJ| == 1, DI = -1..1, DJ = -1..1.

% Start state: the board at step 0 is the start board.
steps(0,I,J,V) :- puzzle_start(I,J,V).

% blank(T,I,J): the empty tile is at (I,J) at step T.
blank(0,I,J) :- puzzle_start(I,J,0).

% Transition: at every step the empty tile moves to one neighbouring cell (so the board always
% changes and the empty tile never stays put).
1 { blank(T,I2,J2) : neighbour(I1,J1,I2,J2) } 1 :- time(T), T > 0, blank(T-1,I1,J1).

% The tile that was in the cell the empty tile moves to takes the cell the empty tile leaves.
steps(T,I1,J1,V) :- time(T), T > 0, blank(T-1,I1,J1), blank(T,I2,J2), steps(T-1,I2,J2,V).
% The empty tile is in its new cell.
steps(T,I,J,0) :- time(T), T > 0, blank(T,I,J).
% Every other tile stays where it was.
steps(T,I,J,V) :- time(T), T > 0, steps(T-1,I,J,V), not blank(T-1,I,J), not blank(T,I,J).

% End state: the board at the last step is the end board.
:- n_STEPS(N), puzzle_end(I,J,V), not steps(N-1,I,J,V).

#show steps/4.
