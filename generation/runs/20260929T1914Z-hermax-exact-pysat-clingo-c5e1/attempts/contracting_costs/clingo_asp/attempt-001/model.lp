% Contracting costs: six tradesmen are paid in pairs, and the payments to each
% pair are known. Find what each man charges.
% The puzzle is fixed by the problem; the instance carries no data.
% pay(A, B, D): the men A and B are paid D dollars together.
pay(paper_hanger,painter,1100).
pay(painter,plumber,1700).
pay(plumber,electrician,1100).
pay(electrician,carpenter,3300).
pay(carpenter,mason,5300).
pay(mason,painter,3200).
man(M) :- pay(M,_,_).
man(M) :- pay(_,M,_).

% charge(M, V): the man M charges V dollars, between 1 and 5300.
1 { charge(M,V) : V = 1..5300 } 1 :- man(M).

% The two men of a pair are paid the given amount together.
:- pay(A,B,D), #sum { V,A : charge(A,V); V,B : charge(B,V) } != D.

% The answer: one atom per man, paper_hanger(V), painter(V), ...
paper_hanger(V) :- charge(paper_hanger,V).
painter(V) :- charge(painter,V).
plumber(V) :- charge(plumber,V).
electrician(V) :- charge(electrician,V).
carpenter(V) :- charge(carpenter,V).
mason(V) :- charge(mason,V).
#show paper_hanger/1.
#show painter/1.
#show plumber/1.
#show electrician/1.
#show carpenter/1.
#show mason/1.
