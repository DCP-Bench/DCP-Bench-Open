// Flow Free: connect the two cells of every colour with a pipe so that the pipes
// cover the whole board and do not cross or overlap. Output B[r][c] is the colour
// of cell (r, c), an integer from 1 to K.
#include "dcp.h"

class FlowFree : public dcp::Space {
 protected:
  int R, C;        // board height and width, from the instance
  IntVarArray B;   // B[r*C + c]: colour of cell (r, c)
  IntVarArray d;   // d[p]: steps along its pipe from the nearest end (0 at an end)

 public:
  explicit FlowFree(const json& instance) {
    const auto& board = instance.at("board");
    R = board.size();
    C = board[0].size();
    int N = R * C;

    // the given non-zero cells are the pipe ends; K is the largest colour on the board
    std::vector<int> given(N, 0);
    int K = 0;
    for (int r = 0; r < R; ++r)
      for (int c = 0; c < C; ++c) {
        given[r * C + c] = board[r][c].get<int>();
        K = given[r * C + c] > K ? given[r * C + c] : K;
      }

    // every cell gets a colour from 1 to K, so the board is covered
    B = IntVarArray(*this, N, 1, K);
    // the pipe distance of a cell from its end is at most the number of cells minus one
    d = IntVarArray(*this, N, 0, N - 1);

    // the given cells keep their colour
    for (int p = 0; p < N; ++p)
      if (given[p] != 0) rel(*this, B[p], IRT_EQ, given[p]);

    // neighbouring cells of the same colour are joined by a pipe segment
    std::vector<BoolVarArgs> degree(N);   // degree[p]: segments at cell p
    std::vector<std::vector<int>> nb(N);  // nb[p]: grid neighbours of cell p
    auto link = [&](int p, int q) {
      nb[p].push_back(q);
      nb[q].push_back(p);
      BoolVar e = expr(*this, B[p] == B[q]);
      degree[p] << e;
      degree[q] << e;
    };
    for (int r = 0; r < R; ++r)
      for (int c = 0; c < C; ++c) {
        int p = r * C + c;
        if (c + 1 < C) link(p, p + 1);
        if (r + 1 < R) link(p, p + C);
      }

    // a pipe end has one segment, every other cell of a pipe has two
    for (int p = 0; p < N; ++p)
      linear(*this, degree[p], IRT_EQ, given[p] != 0 ? 1 : 2);

    // every pipe is a single path from its end, so no loop floats free of an end:
    // an end has distance 0, and every other cell of a pipe has a neighbour of
    // the same colour that is one step closer to the end (strictly decreasing
    // distances rule out cycles)
    for (int p = 0; p < N; ++p) {
      if (given[p] != 0) {
        rel(*this, d[p], IRT_EQ, 0);
      } else {
        rel(*this, d[p], IRT_GR, 0);
        BoolVarArgs closer;
        for (int q : nb[p])
          closer << expr(*this, (B[p] == B[q]) && (d[q] == d[p] - 1));
        clause(*this, BOT_OR, closer, BoolVarArgs(), 1);
      }
    }

    // branch on the colours first, then on the distances, so every variable is fixed
    branch(*this, B, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, d, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("B", Matrix<IntVarArray>(B, C, R));
  }

  FlowFree(FlowFree& s) : dcp::Space(s), R(s.R), C(s.C) {
    B.update(*this, s.B);
    d.update(*this, s.d);
  }
  Gecode::Space* copy() override { return new FlowFree(*this); }
};

DCP_MODEL(FlowFree)
