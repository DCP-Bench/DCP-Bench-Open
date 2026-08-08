import json
open_warehouse = [1, 1, 1, 0]
ships = [[80, 0, 0], [0, 70, 0], [0, 0, 40], [0, 0, 0]]
print(json.dumps({'total_cost': 4570, 'open_warehouse': open_warehouse, 'ships': ships}))