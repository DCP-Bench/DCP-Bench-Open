% Birthday coins: Tommy was given 15 coins (half-crowns, shillings and sixpences)
% worth 1 pound 5 shillings 6 pence. How many half-crowns did he get?
% The puzzle is fixed by the problem; the instance carries no data.
% coin_value(T, P): coin type T (0 half-crown, 1 shilling, 2 sixpence) is worth P pence.
coin_value(0,30). coin_value(1,12). coin_value(2,6).

% coins(T, V): he was given V coins of type T.
1 { coins(T,V) : V = 0..15 } 1 :- coin_value(T,_).

% The coins are worth 1 pound 5 shillings 6 pence, that is 306 pence.
:- #sum { P*V,T : coin_value(T,P), coins(T,V) } != 306.
% He was given 15 coins.
:- #sum { V,T : coins(T,V) } != 15.

half_crowns(V) :- coins(0,V).
#show half_crowns/1.
