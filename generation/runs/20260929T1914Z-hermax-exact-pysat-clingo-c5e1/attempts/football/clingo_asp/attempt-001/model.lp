% Football squad: buy players for as close to GBP 30 million as possible without
% going over, taking the required number from each position and at least eleven
% players in total. The output is the total price in GBP thousands.
% The players on offer are fixed by the problem, so their prices (in GBP thousands) are
% mirrored here: player(P, K, Price) is player P of position K (0 goalkeepers, 1 defenders,
% 2 midfielders, 3 strikers), and position(K, Fewest, Most) the numbers to buy there.
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

% The number of players bought at each position lies within its limits.
:- position(K,Low,High), #count { P : buy(P), player(P,K,_) } < Low.
:- position(K,Low,High), #count { P : buy(P), player(P,K,_) } > High.

% At least eleven players in total.
:- min_players(M), #count { P : buy(P) } < M.

% z: the total price paid, which stays within the budget and is maximised.
z(Z) :- Z = #sum { Price,P : buy(P), player(P,_,Price) }.
:- z(Z), budget(B), Z > B.
#maximize { Z : z(Z) }.

#show z/1.
