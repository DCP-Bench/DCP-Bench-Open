// Who killed Agatha: three people (Agatha, the butler, Charles) live in Dreadsbury Mansion; one of them killed Agatha under the stated hatred and wealth rules.
#include "dcp.h"

void Build(const json& instance, json& outputs) {
  // people are numbered 0 = Agatha, 1 = the butler, 2 = Charles (the order of the names field)
  const int AGATHA = 0, BUTLER = 1, CHARLES = 2;
  int np = 3;

  // killer is the index of the person who killed Agatha
  IntVar* killer = newIntVar(0, np - 1);
  vec<BoolView> is_killer;
  createVars(is_killer, np);
  for (int i = 0; i < np; ++i) int_rel_reif(killer, IRT_EQ, i, is_killer[i]);

  // hates[i][j] = 1 if person i hates person j; richer[i][j] = 1 if person i is richer than person j
  vec<vec<BoolView>> hates, richer;
  createVars(hates, np, np);
  createVars(richer, np, np);

  // no one is richer than himself, and of two people at most one is richer than the other
  for (int i = 0; i < np; ++i) {
    vec<BoolView> none, self_richer;
    self_richer.push(richer[i][i]);
    bool_clause(none, self_richer);
    for (int j = i + 1; j < np; ++j) {
      vec<BoolView> both;
      both.push(richer[i][j]);
      both.push(richer[j][i]);
      bool_clause(none, both);
    }
  }

  // a killer always hates his victim (Agatha) and is no richer than his victim
  for (int i = 0; i < np; ++i) {
    vec<BoolView> hates_victim, not_killer;
    hates_victim.push(hates[i][AGATHA]);
    not_killer.push(is_killer[i]);
    bool_clause(hates_victim, not_killer);

    vec<BoolView> none, killer_richer;
    killer_richer.push(is_killer[i]);
    killer_richer.push(richer[i][AGATHA]);
    bool_clause(none, killer_richer);
  }

  // Charles hates no one that Agatha hates
  for (int j = 0; j < np; ++j) {
    vec<BoolView> none, agatha_and_charles;
    agatha_and_charles.push(hates[AGATHA][j]);
    agatha_and_charles.push(hates[CHARLES][j]);
    bool_clause(none, agatha_and_charles);
  }

  // Agatha hates everybody except the butler
  for (int j = 0; j < np; ++j) {
    if (j == BUTLER) {
      vec<BoolView> none, not_hated;
      not_hated.push(hates[AGATHA][j]);
      bool_clause(none, not_hated);
    } else {
      vec<BoolView> hated;
      hated.push(hates[AGATHA][j]);
      bool_clause(hated);
    }
  }

  // the butler hates everyone who is not richer than Agatha
  for (int j = 0; j < np; ++j) {
    vec<BoolView> hate_or_richer;
    hate_or_richer.push(hates[BUTLER][j]);
    hate_or_richer.push(richer[j][AGATHA]);
    bool_clause(hate_or_richer);
  }

  // the butler hates everyone whom Agatha hates
  for (int j = 0; j < np; ++j) {
    vec<BoolView> butler_hates, agatha_hates;
    butler_hates.push(hates[BUTLER][j]);
    agatha_hates.push(hates[AGATHA][j]);
    bool_clause(butler_hates, agatha_hates);
  }

  // no one hates everyone
  for (int i = 0; i < np; ++i) {
    vec<BoolView> none, someone_not_hated;
    for (int j = 0; j < np; ++j) someone_not_hated.push(hates[i][j]);
    bool_clause(none, someone_not_hated);
  }

  // branch on the killer
  vec<IntVar*> decision;
  decision.push(killer);
  branch(decision, VAR_INORDER, VAL_MIN);

  outputs = {{"killer", dcp::out(killer)}};
}
