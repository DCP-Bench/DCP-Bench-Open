from pumpkin_solver import Model, constraints, SatisfactionResult
import json

model = Model()

# Decision variables: number of men, women, and children
men = model.new_integer_variable(0, 100, "men")
women = model.new_integer_variable(0, 100, "women")
children = model.new_integer_variable(0, 100, "children")

# 100 people in total
model.add_constraint(constraints.Equals(
    [men, women, children], 100, constraint_tag=model.new_constraint_tag()
))
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
model.add_constraint(constraints.Equals(
    [men.scaled(6), women.scaled(4), children], 200,
    constraint_tag=model.new_constraint_tag(),
))
# Five times as many women as men
model.add_constraint(constraints.Equals(
    [men.scaled(5), women.scaled(-1)], 0,
    constraint_tag=model.new_constraint_tag(),
))

result = model.satisfy()
if not isinstance(result, SatisfactionResult.Satisfiable):
    raise SystemExit("No solution found.")
sol = result[0]
print(json.dumps({
    "men": sol.int_value(men),
    "women": sol.int_value(women),
    "children": sol.int_value(children),
}))
