p9 :-
    argv(all, All),
    ( append(_, ["--", F|_], All) -> writeln(found(F)) ; writeln(notfound) ),
    ( append(_, [X, F2|_], All), X == "--" -> writeln(found2(F2)) ; writeln(notfound2) ),
    ( append(_, [X3|_], All), string_length(X3, 2), writeln(len2(X3)), fail ; true ).

:- p9.
