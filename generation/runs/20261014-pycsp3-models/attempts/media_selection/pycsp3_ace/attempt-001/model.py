from pycsp3 import *

# Select advertising media so that every target audience is reached by at least one
# selected medium, at the minimum total campaign cost.

audiences = len(data.target_audiences)
media = len(data.advertising_media)
cover = data.incidence_matrix  # cover[a][m] is 1 when medium m reaches audience a
costs = data.media_costs

# is_selected[m] is 1 when medium m is selected
is_selected = VarArray(size=media, dom={0, 1})

# min_total_cost is the total cost of the selected media
min_total_cost = Var(dom=range(0, sum(costs) + 1))

satisfy(
    # every audience is covered by at least one selected medium
    [Sum(is_selected[m] for m in range(media) if cover[a][m] == 1) >= 1 for a in range(audiences)],

    # the total cost is the sum of the costs of the selected media
    min_total_cost == Sum(costs[m] * is_selected[m] for m in range(media)),
)

# minimise the total cost of the campaign
minimize(min_total_cost)
