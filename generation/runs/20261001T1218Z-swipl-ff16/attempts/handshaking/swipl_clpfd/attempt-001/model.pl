:- use_module(library(clpfd)).
:- use_module(library(apply)).
:- use_module(library(lists)).

% Handshaking: Hilary and Jocelyn (a couple) host some other couples. Nobody
% shakes hands with themselves or their spouse, and everybody except Hilary has
% shaken a different number of hands. How many hands did Hilary shake?
model(Instance, Vars, [hil-Hil]) :-
    NumCouples = Instance.num_couples,      % couples invited, besides the hosts
    N is 2 + NumCouples * 2,                % people at the party
    MaxHands is N - 2,                      % nobody shakes own or spouse's hand

    % Hands[i] is how many hands person i has shaken. Person 1 is Hilary,
    % person 2 is Jocelyn, and the guests follow couple by couple: persons
    % 2c-1 and 2c are spouses.
    length(Hands, N),
    Hands ins 0..MaxHands,
    Hands = [Hil|Answers],
    % all the answers except Hilary's are different
    all_distinct(Answers),

    % Shake[i][j] is 1 when persons i and j shook hands. It is stated once per
    % pair: Shake[i][j] and Shake[j][i] are the same variable, which is the
    % requirement that a handshake is mutual.
    length(Shake, N),
    maplist({N}/[Row]>>(length(Row, N), Row ins 0..1), Shake),
    numlist(1, N, People),
    findall(I-J, (member(I, People), member(J, People), I < J), Pairs),
    maplist({Shake}/[I-J]>>(cell(Shake, I, J, Cell), cell(Shake, J, I, Cell)), Pairs),
    % nobody shakes their own hand
    maplist({Shake}/[I]>>cell(Shake, I, I, 0), People),
    % nobody shakes hands with their spouse
    Couples is N // 2,
    numlist(1, Couples, CoupleNumbers),
    maplist({Shake}/[C]>>(A is 2 * C - 1, B is 2 * C,
                          cell(Shake, A, B, 0), cell(Shake, B, A, 0)),
            CoupleNumbers),
    % the number of hands a person shook is the number of people they shook
    % hands with
    maplist([Row, Count]>>sum(Row, #=, Count), Shake, Hands),

    % Symmetry breaking (not part of the problem statement). Guests of one
    % couple can swap names, and the couples can swap places, without changing
    % what Hilary shook: there are NumCouples! * 2^NumCouples renamings of the
    % same party. Since all guests have different counts, fix one of them: in
    % each couple the first has fewer handshakes than the second, and the
    % couples come in the order of their first member's count. The driver only
    % stops once every solution is exhausted, so without this it would revisit
    % the same party under every renaming.
    Answers = [_|Guests],
    guest_order(Guests),

    append(Shake, Cells),
    append(Hands, Cells, Vars).

% cell(+Matrix, +I, +J, ?Value): Value is entry (I, J) of the matrix.
cell(Matrix, I, J, Value) :-
    nth1(I, Matrix, Row),
    nth1(J, Row, Value).

% guest_order(+Counts): Counts lists the guests couple by couple; each couple's
% first count is below its second and below the next couple's first.
guest_order([]).
guest_order([First, Second|Rest]) :-
    First #< Second,
    (   Rest = [NextFirst|_]
    ->  First #< NextFirst
    ;   true
    ),
    guest_order(Rest).
