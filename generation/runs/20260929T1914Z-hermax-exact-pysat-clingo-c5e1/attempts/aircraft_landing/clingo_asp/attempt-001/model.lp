% Aircraft landing with a fixed landing order: give every aircraft a landing
% time inside its window so that consecutive landings keep the required
% separation, minimising the penalty for landing before or after the target.
% earliest_landing(I, T), latest_landing(I, T), target_landing(I, T), penalty_before(I, P),
% penalty_after(I, P): the data of aircraft I; separation_time(I, J, S): the gap between I and J.
aircraft(I) :- earliest_landing(I,_).

% landing_times(I, T): aircraft I lands at time T, inside its window.
1 { landing_times(I,T) : earliest_landing(I,E), latest_landing(I,L), T = E..L } 1 :- aircraft(I).

% The landing order is fixed as the aircraft index order (as the problem states), so
% aircraft J lands at least separation_time(I, J) after aircraft I.
:- landing_times(I,TI), landing_times(J,TJ), I < J, separation_time(I,J,S), TJ - TI < S.

% How far before and after its target each aircraft lands.
early(I,G - T) :- landing_times(I,T), target_landing(I,G), T <= G.
late(I,T - G) :- landing_times(I,T), target_landing(I,G), T >= G.

% The total penalty, the declared output, is also what is minimised.
total_penalty(P) :- P = #sum { PB * E,I : early(I,E), penalty_before(I,PB) ; PA * D,I,late : late(I,D), penalty_after(I,PA) }.
#minimize { P : total_penalty(P) }.

#show landing_times/2.
#show total_penalty/1.
