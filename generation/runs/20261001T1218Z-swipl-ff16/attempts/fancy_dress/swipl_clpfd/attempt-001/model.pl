:- use_module(library(clpfd)).

% Fancy dress: Mr Greenguest wants to join a party where male guests wear green
% dresses. He picks which of a green tie (t), hat (h), shirt (r) and socks (s)
% to wear and whether he pays the entrance fee (n), so that the three dress
% rules hold (or the fee is paid), at the lowest total cost. The problem has no
% instance data; the prices are the ones in the statement: tie 10, hat 2,
% socks 12, entrance fee 11. The shirt is already owned, so it costs nothing.
% Every choice is 0 or 1 (1 = wears green / pays the fee).
model(_Instance, Vars, [h-H, n-N, r-R, s-S, t-T], min(10*T + 2*H + 12*S + 11*N)) :-
    Vars = [T, H, R, S, N],
    Vars ins 0..1,

    % Rule 1: a green tie requires a green shirt, unless the fee is paid.
    (T #==> R) #\/ N,

    % Rule 2: green socks or a green shirt are only allowed together with a
    % green tie or a green hat, unless the fee is paid.
    ((S #\/ R) #==> (T #\/ H)) #\/ N,

    % Rule 3: a guest in a green shirt or a green hat, or without green socks,
    % must wear a green tie, unless the fee is paid.
    (R #\/ H #\/ #\ S) #==> (T #\/ N).
