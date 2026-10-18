% initials_queue: the initials of the first ten people in a queue for a Maths lecture.
% Each person's initials are an alphabetically ordered pair of distinct letters from A to E,
% coded 0 (A) to 4 (E). The output queue lists the ten pairs from the front of the queue.
:- lib(ic).

model(_Instance, Vars, [queue-Rows]) :-
    Rows = [[X1,Y1],[X2,Y2],[X3,Y3],[X4,Y4],[X5,Y5],
            [X6,Y6],[X7,Y7],[X8,Y8],[X9,Y9],[X10,Y10]],
    Vars = [X1,Y1,X2,Y2,X3,Y3,X4,Y4,X5,Y5,X6,Y6,X7,Y7,X8,Y8,X9,Y9,X10,Y10],
    Vars :: 0..4,

    % each person's initials are a pair of distinct letters in alphabetical order
    ( foreach([X,Y], Rows) do X #< Y ),

    % no two people have the same initials (pair code 5*first + second is unique)
    ( foreach([X,Y], Rows), foreach(Code, Codes) do Code #= 5*X + Y ),
    alldifferent(Codes),

    % no-one shares a letter with the person in front of them
    no_shared_letter(Rows),

    % Mathematician BE was at the front of the queue (B=1, E=4)
    X1 #= 1, Y1 #= 4,
    % CD was right behind (C=2, D=3)
    X2 #= 2, Y2 #= 3,
    % BD was right at the end of the queue (B=1, D=3)
    X10 #= 1, Y10 #= 3.

no_shared_letter([]).
no_shared_letter([_]).
no_shared_letter([[A,B],[C,D]|Rest]) :-
    A #\= C, A #\= D, B #\= C, B #\= D,
    no_shared_letter([[C,D]|Rest]).
