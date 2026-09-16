% People in a room: order the arrivals so the ratio of females to males never
% exceeds seven to three. A 1 is a female arrival.
arrival(0..12).
who(0..1).

1 { sequence(I,V) : who(V) } 1 :- arrival(I).

:- not 9 = #count { I : sequence(I,1) }.

% Over the first I arrivals, 3F <= 7M with M = I - F, which is 10F <= 7I.
females(I,F) :- arrival(I), F = #count { J : sequence(J,1), J < I }.
:- females(I,F), I > 0, 10 * F > 7 * I.

#show sequence/2.
