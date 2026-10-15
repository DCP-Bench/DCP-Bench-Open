// Split weights into two groups so that the heavier group is as light as possible.
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
    let weights = [3, 1, 4, 2, 2];
    let total: i32 = weights.iter().sum();

    let mut solver = Solver::default();
    // in_first[i] is true when item i goes to the first group.
    let in_first: Vec<_> = weights.iter().map(|_| solver.new_literal()).collect();
    let first = solver.new_bounded_integer(0, total);
    let second = solver.new_bounded_integer(0, total);
    let heavier = solver.new_bounded_integer(0, total);

    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(weights.to_vec(), in_first.clone(), first, tag))
        .post();
    // The second group takes the negated literals.
    let complement: Vec<_> = in_first.iter().map(|&p| !p).collect();
    let tag = solver.new_constraint_tag();
    solver
        .add_constraint(pumpkin_solver::boolean_equals(weights.to_vec(), complement, second, tag))
        .post();

    // heavier >= first and heavier >= second.
    for group in [first, second] {
        let tag = solver.new_constraint_tag();
        solver
            .add_constraint(pumpkin_solver::less_than_or_equals(
                vec![group.scaled(1), heavier.scaled(-1)],
                0,
                tag,
            ))
            .post();
    }

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
    let procedure = LinearSatUnsat::new(
        OptimisationDirection::Minimise,
        heavier,
        |_: &Solver, _: SolutionReference, _: &DefaultBrancher, _: &ResolutionResolver| {
            ControlFlow::<()>::Continue(())
        },
    );
    match solver.optimise(&mut brancher, &mut termination, &mut resolver, procedure) {
        OptimisationResult::Optimal(solution) => {
            let group: Vec<usize> = in_first
                .iter()
                .enumerate()
                .filter(|(_, &p)| solution.get_integer_value(p) == 1)
                .map(|(i, _)| i)
                .collect();
            println!("heavier group weight: {}", solution.get_integer_value(heavier));
            println!("first group items (0-based): {group:?}");
        }
        OptimisationResult::Unsatisfiable => println!("no split exists"),
        _ => println!("optimality not proven"),
    }
}
