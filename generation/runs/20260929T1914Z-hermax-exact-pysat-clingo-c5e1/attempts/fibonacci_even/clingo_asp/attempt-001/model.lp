% Fibonacci even: add up the even-valued terms of the Fibonacci sequence that do
% not exceed four million.
% The puzzle is fixed by the problem; the instance carries no data.
% fib(I, F): the I-th Fibonacci number is F: fib(1) = fib(2) = 1, then the sum of the
% previous two; the terms considered are the first 35, the largest is below 10 million.
fib(1,1). fib(2,1).
fib(I,A+B) :- fib(I-1,A), fib(I-2,B), I = 3..35.

% res(S): the sum of the even terms below four million.
res(S) :- S = #sum { F,I : fib(I,F), F \ 2 = 0, F < 4000000 }.
#show res/1.
