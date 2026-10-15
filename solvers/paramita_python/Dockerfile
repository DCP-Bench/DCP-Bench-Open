# syntax=docker/dockerfile:1
# Paramita 1.2.0 with CaDiCaL 3.0.0, EvalMaxSAT2022 and the PB-to-CNF encoders
# pblib and pysat, built from paramita-plugins at a fixed commit.

ARG PYTHON_BASE=python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
ARG PLUGINS_REF=a9c15a0bbaca86e89eaa1cff5d4d62a4218596cb
ARG PLUGIN_DIR=/usr/local/share/paramita/plugins
# pblib and pysat both build libpairwise.so, so pysat goes to a second
# default search path to keep both.
ARG PYSAT_PLUGIN_DIR=/usr/share/paramita/plugins

# ---------------------------------------------------------------- builder
FROM ${PYTHON_BASE} AS builder
ARG PLUGINS_REF
ARG PLUGIN_DIR
ARG PYSAT_PLUGIN_DIR

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      cmake=3.25.1-1 \
      g++=4:12.2.0-3 \
      git=1:2.39.5-0+deb12u3 \
      make=4.3-4.1 \
      zlib1g-dev=1:1.2.13.dfsg-1 \
      wget=1.21.3-1+deb12u1 \
      ca-certificates=20250419~deb12u1 \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir paramita==1.2.0

RUN git clone https://codeberg.org/paramita/paramita-plugins /src/paramita-plugins \
 && git -C /src/paramita-plugins checkout --detach "${PLUGINS_REF}" \
 && git -C /src/paramita-plugins rev-parse HEAD

WORKDIR /work

# The CLI writes build.log to the working directory, hence WORKDIR /work.
RUN paramita plugins build cmake -j 4 -i "${PLUGIN_DIR}" \
      file:///src/paramita-plugins#sat-solvers/cadical-3.0.0
RUN paramita plugins build cmake -j 4 -i "${PLUGIN_DIR}" \
      file:///src/paramita-plugins#maxsat-solvers/mse22-EvalMaxSAT2022
RUN paramita plugins build cmake -j 4 -i "${PLUGIN_DIR}" \
      file:///src/paramita-plugins#pb-to-cnf-encoders/pblib
RUN paramita plugins build cmake -j 4 -i "${PYSAT_PLUGIN_DIR}" \
      file:///src/paramita-plugins#pb-to-cnf-encoders/pysat

# The install prefixes also hold headers, static libs and zlib from the build.
# Stage only the plugin shared objects for the runtime stage.
RUN mkdir -p /out \
 && for d in "${PLUGIN_DIR}" "${PYSAT_PLUGIN_DIR}"; do \
      find "$d" -name '*.so' -not -path "$d/lib/*" -exec cp --parents {} /out/ \; ; \
    done \
 && find /out -type f | sort

# ---------------------------------------------------------------- runtime
FROM ${PYTHON_BASE} AS runtime

RUN pip install --no-cache-dir paramita==1.2.0

COPY --from=builder /out/ /
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/paramita_python/run.py /opt/runner/run.py
ENTRYPOINT ["python", "/opt/runner/run.py"]
