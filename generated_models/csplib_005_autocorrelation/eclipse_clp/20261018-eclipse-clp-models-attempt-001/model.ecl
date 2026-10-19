% CSPLib 005: periodic autocorrelation of a binary sequence.
% Find a sequence of n bits, each +1 or -1, that minimises the sum of the
% squares of its periodic autocorrelations C_k for k = 1 .. n-1.

:- lib(ic).

% A binary sequence of length n, each bit takes the value +1 or -1.
% Bits are coded as 0/1 booleans b_i, with s_i = 2*b_i - 1.
model(Instance, Bs, [sequence-Xs], min(Cost)) :-
    memberchk(n-N, Instance),
    length(Bs, N),
    Bs :: 0..1,
    ( foreach(B, Bs), foreach(X, Xs) do
        X #= 2*B - 1
    ),

    % The periodic k-th autocorrelation C_k = sum_{i=0}^{n-1} S_i * S_{(i+k) mod n}.
    % For +-1 bits, S_i * S_j is 1 when the bits are equal and -1 otherwise,
    % so each product is 2*[b_i = b_j] - 1 and C_k is linear in the equality booleans.
    % The rotation of the sequence by k gives the partner S_{(i+k) mod n} at position i.
    ( for(K, 1, N-1), foreach(Sq, Sqs), param(Bs, N) do
        length(H, K),
        append(H, T, Bs),
        append(T, H, Rot),
        ( foreach(B1, Bs), foreach(B2, Rot), foreach(E, Es) do
            E #= (B1 #= B2)
        ),
        C #= 2*sum(Es) - N,

        % The objective: minimise the sum of the squares of the C_k.
        Sq #= C*C
    ),
    Cost #= sum(Sqs).
