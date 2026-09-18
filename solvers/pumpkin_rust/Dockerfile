FROM rust:1.98.1-slim-bookworm@sha256:ebd900bae66fd508b466cef82d64a83a5fb34682e4c8b2797a42908bddc95a57
RUN apt-get update && apt-get install -y --no-install-recommends python3=3.11.2-1+b1 && rm -rf /var/lib/apt/lists/*
# Cargo.lock is committed and the build is --locked, so the crate graph is the
# one that was tested rather than whatever resolves on the day of the build.
COPY solvers/pumpkin_rust/rust/driver /opt/crate
WORKDIR /opt/crate
# pumpkin-solver's build script shells out to `git` for a version stamp, and
# without NO_CHECKERS it also compiles proof checkers from a `tests/` directory
# the published crate does not ship. git is a build-time need only, so it is
# installed and removed inside one layer.
#
# Only what rustc needs to link a submission is kept: the driver rlib, the
# dependency rlibs, and the proc-macro dependencies, which build to .so rather
# than .rlib and are needed all the same. The Cargo target directory and the
# registry cache are build-time only, and /tmp is a 512 MiB tmpfs at run time.
RUN apt-get update && apt-get install -y --no-install-recommends git=1:2.39.5-0+deb12u2 \
 && NO_CHECKERS=true cargo build --locked --release \
 && mkdir -p /opt/rust/deps \
 && cp /opt/crate/target/release/libdcp_pumpkin.rlib /opt/rust/libdcp_pumpkin.rlib \
 && cp /opt/crate/target/release/deps/*.rlib /opt/rust/deps/ \
 && cp /opt/crate/target/release/deps/*.so /opt/rust/deps/ \
 && rm -rf /opt/crate/target /usr/local/cargo/registry /usr/local/rustup/toolchains/*/share/doc \
 && apt-get purge -y git && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*
COPY solvers/pumpkin_rust/rust/main.rs /opt/rust/main.rs
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/pumpkin_rust/run.py /opt/runner/run.py
ENTRYPOINT ["python3", "/opt/runner/run.py"]
