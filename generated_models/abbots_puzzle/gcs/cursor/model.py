from gcspy import GCS
import json

gcs = GCS()

# Decision variables: number of men, women, and children
men = gcs.create_integer_variable(0, 100, "men")
women = gcs.create_integer_variable(0, 100, "women")
children = gcs.create_integer_variable(0, 100, "children")
people = gcs.create_integer_constant(100)
bushels = gcs.create_integer_constant(200)
zero = gcs.create_integer_constant(0)

# 100 people in total
gcs.post_linear_equality([men, women, children, people], [1, 1, 1, -1], 0)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
gcs.post_linear_equality([men, women, children, bushels], [6, 4, 1, -1], 0)
# Five times as many women as men
gcs.post_linear_equality([men, women, zero], [5, -1, 1], 0)

gcs.solve(all_solutions=False)
print(json.dumps({
    "men": gcs.get_solution_value(men),
    "women": gcs.get_solution_value(women),
    "children": gcs.get_solution_value(children),
}))
