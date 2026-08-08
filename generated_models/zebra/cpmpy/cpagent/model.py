import cpmpy as cp
import numpy as np
import json

# Step 1: Deconstruct & Pre-compute
# This is the classic Zebra puzzle with 5 houses and 5 attributes each
# Houses are numbered 0-4 from left to right
# Each attribute (color, nation, job, pet, drink) has 5 values
# Need to assign each value to exactly one house

# Attributes and their mappings:
color_map = {"yellow": 0, "green": 1, "red": 2, "white": 3, "blue": 4}
nation_map = {"italy": 0, "spain": 1, "japan": 2, "england": 3, "norway": 4}
job_map = {"painter": 0, "sculptor": 1, "diplomat": 2, "pianist": 3, "doctor": 4}
pet_map = {"cat": 0, "zebra": 1, "bear": 2, "snails": 3, "horse": 4}
drink_map = {"milk": 0, "water": 1, "tea": 2, "coffee": 3, "juice": 4}

# Step 2: Model with CPMpy
# Decision variables: each represents which house (0-4) has each attribute value
color_house = cp.intvar(0, 4, shape=5, name="color_house")
nation_house = cp.intvar(0, 4, shape=5, name="nation_house") 
job_house = cp.intvar(0, 4, shape=5, name="job_house")
pet_house = cp.intvar(0, 4, shape=5, name="pet_house")
drink_house = cp.intvar(0, 4, shape=5, name="drink_house")

model = cp.Model()

# Each attribute value must be in exactly one house (AllDifferent)
model += cp.AllDifferent(color_house)
model += cp.AllDifferent(nation_house)
model += cp.AllDifferent(job_house)
model += cp.AllDifferent(pet_house)
model += cp.AllDifferent(drink_house)

# Add the specific constraints:
# 1. The painter owns the horse
model += job_house[job_map["painter"]] == pet_house[pet_map["horse"]]

# 2. The diplomat drinks coffee
model += job_house[job_map["diplomat"]] == drink_house[drink_map["coffee"]]

# 3. The one who drinks milk lives in the white house
model += drink_house[drink_map["milk"]] == color_house[color_map["white"]]

# 4. The Spaniard is a painter
model += nation_house[nation_map["spain"]] == job_house[job_map["painter"]]

# 5. The Englishman lives in the red house
model += nation_house[nation_map["england"]] == color_house[color_map["red"]]

# 6. The snails are owned by the sculptor
model += pet_house[pet_map["snails"]] == job_house[job_map["sculptor"]]

# 7. The green house is on the left of the red one
model += color_house[color_map["green"]] + 1 == color_house[color_map["red"]]

# 8. The Norwegian lives on the right of the blue house
model += color_house[color_map["blue"]] + 1 == nation_house[nation_map["norway"]]

# 9. The doctor drinks milk
model += job_house[job_map["doctor"]] == drink_house[drink_map["milk"]]

# 10. The diplomat is Japanese
model += job_house[job_map["diplomat"]] == nation_house[nation_map["japan"]]

# 11. The Norwegian owns the zebra
model += nation_house[nation_map["norway"]] == pet_house[pet_map["zebra"]]

# 12. The green house is next to the white one
green_house = color_house[color_map["green"]]
white_house = color_house[color_map["white"]]
model += (green_house - white_house == 1) | (white_house - green_house == 1)

# 13. The horse is owned by the neighbor of the diplomat
horse_house = pet_house[pet_map["horse"]]
diplomat_house = job_house[job_map["diplomat"]]
model += (horse_house - diplomat_house == 1) | (diplomat_house - horse_house == 1)

# 14. The Italian either lives in the red, white or green house
italian_house = nation_house[nation_map["italy"]]
red_house = color_house[color_map["red"]]
white_house = color_house[color_map["white"]]
green_house = color_house[color_map["green"]]
model += (italian_house == red_house) | (italian_house == white_house) | (italian_house == green_house)

# Step 3: Solve & Verify
if model.solve():
    # Extract the solution
    color_solution = color_house.value()
    nation_solution = nation_house.value()
    job_solution = job_house.value()
    pet_solution = pet_house.value()
    drink_solution = drink_house.value()
    
    # Verification (independent of CPMpy)
    def verify_solution(color_sol, nation_sol, job_sol, pet_sol, drink_sol):
        """Verify the solution against all constraints"""
        
        def get_house(solution, value_idx):
            return solution[value_idx]
        
        # Check all 14 constraints
        constraints_satisfied = [
            get_house(job_sol, job_map["painter"]) == get_house(pet_sol, pet_map["horse"]),  # 1
            get_house(job_sol, job_map["diplomat"]) == get_house(drink_sol, drink_map["coffee"]),  # 2
            get_house(drink_sol, drink_map["milk"]) == get_house(color_sol, color_map["white"]),  # 3
            get_house(nation_sol, nation_map["spain"]) == get_house(job_sol, job_map["painter"]),  # 4
            get_house(nation_sol, nation_map["england"]) == get_house(color_sol, color_map["red"]),  # 5
            get_house(pet_sol, pet_map["snails"]) == get_house(job_sol, job_map["sculptor"]),  # 6
            get_house(color_sol, color_map["green"]) + 1 == get_house(color_sol, color_map["red"]),  # 7
            get_house(color_sol, color_map["blue"]) + 1 == get_house(nation_sol, nation_map["norway"]),  # 8
            get_house(job_sol, job_map["doctor"]) == get_house(drink_sol, drink_map["milk"]),  # 9
            get_house(job_sol, job_map["diplomat"]) == get_house(nation_sol, nation_map["japan"]),  # 10
            get_house(nation_sol, nation_map["norway"]) == get_house(pet_sol, pet_map["zebra"]),  # 11
            abs(get_house(color_sol, color_map["green"]) - get_house(color_sol, color_map["white"])) == 1,  # 12
            abs(get_house(pet_sol, pet_map["horse"]) - get_house(job_sol, job_map["diplomat"])) == 1,  # 13
            get_house(nation_sol, nation_map["italy"]) in [get_house(color_sol, color_map["red"]), 
                                                          get_house(color_sol, color_map["white"]), 
                                                          get_house(color_sol, color_map["green"])]  # 14
        ]
        
        return all(constraints_satisfied)
    
    # Verify the solution
    assert verify_solution(color_solution, nation_solution, job_solution, pet_solution, drink_solution), "Solution verification failed!"
    
    # Step 4: Output in required JSON format
    solution = {
        "colors": color_solution.tolist(),
        "nations": nation_solution.tolist(), 
        "jobs": job_solution.tolist(),
        "pets": pet_solution.tolist(),
        "drinks": drink_solution.tolist()
    }
    
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))