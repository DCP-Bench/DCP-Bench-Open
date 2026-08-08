import cpmpy as cp
import json

# Problem data
at_most = [1, 2, 2, 2, 1]  # Max times a property can appear in consecutive slots
per_slots = [2, 3, 3, 5, 5]  # Size of consecutive slot windows
demand = [1, 1, 2, 2, 2, 2]  # How many cars of each type to produce
requires = [[1, 0, 1, 1, 0],  # Which properties each car type requires
            [0, 0, 0, 1, 0],
            [0, 1, 0, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 1, 0, 0],
            [1, 1, 0, 0, 0]]

num_car_types = len(demand)
total_cars = sum(demand)
num_properties = len(at_most)

model = cp.Model()

# Decision variables: sequence[i] = car type at position i
sequence = cp.intvar(0, num_car_types - 1, shape=total_cars, name="sequence")

# Constraint 1: Respect demand for each car type
for car_type in range(num_car_types):
    model += cp.Count(sequence, car_type) == demand[car_type]

# Constraint 2: Capacity constraints for each property
# For each property, check sliding windows
for prop in range(num_properties):
    window_size = per_slots[prop]
    max_in_window = at_most[prop]
    
    # For each possible window position
    for start_pos in range(total_cars - window_size + 1):
        # Count cars in this window that have this property
        cars_with_property = []
        for pos in range(start_pos, start_pos + window_size):
            # Check if car at position pos has property prop
            has_property = cp.sum([
                (sequence[pos] == car_type) * requires[car_type][prop] 
                for car_type in range(num_car_types)
            ])
            cars_with_property.append(has_property)
        
        # Sum must not exceed capacity
        model += cp.sum(cars_with_property) <= max_in_window

# Solve the model
if model.solve():
    solution = {"sequence": sequence.value().tolist()}
    print(json.dumps(solution))
else:
    print(json.dumps({"error": "No solution found"}))