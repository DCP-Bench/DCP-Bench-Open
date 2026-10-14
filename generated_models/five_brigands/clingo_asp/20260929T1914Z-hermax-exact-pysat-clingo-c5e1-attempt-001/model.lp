% Five brigands: Alfonso, Benito, Carlos, Diego and Esteban share 200 doubloons,
% each has at least one, and the total would still be 200 if Alfonso had twelve
% times as much, Benito three times, Carlos the same, Diego half and Esteban a third.
% The puzzle is fixed by the problem; the instance carries no data.
% a(V), b(V), c(V), d(V), e(V): the brigand has V doubloons.
1 { a(V) : V = 1..200 } 1.
1 { b(V) : V = 1..200 } 1.
1 { c(V) : V = 1..200 } 1.
1 { d(V) : V = 1..200 } 1.
1 { e(V) : V = 1..200 } 1.

% Together they have 200 doubloons.
:- #sum { V,a : a(V); V,b : b(V); V,c : c(V); V,d : d(V); V,e : e(V) } != 200.

% With the changed amounts they would still have 200: 12A + 3B + C + D/2 + E/3 = 200,
% multiplied by 6 to get whole numbers.
:- #sum { 72*V,a : a(V); 18*V,b : b(V); 6*V,c : c(V); 3*V,d : d(V); 2*V,e : e(V) } != 1200.

#show a/1.
#show b/1.
#show c/1.
#show d/1.
#show e/1.
