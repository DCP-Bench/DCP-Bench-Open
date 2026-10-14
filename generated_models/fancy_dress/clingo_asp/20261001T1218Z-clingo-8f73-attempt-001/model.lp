% Fancy dress: Mr Greenguest wants to join a party where guests must wear green. He owns a green
% shirt and can buy a green tie ($10), a green hat ($2) and green socks ($12). A guest who breaks
% one of three dress rules pays an $11 entrance fee. Find the cheapest way to take part.
% Prices and rules belong to the problem statement (there is no instance data).

% What he wears and whether he pays the entrance fee.
{ tie; hat; shirt; socks; fee }.

% Rule 1: a green tie requires a green shirt, unless the entrance fee is paid.
:- tie, not shirt, not fee.

% Rule 2: green socks or a green shirt require a green tie or a green hat, unless the fee is paid.
:- socks, not tie, not hat, not fee.
:- shirt, not tie, not hat, not fee.

% Rule 3: a green shirt, a green hat, or no green socks require a green tie, unless the fee is paid.
:- shirt, not tie, not fee.
:- hat, not tie, not fee.
:- not socks, not tie, not fee.

% Cost: tie 10, hat 2, socks 12, entrance fee 11. The shirt is already owned, so it costs nothing.
#minimize { 10,tie : tie; 2,hat : hat; 12,socks : socks; 11,fee : fee }.

% The answer is reported as Boolean values t (tie), h (hat), r (shirt), s (socks), n (entrance fee).
t(true) :- tie.
t(false) :- not tie.
h(true) :- hat.
h(false) :- not hat.
r(true) :- shirt.
r(false) :- not shirt.
s(true) :- socks.
s(false) :- not socks.
n(true) :- fee.
n(false) :- not fee.

#show t/1.
#show h/1.
#show r/1.
#show s/1.
#show n/1.
