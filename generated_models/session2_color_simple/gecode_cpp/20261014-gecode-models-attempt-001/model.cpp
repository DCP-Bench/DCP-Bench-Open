#include "dcp.h"

// Colour the countries (Belgium, Denmark, France, Germany, Netherlands, Luxembourg)
// so that neighbouring countries have different colours, minimising the number of
// colours used. Colours are integers starting from 1.
class MapColouring : public dcp::Space {
 protected:
  IntVarArray colors;  // colors[i]: colour of country i+1
  IntVar ncolors;      // number of colours used: the largest colour

 public:
  explicit MapColouring(const json& instance) {
    const auto& graph = instance.at("graph");
    const int n = 6;

    // each country gets a colour from 1 to the number of countries
    colors = IntVarArray(*this, n, 1, n);

    // two neighbouring countries cannot have the same colour
    // (the graph gives the neighbouring pairs, 1-based country numbers)
    for (const auto& edge : graph) {
      int a = edge[0].get<int>() - 1;
      int b = edge[1].get<int>() - 1;
      rel(*this, colors[a] != colors[b]);
    }

    // colours are interchangeable: colour v+1 is only used after colour v
    precede(*this, colors, IntArgs({1, 2, 3, 4, 5, 6}));

    // the number of colours used is the largest colour
    ncolors = expr(*this, max(colors));

    branch(*this, colors, INT_VAR_NONE(), INT_VAL_MIN());
    // find a colouring that minimises the number of colours used
    minimize(ncolors);
    output("colors", colors);
  }

  MapColouring(MapColouring& s) : dcp::Space(s) {
    colors.update(*this, s.colors);
    ncolors.update(*this, s.ncolors);
  }
  Gecode::Space* copy() override { return new MapColouring(*this); }
};

DCP_MODEL(MapColouring)
