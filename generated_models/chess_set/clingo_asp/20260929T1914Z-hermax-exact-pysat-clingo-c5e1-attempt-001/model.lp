% Chess set: a joinery makes small and large boxwood chess sets. Decide how
% many of each to make in a week so that the lathe hours and the boxwood are not
% exceeded and the profit is as large as possible.
% The problem statement fixes all the numbers; the instance carries no data.

% Number of small and large sets made per week (at most 100 of each is ever useful).
1 { small_set(N) : N = 0..100 } 1.
1 { large_set(N) : N = 0..100 } 1.

% Boxwood: a small set needs 1 kg, a large one 3 kg, and only 200 kg is available.
:- small_set(S), large_set(L), S + 3 * L > 200.
% Lathe hours: 3 hours per small set, 2 per large set, 4 lathes x 40 hours = 160 hours.
:- small_set(S), large_set(L), 3 * S + 2 * L > 160.

% Profit: $5 per small set and $20 per large set; it is what is maximised.
max_profit(5 * S + 20 * L) :- small_set(S), large_set(L).
#maximize { P : max_profit(P) }.

#show small_set/1.
#show large_set/1.
#show max_profit/1.
