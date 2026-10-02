% Big Bang 2: five non-transitive dice that play Rock-Paper-Scissors-Lizard-Spock. Each die has
% six faces with values from 1 to 12. One die beats another when it shows the larger value in
% more than half of all pairs of faces. The dice must beat each other exactly as the ten
% "beats" relations of the game say.
% The numbers of dice and faces, the face values and the ten relations belong to the problem
% statement (there is no instance data).

#const rock = 0.
#const paper = 1.
#const scissors = 2.
#const lizard = 3.
#const spock = 4.

die(rock..spock).
faces(6).
face(0..N-1) :- faces(N).
value(1..12).

% The ten relations of the game: beats(W, L) means die W must beat die L.
beats(rock, scissors).      % Rock crushes Scissors
beats(rock, lizard).        % Rock crushes Lizard
beats(paper, rock).         % Paper covers Rock
beats(paper, spock).        % Paper disproves Spock
beats(scissors, paper).     % Scissors cuts Paper
beats(scissors, lizard).    % Scissors decapitates Lizard
beats(lizard, paper).       % Lizard eats Paper
beats(lizard, spock).       % Lizard poisons Spock
beats(spock, rock).         % Spock vaporizes Rock
beats(spock, scissors).     % Spock smashes Scissors

% dice(D, F, V): face F of die D shows the value V. Face values may repeat.
1 { dice(D,F,V) : value(V) } 1 :- die(D), face(F).

% A die beats another one when it wins in more than half of all pairs of faces: more than
% faces * faces / 2 of the pairs (face X of the winner, face Y of the loser) have the winner's
% value larger.
half(H) :- faces(N), H = (N * N) / 2.
:- beats(W,L), half(H),
   #count { X,Y : dice(W,X,VW), dice(L,Y,VL), VW > VL } <= H.

#show dice/3.
