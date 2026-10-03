"""Graceful graphs: label the nodes with distinct values in 0..q so that the edge labels |f(x) - f(y)| are all different."""
import gurobipy as gp
from gurobipy import GRB


def build(instance):
    m = instance["m"]  # number of edges, q
    n = instance["n"]  # number of nodes
    graph = instance["graph"]  # graph[e] = [x, y], the end nodes of edge e
    node_labels = range(m + 1)
    edge_labels = range(1, m + 1)

    model = gp.Model("graceful_graphs")

    # Each node gets a label from 0..q, and no two nodes share one.
    # node_is[i, a] is 1 when node i has label a.
    node_is = model.addVars(n, node_labels, vtype=GRB.BINARY, name="node_is")
    for i in range(n):
        model.addConstr(node_is.sum(i, "*") == 1, name=f"node_label[{i}]")
    for a in node_labels:
        model.addConstr(node_is.sum("*", a) <= 1, name=f"node_distinct[{a}]")
    nodes = [gp.quicksum(a * node_is[i, a] for a in node_labels) for i in range(n)]

    # Each edge gets a label from 1..q, and the edge labels are all different.
    # edge_is[e, d] is 1 when edge e has label d.
    edge_is = model.addVars(m, edge_labels, vtype=GRB.BINARY, name="edge_is")
    for e in range(m):
        model.addConstr(edge_is.sum(e, "*") == 1, name=f"edge_label[{e}]")
    for d in edge_labels:
        model.addConstr(edge_is.sum("*", d) <= 1, name=f"edge_distinct[{d}]")
    edges = [gp.quicksum(d * edge_is[e, d] for d in edge_labels) for e in range(m)]

    # The label of edge xy is |f(x) - f(y)|. gp.abs_ takes a variable, so the
    # signed difference and its size get variables of their own.
    for e, (x, y) in enumerate(graph):
        diff = model.addVar(lb=-m, ub=m, vtype=GRB.INTEGER, name=f"diff[{e}]")
        size = model.addVar(lb=0, ub=m, vtype=GRB.INTEGER, name=f"size[{e}]")
        model.addConstr(diff == nodes[x] - nodes[y], name=f"diff_def[{e}]")
        model.addConstr(size == gp.abs_(diff), name=f"abs[{e}]")
        model.addConstr(size == edges[e], name=f"edge_value[{e}]")

    return model, {"nodes": nodes, "edges": edges}
