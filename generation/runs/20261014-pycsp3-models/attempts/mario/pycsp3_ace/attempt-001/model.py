from pycsp3 import *

# Mario starts at his house and ends at Luigi's house, visiting houses on the way; the route collects the gold of
# the houses it visits and the fuel of the roads it uses must stay within the fuel limit
n = data.nHouses
mario, luigi = data.marioHouse, data.luigiHouse

# s[i] is the house after house i on the route, s[i] = i when house i is not on the route;
# the route returns from Luigi's house to Mario's house, which closes the cycle
s = VarArray(size=n, dom=range(n))

# visited[i] is 1 when house i is on the route
visited = VarArray(size=n, dom={0, 1})

# order[i] is the position of house i on the route, counted from Mario's house
order = VarArray(size=n, dom=range(n))

# fuel[i] is the fuel used on the road leaving house i, 0 when house i is not on the route
fuel = VarArray(size=n, dom=range(0, max(max(row) for row in data.arc_fuel) + 1))

satisfy(
    # every house is the sessor of at most one house
    AllDifferent(s),
    # a house is on the route exactly when it does not loop to itself
    [If(visited[i] == 1, Then=s[i] != i, Else=s[i] == i) for i in range(n)],
    # Mario's house is on the route and Luigi's house leads back to it
    visited[mario] == 1,
    s[luigi] == mario,
    # the route starts at Mario's house
    order[mario] == 0,
    # along the route, each house is one step after the house before it, except for the closing road to Mario's house
    [imply(And(visited[i] == 1, s[i] != mario), order[s[i]] == order[i] + 1) for i in range(n)],
    # the fuel of the road leaving each house on the route, from the table of road fuel costs
    [Table(scope=[s[i], fuel[i]], supports=[(j, data.arc_fuel[i][j]) for j in range(n) if j != i] + [(i, 0)])
     for i in range(n)],
    # the total fuel used must not exceed the fuel limit
    Sum(fuel) <= data.fuelLimit,
)

# maximise the gold collected from the houses on the route
maximize(Sum(data.goldInHouse[i] * visited[i] for i in range(n)))
