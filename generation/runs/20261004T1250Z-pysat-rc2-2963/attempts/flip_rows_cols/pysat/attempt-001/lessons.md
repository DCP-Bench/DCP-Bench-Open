`PBEnc.geq/leq` raise `Wrong bound: -90` for a negative bound even though negative
weights are accepted (evaluation.json here). Rewrite a negative-coefficient term
c * x as |c| * (-x) plus a constant, which moves the bound to a non-negative value.
