from pychoco.model import Model

# Two products; profit per unit, and the resources each unit uses.
PROFIT = [3, 2]
LABOUR = [2, 1]      # hours per unit
MATERIAL = [1, 3]    # kg per unit
LABOUR_LIMIT = 10
MATERIAL_LIMIT = 15

model = Model()
make = [model.intvar(0, 10, name="A"), model.intvar(0, 10, name="B")]
model.scalar(make, LABOUR, "<=", LABOUR_LIMIT).post()
model.scalar(make, MATERIAL, "<=", MATERIAL_LIMIT).post()

profit = model.intvar(0, 100, name="profit")
model.scalar(make, PROFIT, "=", profit).post()

solution = model.get_solver().find_optimal_solution(profit, True)
if solution is None:
    print("no plan")
else:
    print("Make A:", solution.get_int_val(make[0]), "B:", solution.get_int_val(make[1]))
    print("Maximum profit:", solution.get_int_val(profit))
