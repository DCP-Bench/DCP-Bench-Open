//! The binary the evaluator actually compiles.
//!
//! It glob-imports the driver prelude, splices in the staged submission, and
//! hands its `build` function to the driver. The submission never has to write
//! a `main`, declare dependencies, or touch the runner protocol.

use dcp_pumpkin::prelude::*;

include!("/input/model.rs");

fn main() {
    dcp_pumpkin::run(build);
}
