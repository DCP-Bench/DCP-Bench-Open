from gekko import GEKKO
import json

m = GEKKO(remote=False)
m.options.SOLVER = 1  # APOPT MINLP
m.options.IMODE = 3

# Decision variables: number of men, women, and children
men = m.Var(lb=0, ub=100, integer=True, name="men")
women = m.Var(lb=0, ub=100, integer=True, name="women")
children = m.Var(lb=0, ub=100, integer=True, name="children")

# 100 people in total
m.Equation(men + women + children == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
m.Equation(6 * men + 4 * women + children == 200)
# Five times as many women as men
m.Equation(women == 5 * men)

m.solve(disp=False)
print(json.dumps({
    "men": int(round(float(men.value[0]))),
    "women": int(round(float(women.value[0]))),
    "children": int(round(float(children.value[0]))),
}))
