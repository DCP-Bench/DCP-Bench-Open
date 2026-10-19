// Minimise the number of colours. Pumpkin has no count-distinct constraint, so the model
// minimises the largest colour index instead. Colours start at 0, so the number of colours
// is that optimum + 1.
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
    // Petersen graph: outer cycle 0-4, spokes i-(i+5), inner pentagram 5-7-9-6-8-5.
    let mut edges = vec![(0, 1), (1, 2), (2, 3), (3, 4), (4, 0)];
    edges.extend((0..5).map(|i| (i, i + 5)));
    edges.extend([(5, 7), (7, 9), (9, 6), (6, 8), (8, 5)]);
    let n = 10;

    let mut solver = Solver::default();
    let colour: Vec<_> = (0..n).map(|_| solver.new_bounded_integer(0, n as i32 - 1)).collect();
    let top = solver.new_bounded_integer(0, n as i32 - 1);

    let tag = solver.new_constraint_tag();
    for &(u, v) in &edges {
        solver
            .add_constraint(pumpkin_solver::not_equals(vec![colour[u].scaled(1), colour[v].scaled(-1)], 0, tag))
            .post();
    }
    let tag = solver.new_constraint_tag();
    solver.add_constraint(pumpkin_solver::maximum(colour.clone(), top, tag)).post();

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
    let procedure = LinearSatUnsat::new(
        OptimisationDirection::Minimise,
        top,
        |_: &Solver, _: SolutionReference, _: &DefaultBrancher, _: &ResolutionResolver| {
            ControlFlow::<()>::Continue(())
        },
    );
    match solver.optimise(&mut brancher, &mut termination, &mut resolver, procedure) {
        OptimisationResult::Optimal(solution) => {
            let cols: Vec<i32> = colour.iter().map(|&c| solution.get_integer_value(c)).collect();
            let count = solution.get_integer_value(top) + 1;
            println!("colours: {cols:?}");
            println!("chromatic number: {count}");
        }
        _ => println!("optimality not proven"),
    }
}
