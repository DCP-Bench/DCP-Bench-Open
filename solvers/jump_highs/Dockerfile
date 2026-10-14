# JuMP with HiGHS on the official Julia 1.12.7 image. Project.toml and
# Manifest.toml pin every Julia package (JuMP 1.32.0, HiGHS.jl 1.26.0 with its
# HiGHS binary, JSON 1.10.0); they are installed and precompiled here, so a run
# loads them from a read-only depot and never touches the network. Python runs
# the runner around the julia process.
FROM julia:1.12-bookworm@sha256:709daad7eccdb0363b080df203601988cff8c6a9581162668b76804cca407888
RUN apt-get update && apt-get install -y --no-install-recommends python3=3.11.2-1+b1 \
 && rm -rf /var/lib/apt/lists/*
ENV JULIA_PROJECT=/opt/jump JULIA_DEPOT_PATH=/opt/julia-depot JULIA_PKG_OFFLINE=false
COPY solvers/jump_highs/Project.toml solvers/jump_highs/Manifest.toml /opt/jump/
RUN julia -e 'using Pkg; Pkg.instantiate(); Pkg.precompile(); using JuMP, HiGHS, JSON' \
 && chmod -R a+rX /opt/julia-depot /opt/jump
# At run time the first depot, in the writable /tmp, takes anything Julia wants to
# write; the packages come from the read-only one.
ENV JULIA_DEPOT_PATH=/tmp/julia-depot:/opt/julia-depot JULIA_PKG_OFFLINE=true
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/jump_highs/run.py /opt/runner/run.py
COPY solvers/jump_highs/driver.jl /opt/runner/driver.jl
ENTRYPOINT ["python3", "/opt/runner/run.py"]
