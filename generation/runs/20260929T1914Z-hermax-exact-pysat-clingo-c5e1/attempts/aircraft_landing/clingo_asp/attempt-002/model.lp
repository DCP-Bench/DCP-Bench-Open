% Aircraft landing with a fixed landing order: give every aircraft a landing
% time inside its window so that consecutive landings keep the required
% separation, minimising the penalty for landing before or after the target.
% earliest_landing(I, T), latest_landing(I, T), target_landing(I, T), penalty_before(I, P),
% penalty_after(I, P): the data of aircraft I; separation_time(I, J, S): the gap between I and J.
aircraft(I) :- earliest_landing(I,_).

% Each landing time is written as thresholds: ge(I, T) says aircraft I lands at time T or
% later, for T inside its window after the earliest time; the thresholds are nested.
% This keeps the separation rule below linear in the length of the window, where naming
% every pair of landing times would grow with its square.
window(I,E + 1..L) :- earliest_landing(I,E), latest_landing(I,L).
{ ge(I,T) } :- window(I,T).
:- ge(I,T + 1), not ge(I,T), window(I,T).

% landing_times(I, T): aircraft I lands at time T, the last threshold it reaches.
landing_times(I,E) :- earliest_landing(I,E), not ge(I,E + 1).
landing_times(I,T) :- window(I,T), ge(I,T), not ge(I,T + 1).

% The landing order is fixed as the aircraft index order (as the problem states), so
% aircraft J lands at least separation_time(I, J) after aircraft I: reaching time T for I
% forces J to reach T + S, and no aircraft can reach past the end of its window.
ge(J,T + S) :- ge(I,T), I < J, separation_time(I,J,S), window(J,T + S).
:- ge(I,T), I < J, separation_time(I,J,S), latest_landing(J,L), T + S > L.
% Even at its earliest time, aircraft I forces J to reach earliest(I) + S.
ge(J,E + S) :- earliest_landing(I,E), I < J, separation_time(I,J,S), window(J,E + S).
:- earliest_landing(I,E), I < J, separation_time(I,J,S), latest_landing(J,L), E + S > L.

% Units of earliness and lateness: one for every time step by which the landing is
% before (after) the target time.
early_unit(I,T) :- window(I,T), target_landing(I,G), T <= G, not ge(I,T).
early_unit(I,E + 1..G) :- earliest_landing(I,E), target_landing(I,G), not ge(I,E + 1), E < G.
late_unit(I,T) :- window(I,T), target_landing(I,G), T > G, ge(I,T).

% The total penalty, the declared output, is also what is minimised.
total_penalty(P) :- P = #sum { PB,I,T,early : early_unit(I,T), penalty_before(I,PB) ;
                               PA,I,T,late : late_unit(I,T), penalty_after(I,PA) }.
#minimize { P : total_penalty(P) }.

#show landing_times/2.
#show total_penalty/1.
