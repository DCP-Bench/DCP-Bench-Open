from pyoptinterface.highs import Model
import pyoptinterface as poi
import json

model = Model()
# Decision variables: number of men, women, and children
men = model.add_variable(domain=poi.VariableDomain.Integer, lb=0, ub=100, name="men")
women = model.add_variable(domain=poi.VariableDomain.Integer, lb=0, ub=100, name="women")
children = model.add_variable(domain=poi.VariableDomain.Integer, lb=0, ub=100, name="children")

# 100 people in total
model.add_linear_constraint(men + women + children, poi.Eq, 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
model.add_linear_constraint(6 * men + 4 * women + children, poi.Eq, 200)
# Five times as many women as men
model.add_linear_constraint(women - 5 * men, poi.Eq, 0)

model.optimize()
print(json.dumps({
    "men": int(round(model.get_value(men))),
    "women": int(round(model.get_value(women))),
    "children": int(round(model.get_value(children))),
}))
