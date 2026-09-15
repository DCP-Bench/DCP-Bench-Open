Each row of `movies` is a title followed by a start and an end, so the field
mixes a string with two integers within one row. MiniZinc's data interface binds
a list of lists as a rectangular array of one element type, and refuses with
"non-uniform array literal. Expected `string' but got `int'". No model can avoid
it — the shape of the instance field is the obstacle, exactly as for the ragged
`Qualified` field of covering_opl. Recorded as a blocker for this pair.
