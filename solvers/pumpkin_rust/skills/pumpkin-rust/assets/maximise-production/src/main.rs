// Maximise profit 3x + 2y for whole units of two products under two capacity limits.
use std::ops::ControlFlow;
use std::time::Duration;

use pumpkin_solver::conflict_resolvers::resolvers::ResolutionResolver;
use pumpkin_solver::core::DefaultBrancher;
use pumpkin_solver::core::optimisation::OptimisationDirection;
use pumpkin_solver::core::optimisation::linear_sat_unsat::LinearSatUnsat;
use pumpkin_solver::core::results::{OptimisationResult, ProblemSolution, SolutionReference};
use pumpkin_solver::core::termination::TimeBudget;
use pumpkin_solver::core::variables::TransformableVariable;
use pumpkin_solver::Solver;

fn main() {
    let mut solver = Solver::default();
    let x = solver.new_bounded_integer(0, 10);
    let y = solver.new_bounded_integer(0, 10);
    let profit = solver.new_bounded_integer(0, 30);

    // x + y <= 4 and x + 3y <= 6.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(vec![x.scaled(1), y.scaled(1)], 4, tag))
        .post();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::less_than_or_equals(vec![x.scaled(1), y.scaled(3)], 6, tag))
        .post();
    // profit = 3x + 2y, written as 3x + 2y - profit = 0.
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::equals(
            vec![x.scaled(3), y.scaled(2), profit.scaled(-1)],
            0,
            tag,
        ))
        .post();

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
    let procedure = LinearSatUnsat::new(
        OptimisationDirection::Maximise,
        profit,
        |_: &Solver, _: SolutionReference, _: &DefaultBrancher, _: &ResolutionResolver| {
            ControlFlow::<()>::Continue(())
        },
    );
    match solver.optimise(&mut brancher, &mut termination, &mut resolver, procedure) {
        OptimisationResult::Optimal(solution) => println!(
            "maximum profit: {}\nx = {}, y = {}",
            solution.get_integer_value(profit),
            solution.get_integer_value(x),
            solution.get_integer_value(y)
        ),
        OptimisationResult::Unsatisfiable => println!("no plan exists"),
        _ => println!("optimality not proven"),
    }
}
