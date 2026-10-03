"""People in a room: order 13 people, 4 of them male, so the female-to-male ratio in the room never exceeds 7/3."""
import gurobipy as gp
from gurobipy import GRB

# The problem has no instance data: 13 people, 4 male, ratio 7/3, as stated.
TOTAL_PEOPLE = 13
NUM_MALES = 4
RATIO_FEMALES, RATIO_MALES = 7, 3


def build(instance):
    model = gp.Model("session3_people_in_a_room")

    # sequence[i] = 1 when the i-th person to enter is female, 0 when male.
    sequence = [model.addVar(vtype=GRB.BINARY, name=f"female[{i}]") for i in range(TOTAL_PEOPLE)]

    # Exactly 4 of the 13 are male.
    model.addConstr(gp.quicksum(sequence) == TOTAL_PEOPLE - NUM_MALES, name="number_of_males")

    # After each of the first i people has entered (i = 1..12, as in the
    # reference), females / males <= 7 / 3, i.e. 3 * females <= 7 * males.
    for i in range(1, TOTAL_PEOPLE):
        females = gp.quicksum(sequence[:i])
        males = i - females
        model.addConstr(RATIO_MALES * females <= RATIO_FEMALES * males, name=f"ratio[{i}]")

    return model, {"sequence": sequence}
