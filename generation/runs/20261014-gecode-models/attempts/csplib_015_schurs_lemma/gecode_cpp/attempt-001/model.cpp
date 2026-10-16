#include "dcp.h"

// Schur's lemma: put the balls 1..n into c boxes so that no triple of balls
// (x, y, z) with x + y = z has all three balls in the same box.
class SchursLemma : public dcp::Space {
 protected:
  IntVarArray balls;  // balls[i-1]: box of ball i

 public:
  explicit SchursLemma(const json& instance) {
    int n = instance.at("n").get<int>();
    int c = instance.at("c").get<int>();
    balls = IntVarArray(*this, n, 1, c);

    // the boxes are interchangeable: box v+1 is first used only after box v
    IntArgs boxes(c);
    for (int v = 0; v < c; ++v) boxes[v] = v + 1;
    precede(*this, balls, boxes);

    // for every x + y = z with 1 <= x <= y, z <= n (x = y is allowed),
    // not all three balls are in the same box
    for (int x = 1; x <= n; ++x)
      for (int y = x; x + y <= n; ++y) {
        int z = x + y;
        rel(*this, (balls[x - 1] != balls[y - 1]) || (balls[y - 1] != balls[z - 1]));
      }

    branch(*this, balls, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    output("balls", balls);
  }

  SchursLemma(SchursLemma& s) : dcp::Space(s) {
    balls.update(*this, s.balls);
  }
  Gecode::Space* copy() override { return new SchursLemma(*this); }
};

DCP_MODEL(SchursLemma)
