"""Seat five people in a row: neighbours and non-neighbours, one person per seat."""
import cpmpy as cp

people = ["Ana", "Ben", "Cem", "Dora", "Eli"]
pos = cp.intvar(0, len(people) - 1, shape=len(people), name="pos")  # seat of each person

model = cp.Model(
    cp.AllDifferent(pos),          # one person per seat
    cp.abs(pos[0] - pos[1]) == 1,  # Ana sits next to Ben
    cp.abs(pos[2] - pos[3]) > 1,   # Cem does not sit next to Dora
    pos[4] == 0,                   # Eli sits at the left end
)

if model.solve():
    seats = [int(p.value()) for p in pos]
    order = sorted(range(len(people)), key=lambda i: seats[i])
    assert abs(seats[0] - seats[1]) == 1 and abs(seats[2] - seats[3]) > 1 and seats[4] == 0
    print("Satisfiable:", True)
    print("Seating:", " - ".join(people[i] for i in order))
    print("Checked: all constraints hold")
else:
    print("Satisfiable:", False)
