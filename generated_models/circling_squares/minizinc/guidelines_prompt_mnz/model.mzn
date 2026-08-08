
% Circling the Squares Puzzle in MiniZinc
% Place different numbers in 10 squares A, B, C, D, E, F, G, H, I, K
% so that for every two adjacent squares, the sum of their squares
% equals the sum of the squares of the two squares diametrically opposite.

int: n = 10;

% Variables for the 10 positions (1:A, 2:B, 3:C, 4:D, 5:E, 6:F, 7:G, 8:H, 9:I, 10:K)
array[1..n] of var 1..99: X;

% Given values
constraint X[1] = 16;  % A
constraint X[2] = 2;   % B
constraint X[6] = 8;   % F
constraint X[7] = 14;  % G

% All numbers must be different
constraint
    all_different(X);

% Define a function to get the diametrically opposite index on a circle of size n=10
function int: opp(int: i) = if i <= 5 then i + 5 else i - 5 endif;

% For each adjacent pair (i, i+1) around the circle, enforce:
% X[i]^2 + X[i+1]^2 = X[opp(i)]^2 + X[opp(i+1)]^2
constraint
    forall(i in 1..n) (
        let {
            int: j = if i < n then i + 1 else 1 endif,
            int: oi = opp(i),
            int: oj = opp(j)
        } in
        X[i] * X[i] + X[j] * X[j] = X[oi] * X[oi] + X[oj] * X[oj]
    );

solve satisfy;

% Output the solution in JSON format with keys A, B, C, D, E, F, G, H, I, K
output [
    "{",
    join(",", [
        "\"A\": " ++ show(X[1]),
        "\"B\": " ++ show(X[2]),
        "\"C\": " ++ show(X[3]),
        "\"D\": " ++ show(X[4]),
        "\"E\": " ++ show(X[5]),
        "\"F\": " ++ show(X[6]),
        "\"G\": " ++ show(X[7]),
        "\"H\": " ++ show(X[8]),
        "\"I\": " ++ show(X[9]),
        "\"K\": " ++ show(X[10])
    ]),
    "}"
];
