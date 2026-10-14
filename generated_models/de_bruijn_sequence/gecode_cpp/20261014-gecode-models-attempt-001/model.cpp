// de Bruijn sequence B(k, n): a cyclic sequence over an alphabet of k symbols,
// length k^n, in which every length-n string occurs exactly once as a substring.
// Instance: base = k (alphabet size), n = order.
#include "dcp.h"

namespace {
int ipow(int b, int e) {
  int r = 1;
  for (int i = 0; i < e; ++i) r *= b;
  return r;
}
}  // namespace

class DeBruijn : public dcp::Space {
 protected:
  IntVarArray seq;   // seq[i]: symbol at position i of the cyclic sequence
  IntVarArray win;   // win[i]: value of the length-n string starting at position i

 public:
  explicit DeBruijn(const json& instance) {
    int base = instance.at("base").get<int>();
    int n = instance.at("n").get<int>();
    int len = ipow(base, n);      // the sequence has k^n symbols
    int strings = ipow(base, n);  // there are k^n strings of length n

    seq = IntVarArray(*this, len, 0, base - 1);
    win = IntVarArray(*this, len, 0, strings - 1);

    // each string of length n, read as a base-k number, is the value of one window
    // the sequence is cyclic: a window that runs past the end wraps to the start
    for (int i = 0; i < len; ++i) {
      IntVarArgs xs;
      IntArgs cs;
      for (int j = 0; j < n; ++j) {
        xs << seq[(i + j) % len];
        cs << ipow(base, n - 1 - j);
      }
      xs << win[i];
      cs << -1;
      linear(*this, cs, xs, IRT_EQ, 0);
    }

    // every length-n string occurs exactly once: the windows are all different
    distinct(*this, win, IPL_DOM);

    branch(*this, seq, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, win, INT_VAR_NONE(), INT_VAL_MIN());
    output("de_bruijn", seq);
  }

  DeBruijn(DeBruijn& s) : dcp::Space(s) {
    seq.update(*this, s.seq);
    win.update(*this, s.win);
  }
  Gecode::Space* copy() override { return new DeBruijn(*this); }
};

DCP_MODEL(DeBruijn)
