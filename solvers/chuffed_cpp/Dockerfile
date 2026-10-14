FROM python:3.12.11-slim-bookworm@sha256:519591d6871b7bc437060736b9f7456b8731f1499a57e22e6c285135ae657bf7
RUN apt-get update && apt-get install -y --no-install-recommends g++=4:12.2.0-3 make=4.3-4.1 cmake=3.25.1-1 curl=7.88.1-10+deb12u15 ca-certificates=20250419~deb12u1 nlohmann-json3-dev=3.11.2-2 && rm -rf /var/lib/apt/lists/*
RUN curl -fL https://github.com/chuffed/chuffed/archive/refs/tags/0.14.0.tar.gz -o /tmp/chuffed.tgz && echo '8f0da88d498bc610d894b784da59f87e1e7570fe017dd7249cc90f6ae81f1267  /tmp/chuffed.tgz' | sha256sum -c - && mkdir /tmp/chuffed-src && tar xzf /tmp/chuffed.tgz -C /tmp/chuffed-src --strip-components=1 && cmake -S /tmp/chuffed-src -B /tmp/chuffed-build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/opt/chuffed && cmake --build /tmp/chuffed-build -j"$(nproc)" && cmake --install /tmp/chuffed-build && rm -rf /tmp/chuffed.tgz /tmp/chuffed-src /tmp/chuffed-build
COPY --chmod=0755 solvers/chuffed_cpp/cpp /opt/cpp
ENV CMAKE_PREFIX_PATH=/opt/chuffed
COPY --chmod=0755 runner/runtime.py solvers/chuffed_cpp/run.py /opt/runner/
ENTRYPOINT ["python", "/opt/runner/run.py"]
