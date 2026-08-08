import cpmpy as cp
import json

# Step 1: Problem Analysis
# Four friends: Debra=0, Janet=1, Hugh=2, Rick=3
# Allergies: eggs, mold, nuts, ragweed (each person has exactly one)
# Surnames: baxter, lemon, malone, fleet (each person has exactly one)

# Step 2: Model with CPMpy
# Decision variables: For each allergy/surname, which person (0-3) has it
eggs_person = cp.intvar(0, 3, name="eggs")
mold_person = cp.intvar(0, 3, name="mold") 
nuts_person = cp.intvar(0, 3, name="nuts")
ragweed_person = cp.intvar(0, 3, name="ragweed")

baxter_person = cp.intvar(0, 3, name="baxter")
lemon_person = cp.intvar(0, 3, name="lemon")
malone_person = cp.intvar(0, 3, name="malone")
fleet_person = cp.intvar(0, 3, name="fleet")

model = cp.Model()

# Step 3: Add constraints
# Each person has exactly one allergy and one surname
model += cp.AllDifferent([eggs_person, mold_person, nuts_person, ragweed_person])
model += cp.AllDifferent([baxter_person, lemon_person, malone_person, fleet_person])

# Specific constraints from problem:
# 1. Rick (3) is not allergic to mold
model += mold_person != 3

# 2. Baxter is allergic to eggs
model += baxter_person == eggs_person

# 3. Hugh (2) is neither surnamed Lemon nor Fleet
model += lemon_person != 2
model += fleet_person != 2

# 4. Debra (0) is allergic to ragweed
model += ragweed_person == 0

# 5. Janet (1) who isn't Lemon is neither allergic to eggs nor to mold
model += lemon_person != 1  # Janet isn't Lemon
model += eggs_person != 1   # Janet not allergic to eggs
model += mold_person != 1   # Janet not allergic to mold

# Step 4: Solve and verify
if model.solve():
    solution = {
        "eggs": eggs_person.value(),
        "mold": mold_person.value(), 
        "nuts": nuts_person.value(),
        "ragweed": ragweed_person.value(),
        "baxter": baxter_person.value(),
        "lemon": lemon_person.value(),
        "malone": malone_person.value(),
        "fleet": fleet_person.value()
    }
    
    # Verification
    def verify_solution(sol):
        allergy_assignments = [sol["eggs"], sol["mold"], sol["nuts"], sol["ragweed"]]
        surname_assignments = [sol["baxter"], sol["lemon"], sol["malone"], sol["fleet"]]
        
        # Structural checks
        if len(set(allergy_assignments)) != 4 or len(set(surname_assignments)) != 4:
            return False
        
        # Logical constraint checks
        if sol["mold"] == 3:  # Rick not allergic to mold
            return False
        if sol["baxter"] != sol["eggs"]:  # Baxter allergic to eggs
            return False
        if sol["lemon"] == 2 or sol["fleet"] == 2:  # Hugh not Lemon or Fleet
            return False
        if sol["ragweed"] != 0:  # Debra allergic to ragweed
            return False
        if sol["lemon"] == 1 or sol["eggs"] == 1 or sol["mold"] == 1:  # Janet constraints
            return False
        
        return True
    
    assert verify_solution(solution), "Solution verification failed!"
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))