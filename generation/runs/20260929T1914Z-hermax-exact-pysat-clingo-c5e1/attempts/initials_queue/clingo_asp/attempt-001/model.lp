% Initials queue: the ten people in a queue have as initials the ten different
% alphabetically ordered pairs of distinct letters from A-E, no one shares a
% letter with the person in front, BE is first, CD second and BD last.
% queue(I, K, V): the K-th letter (0 or 1) of the I-th person is V, with A..E
% coded 0..4.
1 { queue(I,K,V) : V = 0..4 } 1 :- I = 0..9, K = 0..1.

% The two letters of a person are in alphabetical order, so they are different.
:- queue(I,0,A), queue(I,1,B), A >= B.

% Nobody has the same initials as anybody else.
:- queue(I,0,A), queue(I,1,B), queue(J,0,A), queue(J,1,B), I < J.

% Nobody shares a letter with the person in front.
:- queue(I,K,V), queue(I+1,L,V).

% BE is at the front, CD right behind, BD at the end.
given(0,0,1). given(0,1,4).
given(1,0,2). given(1,1,3).
given(9,0,1). given(9,1,3).
:- given(I,K,V), not queue(I,K,V).

#show queue/3.
