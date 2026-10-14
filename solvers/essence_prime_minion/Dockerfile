# Savile Row 1.11.1 (Essence' to Minion). Java 17 runtime for Savile Row, python3 for the runner.
FROM eclipse-temurin:17-jre-jammy@sha256:8993f1aed8b25fcea7a7047a7949c1866fa558fc6830d938c22c4f13b26be9d7
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3-minimal curl ca-certificates \
 && ln -s python3 /usr/bin/python \
 && curl -fsSL -o /tmp/savilerow.tgz https://www-users.york.ac.uk/peter.nightingale/savilerow/savilerow-1.11.1-linux.tgz \
 && echo "7b9653bb9ffa8fd71b29f3d5c2de41011cdc136ed2241f82b39f86aa9b3489c6  /tmp/savilerow.tgz" | sha256sum -c - \
 && mkdir /opt/savilerow \
 && tar -xzf /tmp/savilerow.tgz -C /opt/savilerow --strip-components=1 \
 && rm -rf /tmp/savilerow.tgz /opt/savilerow/examples /opt/savilerow/bin/fzn-chuffed /opt/savilerow/bin/kissat \
 && chmod -R a+rX /opt/savilerow \
 && apt-get purge -y --auto-remove curl \
 && rm -rf /var/lib/apt/lists/*
# python3-minimal above has no json module; the full interpreter package adds the standard library.
RUN apt-get update \
 && apt-get install -y --no-install-recommends python3 \
 && rm -rf /var/lib/apt/lists/*
COPY --chmod=0755 runner/runtime.py solvers/essence_prime_minion/run.py /opt/runner/
ENTRYPOINT ["python", "/opt/runner/run.py"]
