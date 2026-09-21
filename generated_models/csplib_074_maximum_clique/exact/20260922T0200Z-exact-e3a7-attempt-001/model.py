# Largest set of mutually adjacent vertices.
from dcp_pb import Pb


def build(instance):
    n = instance["n"]
    adj = instance["adj"]

    pb = Pb()
    chosen = pb.bools(n)
    for i in range(n):
        for j in range(i + 1, n):
            if adj[i][j] == 0:
                pb.at_most([chosen[i], chosen[j]], 1)
    pb.maximise([(1, c) for c in chosen])
    return pb, {"c": chosen}
