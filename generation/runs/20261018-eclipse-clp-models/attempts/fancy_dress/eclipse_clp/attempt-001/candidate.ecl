% Fancy dress party (Mr Greenguest): choose green clothing items so that the
% guest follows the dress rules, or pays the entrance fee, at minimum cost.
% Variables (0/1): t tie, h hat, r shirt, s socks, n entrance fee.
% Cost: tie 10, hat 2, socks 12, entrance fee 11, and 9 for a shirt bought
% (he owns one, so the shirt costs 9 only when r = 0).
:- lib(ic).

model(_Instance, [T, H, R, S, N], [t-T, h-H, r-R, s-S, n-N], min(Cost)) :-
    [T, H, R, S, N] :: 0..1,

    % Rule 1: If someone wears a green tie he has to wear a green shirt.
    (T #= 1) => (R #= 1),

    % Rule 2: A guest may only wear green socks and a green shirt if he wears
    % a green tie or a green hat.
    ((S #= 1) and (R #= 1)) => ((T #= 1) or (H #= 1)),

    % Rule 3: A guest wearing a green shirt or a green hat or who does not wear
    % green socks must wear a green tie.
    ((R #= 1) or (H #= 1) or (S #= 0)) => (T #= 1),

    % Rule 4: A guest who is not dressed according to rules 1-3 must pay a
    % $11 entrance fee.
    (N #= 1) <=> neg( ((T #= 1) => (R #= 1)) and
                      (((S #= 1) and (R #= 1)) => ((T #= 1) or (H #= 1))) and
                      (((R #= 1) or (H #= 1) or (S #= 0)) => (T #= 1)) ),

    Cost #= 10*T + 2*H + 12*S + 11*N + 9*(1 - R),
    Cost #>= 0.
