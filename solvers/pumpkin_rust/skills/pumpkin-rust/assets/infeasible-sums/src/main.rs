// Two integers from 0 to 2 cannot add up to 5: the solver proves there is no solution.
use std::time::Duration;

use pumpkin_solver::conflict_resolvers::resolvers::ResolutionResolver;
use pumpkin_solver::core::results::SatisfactionResult;
use pumpkin_solver::core::termination::TimeBudget;
use pumpkin_solver::core::variables::TransformableVariable;
use pumpkin_solver::Solver;

fn main() {
    let mut solver = Solver::default();
    let a = solver.new_bounded_integer(0, 2);
    let b = solver.new_bounded_integer(0, 2);

    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(vec![a.scaled(1), b.scaled(1)], 5, tag))
        .post();

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
    let result = solver.satisfy(&mut brancher, &mut termination, &mut resolver);
    match result {
        SatisfactionResult::Satisfiable(_) => println!("unexpected solution"),
        SatisfactionResult::Unsatisfiable(..) => println!("no solution: proven infeasible"),
        SatisfactionResult::Unknown(..) => println!("time limit reached"),
    }
}
