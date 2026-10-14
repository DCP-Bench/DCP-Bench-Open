#include "dcp.h"

// Vessel loading (CSPLib prob008): place every container on the rectangular deck,
// as a non-overlapping, axis-parallel rectangle, and keep containers of separated
// classes apart by their minimum distance along the deck or across the deck.
// Containers may be turned by 90 degrees. Edges are exclusive: right = left + width.
class VesselLoading : public dcp::Space {
 protected:
  int n;
  IntVarArray left, right, bottom, top;  // container edges along the deck length and width
  IntVarArray rot;                        // rot[i] = 1 if container i is turned
  IntVarArray w, h;                       // extent of container i along x and along y

 public:
  explicit VesselLoading(const json& instance) {
    int deck_width = instance.at("deck_width").get<int>();
    int deck_length = instance.at("deck_length").get<int>();
    n = instance.at("n_containers").get<int>();
    std::vector<int> width = instance.at("width");
    std::vector<int> length = instance.at("length");
    std::vector<int> classes = instance.at("classes");
    std::vector<std::vector<int>> separation = instance.at("separation");

    int widest = deck_width > deck_length ? deck_width : deck_length;
    left = IntVarArray(*this, n, 0, deck_width);
    right = IntVarArray(*this, n, 0, deck_width);
    bottom = IntVarArray(*this, n, 0, deck_length);
    top = IntVarArray(*this, n, 0, deck_length);
    rot = IntVarArray(*this, n, 0, 1);
    w = IntVarArray(*this, n, 0, widest);
    h = IntVarArray(*this, n, 0, widest);

    // a container is turned by 90 degrees: its x extent is then its length
    for (int i = 0; i < n; ++i) {
      element(*this, IntArgs({width[i], length[i]}), rot[i], w[i]);
      element(*this, IntArgs({length[i], width[i]}), rot[i], h[i]);
      // the right and top edges follow from the left and bottom edges and the size
      rel(*this, left[i] + w[i] == right[i]);
      rel(*this, bottom[i] + h[i] == top[i]);
    }

    // containers do not overlap
    IntVarArgs x0, ww, x1, y0, hh, y1;
    for (int i = 0; i < n; ++i) {
      x0 << left[i];
      ww << w[i];
      x1 << right[i];
      y0 << bottom[i];
      hh << h[i];
      y1 << top[i];
    }
    nooverlap(*this, x0, ww, x1, y0, hh, y1);

    // containers of two classes with a minimum distance s between them are at least s
    // apart along the deck or across the deck (the separation matrix gives s per class pair)
    for (int i = 0; i < n; ++i) {
      for (int j = i + 1; j < n; ++j) {
        int s = separation[classes[i] - 1][classes[j] - 1];
        if (s == 0) continue;  // covered by the non-overlap constraint
        BoolVarArgs apart;
        apart << expr(*this, left[j] - right[i] >= s);     // j is right of i
        apart << expr(*this, left[i] - right[j] >= s);     // i is right of j
        apart << expr(*this, bottom[j] - top[i] >= s);     // j is above i
        apart << expr(*this, bottom[i] - top[j] >= s);     // i is above j
        clause(*this, BOT_OR, apart, BoolVarArgs(), 1);
      }
    }

    // cell view of the deck: inX/inY say whether a container spans a column or a row;
    // owner[c] names the container on cell c, 0 for an empty cell. The channel makes a
    // cell covered by at most one container. It is redundant with the non-overlap
    // constraint but propagates far more on a tightly filled deck.
    BoolVarArray inX(*this, n * deck_width, 0, 1);
    BoolVarArray inY(*this, n * deck_length, 0, 1);
    for (int i = 0; i < n; ++i) {
      for (int x = 0; x < deck_width; ++x)
        inX[i * deck_width + x] = expr(*this, (left[i] <= x) && (right[i] >= x + 1));
      for (int y = 0; y < deck_length; ++y)
        inY[i * deck_length + y] = expr(*this, (bottom[i] <= y) && (top[i] >= y + 1));
    }
    IntVarArray owner(*this, deck_width * deck_length, 0, n);
    for (int y = 0; y < deck_length; ++y) {
      for (int x = 0; x < deck_width; ++x) {
        // cover[0] says the cell is empty, cover[i + 1] says container i covers it
        BoolVarArgs cover;
        cover << expr(*this, owner[y * deck_width + x] == 0);
        for (int i = 0; i < n; ++i)
          cover << expr(*this, inX[i * deck_width + x] && inY[i * deck_length + y]);
        channel(*this, cover, owner[y * deck_width + x], 0);
      }
    }

    // when the containers have exactly the area of the deck, no cell can stay empty
    // (a fact derived from the instance data, so it is posted only then)
    int total_area = 0;
    for (int i = 0; i < n; ++i) total_area += width[i] * length[i];
    if (total_area == deck_width * deck_length)
      for (int k = 0; k < deck_width * deck_length; ++k) rel(*this, owner[k], IRT_NQ, 0);

    // branch on the cell owners first (in row order, from the bottom), then on the
    // orientations and the positions
    branch(*this, owner, INT_VAR_NONE(), INT_VAL_MAX());
    branch(*this, rot, INT_VAR_NONE(), INT_VAL_MIN());
    branch(*this, left, INT_VAR_SIZE_MIN(), INT_VAL_MIN());
    branch(*this, bottom, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("left", left);
    output("right", right);
    output("bottom", bottom);
    output("top", top);
  }

  VesselLoading(VesselLoading& s) : dcp::Space(s), n(s.n) {
    left.update(*this, s.left);
    right.update(*this, s.right);
    bottom.update(*this, s.bottom);
    top.update(*this, s.top);
    rot.update(*this, s.rot);
    w.update(*this, s.w);
    h.update(*this, s.h);
  }
  Gecode::Space* copy() override { return new VesselLoading(*this); }
};

DCP_MODEL(VesselLoading)
