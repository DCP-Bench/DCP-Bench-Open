// Vessel loading: place rectangular containers in a single layer on a rectangular deck, without overlap and
// with the required minimum separations between containers of the classes that need them. Containers are
// placed parallel to the deck sides, so each container may be turned by 90 degrees (width and length swap).
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  int deck_w = instance.at("deck_width");   // extent of the deck across (horizontal axis)
  int deck_l = instance.at("deck_length");  // extent of the deck along (vertical axis)
  int n = instance.at("n_containers");
  std::vector<int> width = instance.at("width").get<std::vector<int>>();
  std::vector<int> length = instance.at("length").get<std::vector<int>>();
  std::vector<int> cls = instance.at("classes").get<std::vector<int>>();
  std::vector<std::vector<int>> sep = instance.at("separation").get<std::vector<std::vector<int>>>();

  // turned[i] = 1 if container i is turned by 90 degrees, so its horizontal extent is its length
  vec<IntVar*> turned;
  createVars(turned, n, 0, 1, true);

  // left[i], right[i]: horizontal extent of container i; bottom[i], top[i]: vertical extent
  vec<IntVar*> left, right, bottom, top;
  for (int i = 0; i < n; ++i) {
    int wmin = std::min(width[i], length[i]), wmax = std::max(width[i], length[i]);
    IntVar* l = newIntVar(0, deck_w);
    IntVar* r = newIntVar(0, deck_w);
    IntVar* b = newIntVar(0, deck_l);
    IntVar* t = newIntVar(0, deck_l);
    // horizontal extent ex = width if not turned, length if turned: ex = width + (length - width) * turned
    IntVar* ex = newIntVar(wmin, wmax);
    vec<int> cex;
    cex.push(1);
    cex.push(-(length[i] - width[i]));
    vec<IntVar*> vex;
    vex.push(ex);
    vex.push(turned[i]);
    int_linear(cex, vex, IRT_EQ, width[i]);
    // vertical extent ey = length if not turned, width if turned: ey = length + (width - length) * turned
    IntVar* ey = newIntVar(wmin, wmax);
    vec<int> cey;
    cey.push(1);
    cey.push(-(width[i] - length[i]));
    vec<IntVar*> vey;
    vey.push(ey);
    vey.push(turned[i]);
    int_linear(cey, vey, IRT_EQ, length[i]);
    // the container spans its extents: right = left + ex, top = bottom + ey
    vec<int> c3;
    c3.push(1);
    c3.push(1);
    c3.push(-1);
    vec<IntVar*> lxr;
    lxr.push(l);
    lxr.push(ex);
    lxr.push(r);
    int_linear(c3, lxr, IRT_EQ, 0);
    vec<IntVar*> byt;
    byt.push(b);
    byt.push(ey);
    byt.push(t);
    int_linear(c3, byt, IRT_EQ, 0);
    left.push(l);
    right.push(r);
    bottom.push(b);
    top.push(t);
  }

  // containers do not overlap, and containers of classes that need a separation s are at least s apart,
  // either across the deck (horizontally) or along the deck (vertically); with s = 0 this is non-overlap
  for (int i = 0; i < n; ++i) {
    for (int j = i + 1; j < n; ++j) {
      int s = sep[cls[i] - 1][cls[j] - 1];
      vec<BoolView> options;
      vec<int> gap;
      gap.push(1);
      gap.push(-1);

      // j lies to the right of i with a gap of at least s
      BoolView right_of = newBoolVar();
      vec<IntVar*> v1;
      v1.push(left[j]);
      v1.push(right[i]);
      int_linear(gap, v1, IRT_GE, s, right_of);
      options.push(right_of);

      // i lies to the right of j with a gap of at least s
      BoolView left_of = newBoolVar();
      vec<IntVar*> v2;
      v2.push(left[i]);
      v2.push(right[j]);
      int_linear(gap, v2, IRT_GE, s, left_of);
      options.push(left_of);

      // j lies above i with a gap of at least s
      BoolView above = newBoolVar();
      vec<IntVar*> v3;
      v3.push(bottom[j]);
      v3.push(top[i]);
      int_linear(gap, v3, IRT_GE, s, above);
      options.push(above);

      // i lies above j with a gap of at least s
      BoolView below = newBoolVar();
      vec<IntVar*> v4;
      v4.push(bottom[i]);
      v4.push(top[j]);
      int_linear(gap, v4, IRT_GE, s, below);
      options.push(below);

      bool_clause(options);
    }
  }

  vec<IntVar*> decisions;
  for (int i = 0; i < n; ++i) {
    decisions.push(left[i]);
    decisions.push(bottom[i]);
  }
  vec<IntVar*> all = decisions; for (int i = 0; i < n; ++i) all.push(turned[i]);
  branch(all, VAR_SIZE_MIN, VAL_MIN);

  auto arr = [](vec<IntVar*>& v) {
    json a = json::array();
    for (int i = 0; i < v.size(); ++i) a.push_back(dcp::out(v[i]));
    return a;
  };
  outputs = {{"left", arr(left)}, {"right", arr(right)}, {"top", arr(top)}, {"bottom", arr(bottom)}};
}
