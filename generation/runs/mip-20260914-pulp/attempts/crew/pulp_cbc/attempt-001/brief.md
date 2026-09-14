# crew
Instance: `attributes` (person x skill 0/1) and `required_crew` (per flight:
crew size then five skill minima). Output: `crew`, a flight x person 0/1 matrix.
Satisfaction: each flight takes exactly its crew size, meets every skill
minimum, and nobody flies twice within any three consecutive flights.
The reference's `num_working` counts the people used; it is not a declared
output and every flight needs several crew, so its 1..num_persons bound cannot
exclude any assignment. It is left out rather than reified.
