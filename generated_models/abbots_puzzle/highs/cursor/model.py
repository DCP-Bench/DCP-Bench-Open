from highspy import Highs
import json

highs = Highs()
highs.silent()

# Decision variables: number of men, women, and children
men = highs.addIntegral(0, 100, name="men")
women = highs.addIntegral(0, 100, name="women")
children = highs.addIntegral(0, 100, name="children")

# 100 people in total
highs.addConstr(men + women + children == 100)
# 100 bushels: 3 per man, 2 per woman, 1/2 per child  (×2 to stay integer)
highs.addConstr(6 * men + 4 * women + children == 200)
# Five times as many women as men
highs.addConstr(women == 5 * men)

highs.run()
print(json.dumps({
    "men": int(round(highs.val(men))),
    "women": int(round(highs.val(women))),
    "children": int(round(highs.val(children))),
}))
