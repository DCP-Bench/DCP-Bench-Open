% General store puzzle: give each letter of the words C H E S A B O W P L a
% different decimal digit so that the words above the line add up to ALL WOOL.
% The output names are the letters of the problem statement.

:- lib(ic).

model(_Instance, Vars, Outputs) :-
    Vars = [C, H, E, S, A, B, O, W, P, L],
    Vars :: 0..9,
    % Each different letter stands for a different digit.
    alldifferent(Vars),

    % The words above the horizontal line, each read as the number its digits spell.
    NChess   :: 0..99999,
    NCash    :: 0..9999,
    NBowwow  :: 0..999999,
    NChops   :: 0..99999,
    NAlsops  :: 0..999999,
    NPaleale :: 0..9999999,
    NCool    :: 0..9999,
    NBass    :: 0..9999,
    NHops    :: 0..9999,
    NAles    :: 0..9999,
    NHoes    :: 0..9999,
    NApples  :: 0..999999,
    NCows    :: 0..9999,
    NCheese  :: 0..999999,
    NChsoap  :: 0..999999,
    NSheep   :: 0..99999,
    NAllwool :: 0..9999999,
    NChess   #= 10000*C + 1000*H + 100*E + 10*S + S,
    NCash    #= 1000*C + 100*A + 10*S + H,
    NBowwow  #= 100000*B + 10000*O + 1000*W + 100*W + 10*O + W,
    NChops   #= 10000*C + 1000*H + 100*O + 10*P + S,
    NAlsops  #= 100000*A + 10000*L + 1000*S + 100*O + 10*P + S,
    NPaleale #= 1000000*P + 100000*A + 10000*L + 1000*E + 100*A + 10*L + E,
    NCool    #= 1000*C + 100*O + 10*O + L,
    NBass    #= 1000*B + 100*A + 10*S + S,
    NHops    #= 1000*H + 100*O + 10*P + S,
    NAles    #= 1000*A + 100*L + 10*E + S,
    NHoes    #= 1000*H + 100*O + 10*E + S,
    NApples  #= 100000*A + 10000*P + 1000*P + 100*L + 10*E + S,
    NCows    #= 1000*C + 100*O + 10*W + S,
    NCheese  #= 100000*C + 10000*H + 1000*E + 100*E + 10*S + E,
    NChsoap  #= 100000*C + 10000*H + 1000*S + 100*O + 10*A + P,
    NSheep   #= 10000*S + 1000*H + 100*E + 10*E + P,
    NAllwool #= 1000000*A + 100000*L + 10000*L + 1000*W + 100*O + 10*O + L,

    % The words above the line add up to the total ALL WOOL.
    NChess + NCash + NBowwow + NChops + NAlsops + NPaleale + NCool + NBass
        + NHops + NAles + NHoes + NApples + NCows + NCheese + NChsoap + NSheep
        #= NAllwool,

    Outputs = ['A'-A, 'B'-B, 'C'-C, 'E'-E, 'H'-H, 'L'-L, 'O'-O, 'P'-P, 'S'-S, 'W'-W].

search_goal(Vars) :-
    search(Vars, 0, first_fail, indomain_min, complete, []).
