% Handshaking: Hilary and Jocelyn are married and invite some couples to dinner. Everyone shakes
% hands with some of the others, but nobody with themselves or their spouse. Jocelyn asks how many
% hands each person has shaken and all the answers are different. How many hands has Hilary shaken?
% Instance facts: num_couples(C), the couples invited, not counting Hilary and Jocelyn.
% People are numbered 0..N-1 with N = 2 + 2C; the two spouses of a couple are 2K and 2K+1,
% Hilary is person 0 and Jocelyn person 1.
person(0..2 * C + 1) :- num_couples(C).

% spouses(I, J): I and J are married to each other.
spouses(I,I + 1) :- person(I), I \ 2 == 0.
spouses(J,I) :- spouses(I,J).

% shake(I, J): persons I and J shake hands, for I < J and not spouses. Shaking is mutual,
% so the pair is listed once and hand(I, J) holds for both directions.
{ shake(I,J) } :- person(I), person(J), I < J, not spouses(I,J).
hand(I,J) :- shake(I,J).
hand(J,I) :- shake(I,J).

% x(I, D): person I has shaken D hands. Nobody shakes hands with themselves or their
% spouse, so D is at most N - 2 (that is 2C).
x(I,D) :- person(I), D = #count { J : hand(I,J) }.

% Everybody except Hilary has shaken a different number of hands.
:- x(I,D), x(J,D), 1 <= I, I < J.

% The N - 1 people other than Hilary have different numbers of hands, chosen among the N - 1
% values 0..N-2, so every value is taken by exactly one of them. This follows from the
% constraint above; it is stated because the solver cannot see this counting argument.
1 { x(I,D) : person(I), I >= 1 } 1 :- num_couples(C), D = 0..2 * C.

% The couples can be renamed without changing any answer, so only one naming is searched: in
% each couple other than Hilary and Jocelyn the person with the even number has shaken more
% hands than their spouse, and the couples are listed by decreasing number of hands of that
% person. This leaves Hilary's number of hands unchanged.
:- x(I,D), x(I + 1,E), I >= 2, I \ 2 == 0, D < E.
:- x(I,D), x(I + 2,E), I >= 2, I \ 2 == 0, D < E.

% hil: the number of hands Hilary has shaken.
hil(D) :- x(0,D).

% The handshakes themselves are not part of the answer; project the solutions onto hil so
% that equivalent handshake patterns are not enumerated one by one.
#project hil/1.
#show hil/1.
