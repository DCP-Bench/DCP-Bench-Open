# session3_kidney_exchange
Instance: `num_people`, `compatible` (1-based donation lists). Output:
`transplants`, a num_people x num_people 0/1 matrix. Maximize transplants:
each person donates at most once and receives at most once, only to a compatible
recipient, and anyone who donates must also receive. With the at-most-one
constraints each row and column sum is 0 or 1, so the implication is the linear
inequality row <= column.
