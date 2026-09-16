% The zebra puzzle: five houses, and five attributes per house. Every value is
% a house number 0..4, so two attributes sharing a number share a house.
house(0..4).
idx(0..4).

1 { colors(I,H) : house(H) } 1 :- idx(I).
1 { nations(I,H) : house(H) } 1 :- idx(I).
1 { jobs(I,H) : house(H) } 1 :- idx(I).
1 { pets(I,H) : house(H) } 1 :- idx(I).
1 { drinks(I,H) : house(H) } 1 :- idx(I).

:- colors(I,H), colors(J,H), I < J.
:- nations(I,H), nations(J,H), I < J.
:- jobs(I,H), jobs(J,H), I < J.
:- pets(I,H), pets(J,H), I < J.
:- drinks(I,H), drinks(J,H), I < J.

% colors: yellow green red white blue ; nations: italy spain japan england norway
% jobs: painter sculptor diplomat pianist doctor ; pets: cat zebra bear snails horse
% drinks: milk water tea coffee juice
:- jobs(0,P), pets(4,H), P != H.        % the painter owns the horse
:- jobs(2,D), drinks(3,C), D != C.      % the diplomat drinks coffee
:- colors(3,W), drinks(0,M), W != M.    % milk is drunk in the white house
:- nations(1,S), jobs(0,P), S != P.     % the Spaniard is a painter
:- nations(3,E), colors(2,R), E != R.   % the Englishman is in the red house
:- pets(3,S), jobs(1,C), S != C.        % the snails belong to the sculptor
:- colors(1,G), colors(2,R), R != G + 1.   % green immediately left of red
:- colors(4,B), nations(4,N), N != B + 1.  % Norwegian immediately right of blue
:- jobs(4,D), drinks(0,M), D != M.      % the doctor drinks milk
:- nations(2,J), jobs(2,D), J != D.     % the diplomat is Japanese
:- nations(4,N), pets(1,Z), N != Z.     % the Norwegian owns the zebra
:- colors(1,G), colors(3,W), |G - W| != 1.        % green next to white
:- pets(4,H), jobs(2,D), |H - D| != 1.            % horse next to the diplomat
:- nations(0,I), colors(2,R), colors(3,W), colors(1,G), I != R, I != W, I != G.

#show colors/2.
#show nations/2.
#show jobs/2.
#show pets/2.
#show drinks/2.
