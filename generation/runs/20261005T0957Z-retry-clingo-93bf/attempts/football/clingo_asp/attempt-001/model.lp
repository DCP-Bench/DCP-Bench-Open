% Football squad: buy players for as close to GBP 30 million as possible without
% going over, taking the required number from each position and at least eleven
% players in total. The output z is the total price in GBP thousands.
% The players on offer are fixed by the problem (the instance is empty), so their
% prices in GBP thousands are mirrored here: player(P, K, Price) is player P of
% position K (0 goalkeepers, 1 defenders, 2 midfielders, 3 strikers), and
% position(K, Fewest, Most) the numbers to buy there. The players of one position
% have consecutive numbers P, which the squad-building chain below relies on.
budget(30000).
min_players(11).  % at least this many players in all
position(0,1,1). position(1,2,8). position(2,3,10). position(3,2,5).
player(0,0,730).   player(1,0,1280).  player(2,0,3880).
player(3,1,920).   player(4,1,1310).  player(5,1,1620).  player(6,1,2410).  player(7,1,2790).
player(8,1,3280).  player(9,1,3910).  player(10,1,4570).
player(11,2,1800). player(12,2,2630). player(13,2,3170). player(14,2,3769). player(15,2,4140).
player(16,2,4750). player(17,2,5380). player(18,2,5930). player(19,2,6780). player(20,2,7130).
player(21,3,4460). player(22,3,6470). player(23,3,7780). player(24,3,8390). player(25,3,9500).

% buy(P): player P is bought.
{ buy(P) } :- player(P,_,_).

% Why a chain: with one budget sum over the bought players, proving optimality
% means proving by search that no legal squad costs more than the best one
% found while staying within budget, and that proof did not finish in 180 s. Instead the squad is built player by
% player, and the grounder enumerates every (price so far, players so far,
% players so far at this position) that a legal partial squad can reach. Only
% legal complete squads then exist as atoms, so their best total is known to
% the solver as soon as it finds one.

% A position's count only matters up to its lower limit, unless its upper limit
% is below the number of players on offer, in which case it is counted up to
% that limit. The total is counted up to eleven.
size(K,Sz) :- position(K,_,_), Sz = #count { P : player(P,K,_) }.
cap(K,Hi) :- position(K,_,Hi), size(K,Sz), Hi < Sz.
cap(K,Lo) :- position(K,Lo,Hi), size(K,Sz), Hi >= Sz.
pos_next(K,C,C+1) :- cap(K,Cap), C = 0..Cap-1.
pos_next(K,Cap,Cap) :- cap(K,Cap).
total_next(N,N+1) :- min_players(M), N = 0..M-1.
total_next(M,M) :- min_players(M).

% first(P): P is the first player of its position; last(P): the last player on offer.
first(P) :- player(P,K,_), not player(P-1,K,_).
last(P) :- player(P,_,_), not player(P+1,_,_).

% before(P,S,N,C): the players before P cost S, number N in all and C at P's
% position. At the first player of a position, the previous position must have
% its fewest players bought, and the count at the new position starts at 0.
before(0,0,0,0).
before(P,S,N,0) :- after(P-1,S,N,C), first(P), P > 0,
                   player(P-1,K,_), position(K,Lo,_), C >= Lo.
before(P,S,N,C) :- after(P-1,S,N,C), player(P,_,_), not first(P).

% after(P,S,N,C): the same once player P is decided. Buying P keeps the price
% within the budget and the count at P's position within its upper limit.
after(P,S,N,C) :- before(P,S,N,C), not buy(P).
after(P,S+Pr,N2,C2) :- before(P,S,N,C), buy(P), player(P,K,Pr), budget(B), S + Pr <= B,
                       position(K,_,Hi), C < Hi, pos_next(K,C,C2), total_next(N,N2).

% A complete squad: the last position has its fewest players and at least eleven
% players are bought. Its price is z, which the bought squad must have.
z(S) :- after(L,S,N,C), last(L), player(L,K,_), position(K,Lo,_), C >= Lo,
        min_players(M), N >= M.
squad :- z(_).
:- not squad.

% The total price is as large as possible. It is stated through the thresholds
% ge(V), "the total is at least V", one per unit, so the objective's largest
% possible value is the largest total a legal squad can reach and the solver
% sees the optimum is proven once it finds that total.
ge(S) :- z(S).
ge(V-1) :- ge(V), V > 1.
#maximize { 1,V : ge(V) }.

% Which players are bought is not part of the answer, so solutions are projected onto z.
#project z/1.
#show z/1.
