// The submission (/input/model.rs) is spliced in as items of this crate, so it
// can use the prelude names without importing them and cannot define `main`.
use dcp_pindakaas::prelude::*;

include!("/input/model.rs");

fn main() {
    dcp_pindakaas::run(build);
}
