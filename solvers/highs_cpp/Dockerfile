FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7 AS highs-build
# HiGHS v1.15.1 (latest release), built from source at a pinned commit.
RUN apt-get update && apt-get install -y --no-install-recommends g++=4:12.2.0-3 make=4.3-4.1 cmake=3.25.1-1 git=1:2.39.5-0+deb12u2 && rm -rf /var/lib/apt/lists/*
RUN git clone --depth 1 --branch v1.15.1 https://github.com/ERGO-Code/HiGHS.git /src/HiGHS \
 && test "$(git -C /src/HiGHS rev-parse HEAD)" = "04024d701f79feb8e2f18bc3df0dffc04ef05088"
RUN cmake -S /src/HiGHS -B /build/highs -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/highs \
      -DBUILD_SHARED_LIBS=OFF -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF -DBUILD_CXX_EXE=OFF \
      -DZLIB=OFF -DFAST_BUILD=ON \
 && cmake --build /build/highs -j2 \
 && cmake --install /build/highs

FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN apt-get update && apt-get install -y --no-install-recommends g++=4:12.2.0-3 make=4.3-4.1 cmake=3.25.1-1 nlohmann-json3-dev=3.11.2-2 && rm -rf /var/lib/apt/lists/*
COPY --from=highs-build /opt/highs /opt/highs
ENV CMAKE_PREFIX_PATH=/opt/highs
COPY --chmod=0755 solvers/highs_cpp/cpp /opt/cpp
COPY --chmod=0755 runner/runtime.py solvers/highs_cpp/run.py /opt/runner/
ENTRYPOINT ["python", "/opt/runner/run.py"]
