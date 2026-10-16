// Diamond-free degree sequences (CSPLib 050). Find a simple undirected graph on N
// vertices, with no loops, in which no four vertices span at least five edges
// (no induced diamond), every vertex has a degree that is a positive multiple of 3,
// the degrees are sorted non-increasing, and the sum of the degrees is a multiple of 12.
// The output is the adjacency matrix of such a graph.
#include "dcp.h"

class DiamondFree : public dcp::Space {
 protected:
  int n;              // number of vertices, from the instance
  BoolVarArray adj;   // adj[i*n+j]: vertices i and j are adjacent
  IntVarArray deg;    // deg[i]: degree of vertex i

 public:
  explicit DiamondFree(const json& instance) {
    n = instance.at("N").get<int>();

    adj = BoolVarArray(*this, n * n, 0, 1);

    // degrees are positive multiples of 3, at most n-1
    std::vector<int> degrees;
    for (int d = 3; d <= n - 1; d += 3) degrees.push_back(d);
    deg = IntVarArray(*this, n, IntSet(IntArgs(degrees)));

    // no loop edges: a vertex is not adjacent to itself
    for (int i = 0; i < n; ++i) rel(*this, adj[i * n + i], IRT_EQ, 0);

    // undirected graph: the edge {i, j} is one Boolean, seen from both rows
    for (int i = 0; i < n; ++i)
      for (int j = i + 1; j < n; ++j)
        rel(*this, adj[i * n + j], IRT_EQ, adj[j * n + i]);

    // the degree of vertex i is the number of vertices adjacent to it
    for (int i = 0; i < n; ++i) {
      BoolVarArgs row;
      for (int j = 0; j < n; ++j)
        if (j != i) row << adj[i * n + j];
      linear(*this, row, IRT_EQ, deg[i]);
    }

    // degree sequence d_1 >= d_2 >= ... >= d_n
    for (int i = 0; i + 1 < n; ++i) rel(*this, deg[i], IRT_GQ, deg[i + 1]);

    // the sum of the degrees is a multiple of 12 (so the number of edges is a multiple of 6)
    IntVar k(*this, 0, n * (n - 1) / 12);
    IntVarArgs degrees_all;
    for (int i = 0; i < n; ++i) degrees_all << deg[i];
    rel(*this, sum(degrees_all) == 12 * k);

    // no diamond: any four vertices have at most four edges between them
    for (int a = 0; a < n; ++a)
      for (int b = a + 1; b < n; ++b)
        for (int c = b + 1; c < n; ++c)
          for (int d = c + 1; d < n; ++d) {
            BoolVarArgs six;
            six << adj[a * n + b] << adj[a * n + c] << adj[a * n + d]
                << adj[b * n + c] << adj[b * n + d] << adj[c * n + d];
            linear(*this, six, IRT_LQ, 4);
          }

    // branch on the degree sequence first, then on the edges
    branch(*this, deg, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, adj, BOOL_VAR_NONE(), BOOL_VAL_MIN());

    // the adjacency matrix, one list per row
    std::vector<BoolVarArgs> rows(n);
    for (int i = 0; i < n; ++i)
      for (int j = 0; j < n; ++j) rows[i] << adj[i * n + j];
    output("matrix", rows);
  }

  DiamondFree(DiamondFree& s) : dcp::Space(s), n(s.n) {
    adj.update(*this, s.adj);
    deg.update(*this, s.deg);
  }
  Gecode::Space* copy() override { return new DiamondFree(*this); }
};

DCP_MODEL(DiamondFree)
