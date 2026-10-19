% session3_people_in_a_room: 13 people, 4 male, 9 female, enter a room one at a time.
% Find an order of entry such that the ratio of females to males in the room at any
% one time is no greater than 7/3. Output sequence: 0 for male, 1 for female.

:- lib(ic).

model(_Instance, Xs, [sequence-Xs]) :-
    % There are 13 people. 4 of them are male.
    length(Xs, 13),
    Xs :: 0..1,
    sum(Xs) #= 9,

    % The ratio of females to males in the room at any one time is no greater than 7/3.
    % With F females and M males in the room, F/M <= 7/3 is 3F <= 7M, and with
    % K = F + M people in the room, M = K - F, so 10F <= 7K at every prefix.
    prefix_ratio_ok(Xs, 0, 0).

prefix_ratio_ok([], _, _).
prefix_ratio_ok([X|Xs], K, Acc) :-
    K1 is K + 1,
    Acc1 #= Acc + X,
    10 * Acc1 #=< 7 * K1,
    prefix_ratio_ok(Xs, K1, Acc1).
