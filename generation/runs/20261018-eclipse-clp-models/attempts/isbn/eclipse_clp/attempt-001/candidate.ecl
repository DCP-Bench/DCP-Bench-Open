% ISBN-13 validation and check digit calculation.
% Given 13 digits where -1 marks an unknown digit, find the unknown digits so that
% the number is a valid ISBN-13.

:- lib(ic).

model(Instance, Xs, [isbn-Xs]) :-
    memberchk(isbn_init-Init, Instance),
    length(Xs, 13),
    Xs :: 0..9,

    % Given digits are fixed; unknown digits (-1) stay free.
    ( foreach(X, Xs), foreach(D, Init) do
        ( D < 0 -> true ; X #= D )
    ),

    % An ISBN-13 must start with 978 or 979.
    Xs = [X1, X2, X3, X4, X5, X6, X7, X8, X9, X10, X11, X12, X13],
    X1 #= 9,
    X2 #= 7,
    X3 :: [8, 9],

    % Multiply the first 12 digits alternately by 1 and 3 (starting with 1).
    % Sum the products.
    % The check digit is (10 - (sum % 10)) % 10.
    Sum :: 0..200,
    Sum #= X1 + 3*X2 + X3 + 3*X4 + X5 + 3*X6 + X7 + 3*X8 + X9 + 3*X10 + X11 + 3*X12,
    % sum % 10, then (10 - that) % 10, each as its own constraint.
    R :: 0..9,
    R #= Sum mod 10,
    T :: 0..10,
    T #= 10 - R,
    X13 #= T mod 10.
