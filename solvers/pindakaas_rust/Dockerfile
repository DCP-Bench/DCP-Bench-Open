FROM rust:1.98.1-slim-bookworm@sha256:ebd900bae66fd508b466cef82d64a83a5fb34682e4c8b2797a42908bddc95a57
RUN apt-get update && apt-get install -y --no-install-recommends python3=3.11.2-1+b1 && rm -rf /var/lib/apt/lists/*
COPY solvers/pindakaas_rust/rust/driver /opt/crate
WORKDIR /opt/crate
# Cargo.lock is committed and the build is --locked, so the crate graph is the
# one that was tested rather than whatever resolves on the day of the build.
#
# pindakaas compiles CaDiCaL with the cc crate, which needs a C++ compiler.
# g++ is a build-time need only, so it is purged in the same layer. Submissions are
# linked by rustc through cc against the static CaDiCaL objects, which need the
# libstdc++ shared object; its development package (the linker's name for it) stays.
#
# Only what rustc needs to link a submission is kept: the driver rlib, the
# dependency rlibs (this crate graph has no proc-macro dependencies, so there are no
# .so files to keep). The Cargo target directory and the
# registry cache are build-time only, and /tmp is a 512 MiB tmpfs at run time.
RUN apt-get update && apt-get install -y --no-install-recommends g++=4:12.2.0-3 libstdc++-12-dev=12.2.0-14+deb12u1 \
 && cargo build --locked --release \
 && mkdir -p /opt/rust/deps \
 && cp /opt/crate/target/release/libdcp_pindakaas.rlib /opt/rust/libdcp_pindakaas.rlib \
 && cp /opt/crate/target/release/deps/*.rlib /opt/rust/deps/ \
 && rm -rf /opt/crate/target /usr/local/cargo/registry /usr/local/rustup/toolchains/*/share/doc \
 && apt-get purge -y g++ g++-12 && rm -rf /var/lib/apt/lists/*
COPY solvers/pindakaas_rust/rust/main.rs /opt/rust/main.rs
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/pindakaas_rust/run.py /opt/runner/run.py
ENTRYPOINT ["python3", "/opt/runner/run.py"]
