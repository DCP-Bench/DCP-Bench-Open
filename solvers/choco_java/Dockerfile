FROM eclipse-temurin:21-jdk-noble@sha256:b468c3fc688b14450571494f588bd939378e7fd542ed5a73f8efc13f17872a87
RUN apt-get update && apt-get install -y --no-install-recommends python3=3.12.3-0ubuntu2.1 && rm -rf /var/lib/apt/lists/*
# Choco 6.0.1 as Maven Central publishes it, with its dependencies bundled, and
# Gson for the request JSON. Both are checked against their published hashes.
ADD --checksum=sha256:c1956f7688f0982c55dc12edfa5695b60085fb9c37f3fbc6cf7efc53afc0da39 \
    https://repo1.maven.org/maven2/org/choco-solver/choco-solver/6.0.1/choco-solver-6.0.1-jar-with-dependencies.jar /opt/java/choco-solver.jar
ADD --checksum=sha256:57928d6e5a6edeb2abd3770a8f95ba44dce45f3b23b7a9dc2b309c581552a78b \
    https://repo1.maven.org/maven2/com/google/code/gson/gson/2.11.0/gson-2.11.0.jar /opt/java/gson.jar
COPY solvers/choco_java/java/dcp /opt/java/src/dcp
RUN chmod 0644 /opt/java/*.jar \
 && javac -encoding UTF-8 -cp "/opt/java/choco-solver.jar:/opt/java/gson.jar" -d /opt/java/classes /opt/java/src/dcp/*.java \
 && jar --create --file /opt/java/dcp.jar -C /opt/java/classes . \
 && rm -rf /opt/java/classes /opt/java/src
COPY --chmod=0755 runner/runtime.py solvers/choco_java/run.py /opt/runner/
ENTRYPOINT ["python3", "/opt/runner/run.py"]
