// Colour a small graph with three colours so that no edge joins two equal colours.
use std::time::Duration;

use pumpkin_solver::conflict_resolvers::resolvers::ResolutionResolver;
use pumpkin_solver::core::results::{ProblemSolution, SatisfactionResult};
use pumpkin_solver::core::termination::TimeBudget;
use pumpkin_solver::core::variables::TransformableVariable;
use pumpkin_solver::Solver;

fn main() {
    // A 5-cycle 0-1-2-3-4-0 with the chord 0-2.
    let edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2)];
    let vertices = 5;

    let mut solver = Solver::default();
    let colour: Vec<_> = (0..vertices).map(|_| solver.new_bounded_integer(0, 2)).collect();

    // One tag for the whole group: every edge says the same thing.
    let edge_tag = solver.new_constraint_tag();
    for &(u, v) in &edges {
        solver
            .add_constraint(pumpkin_solver::not_equals(
                vec![colour[u].scaled(1), colour[v].scaled(-1)],
                0,
                edge_tag,
            ))
            .post();
    }

    let mut brancher = solver.default_brancher();
    let mut resolver = ResolutionResolver::default();
    let mut termination = TimeBudget::starting_now(Duration::from_secs(10));
    let result = solver.satisfy(&mut brancher, &mut termination, &mut resolver);
    match result {
        SatisfactionResult::Satisfiable(found) => {
            let solution = found.solution();
            let colours: Vec<i32> = colour.iter().map(|&c| solution.get_integer_value(c)).collect();
            println!("colours: {colours:?}");
        }
        SatisfactionResult::Unsatisfiable(..) => println!("no colouring exists"),
        SatisfactionResult::Unknown(..) => println!("time limit reached"),
    }
}
