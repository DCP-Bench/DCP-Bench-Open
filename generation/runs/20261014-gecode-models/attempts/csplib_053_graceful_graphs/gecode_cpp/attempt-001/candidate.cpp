#include "dcp.h"

// Graceful labelling of a graph with q edges: give every node a distinct label
// from {0, ..., q} so that the edge labels |f(x) - f(y)| are all different.
// The graph is read from the instance; q is its number of edges.
class GracefulGraph : public dcp::Space {
 protected:
  IntVarArray node;  // node[v]: label f(v) of node v, from 0..q
  IntVarArray edge;  // edge[k]: label |f(x) - f(y)| of the k-th edge xy

 public:
  explicit GracefulGraph(const json& instance) {
    int q = instance.at("m").get<int>();
    int n = instance.at("n").get<int>();
    const auto& graph = instance.at("graph");

    node = IntVarArray(*this, n, 0, q);
    edge = IntVarArray(*this, q, 1, q);

    // each node receives a different label from 0..q
    distinct(*this, node, IPL_DOM);

    // each edge xy is labelled with the difference of the labels of x and y
    for (int k = 0; k < q; ++k) {
      int x = graph[k][0].get<int>();
      int y = graph[k][1].get<int>();
      rel(*this, edge[k] == abs(node[x] - node[y]));
    }

    // all edge labels are different
    distinct(*this, edge, IPL_DOM);

    // branch on the node labels first; the edge labels follow from them
    branch(*this, node, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, edge, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("nodes", node);
    output("edges", edge);
  }

  GracefulGraph(GracefulGraph& s) : dcp::Space(s) {
    node.update(*this, s.node);
    edge.update(*this, s.edge);
  }

  Gecode::Space* copy() override { return new GracefulGraph(*this); }
};

DCP_MODEL(GracefulGraph)
