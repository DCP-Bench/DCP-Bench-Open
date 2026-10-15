// Contracting costs: a contractor pays six tradesmen in pairs. Find what each
// man charges (paper hanger, painter, plumber, electrician, carpenter, mason)
// so that every pair's total matches the amount paid for that pair.
#include "dcp.h"

class ContractingCosts : public dcp::Space {
 protected:
  // charge[0..5] = paper hanger, painter, plumber, electrician, carpenter, mason
  IntVarArray charge;

 public:
  explicit ContractingCosts(const json& instance) {
    // The problem gives no instance data: the pair totals are fixed by the statement.
    // A charge is a non-negative number of dollars. The largest pair total is
    // 5300 (carpenter and mason), so no single charge can exceed 5300.
    charge = IntVarArray(*this, 6, 0, 5300);
    IntVar paper_hanger = charge[0];
    IntVar painter      = charge[1];
    IntVar plumber      = charge[2];
    IntVar electrician  = charge[3];
    IntVar carpenter    = charge[4];
    IntVar mason        = charge[5];

    // the paper hanger and the painter together are paid $1,100
    linear(*this, IntVarArgs({paper_hanger, painter}), IRT_EQ, 1100, IPL_DOM);
    // the painter and the plumber together are paid $1,700
    linear(*this, IntVarArgs({painter, plumber}), IRT_EQ, 1700, IPL_DOM);
    // the plumber and the electrician together are paid $1,100
    linear(*this, IntVarArgs({plumber, electrician}), IRT_EQ, 1100, IPL_DOM);
    // the electrician and the carpenter together are paid $3,300
    linear(*this, IntVarArgs({electrician, carpenter}), IRT_EQ, 3300, IPL_DOM);
    // the carpenter and the mason together are paid $5,300
    linear(*this, IntVarArgs({carpenter, mason}), IRT_EQ, 5300, IPL_DOM);
    // the mason and the painter together are paid $3,200
    linear(*this, IntVarArgs({mason, painter}), IRT_EQ, 3200, IPL_DOM);

    // no objective: any assignment satisfying the pair totals is an answer
    branch(*this, charge, INT_VAR_SIZE_MIN(), INT_VAL_MIN());

    output("paper_hanger", paper_hanger);
    output("painter", painter);
    output("plumber", plumber);
    output("electrician", electrician);
    output("carpenter", carpenter);
    output("mason", mason);
  }

  ContractingCosts(ContractingCosts& s) : dcp::Space(s) {
    charge.update(*this, s.charge);
  }
  Gecode::Space* copy() override { return new ContractingCosts(*this); }
};

DCP_MODEL(ContractingCosts)
