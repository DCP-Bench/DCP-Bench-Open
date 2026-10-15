# huey_dewey_louie plan

Each statement is true, because the three cub scouts cannot tell a lie.

- Huey: "Dewey and Louie has equal share in it; if one is guilty, so is the other." -> Iff(dewey, louie)
- Dewey: "If Huey is guilty, then so am I." -> If(huey, dewey)
- Louie: "Dewey and I are not both guilty." -> ~(dewey & louie)
- Output: dewey, huey, louie as Bools. Satisfaction problem, no objective.
