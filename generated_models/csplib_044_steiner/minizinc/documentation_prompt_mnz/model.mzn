include "globals.mzn";

% Input data
int: n = 9;

% Number of triples
int: num_triples = n * (n - 1) div 6;

% Each triple has 3 distinct elements from 1..n
array[1..num_triples, 1..3] of var 1..n: triples;

% Constraints

% 1) Each triple has distinct elements
constraint
  forall(t in 1..num_triples) (
    alldifferent([triples[t, i] | i in 1..3])
  );

% 2) For any two distinct triples, they share at most one element
constraint
  forall(t1, t2 in 1..num_triples where t1 < t2) (
    let {
      array[1..3] of var bool: in_t2 = [exists(i2 in 1..3)(triples[t1,i1] = triples[t2,i2]) | i1 in 1..3]
    } in
      sum([bool2int(in_t2[i]) | i in 1..3]) <= 1
  );

% 3) To avoid symmetries, enforce triples sorted internally
constraint
  forall(t in 1..num_triples) (
    triples[t,1] < triples[t,2] /\ triples[t,2] < triples[t,3]
  );

% 4) To avoid symmetries, enforce triples sorted lex order
constraint
  forall(t in 1..num_triples-1) (
    (triples[t,1] < triples[t+1,1]) \/
    (triples[t,1] = triples[t+1,1] /\ triples[t,2] < triples[t+1,2]) \/
    (triples[t,1] = triples[t+1,1] /\ triples[t,2] = triples[t+1,2] /\ triples[t,3] < triples[t+1,3])
  );

solve satisfy;

output [
  "{\n",
  "  \"triples\": [\n",
  join(",\n", [
    "    [" ++ show(triples[t,1]) ++ "," ++ show(triples[t,2]) ++ "," ++ show(triples[t,3]) ++ "]"
    | t in 1..num_triples
  ]),
  "\n  ]\n",
  "}"
];