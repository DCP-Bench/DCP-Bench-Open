FROM eclipse-temurin:21.0.8_9-jdk-noble@sha256:03b731a231066bd04ada0a7ee9003cdbc1460083344f9277245b233e5ffcbf47
RUN apt-get update && apt-get install -y --no-install-recommends python3=3.12.3-0ubuntu2.1 \
 && rm -rf /var/lib/apt/lists/*
# JaCoP and org.json from Maven Central, each checked against a pinned hash.
# JaCoP's Maven dependencies (Scala, slf4j) serve only its Scala wrapper and
# FlatZinc front end; the Java modelling API runs without them.
RUN mkdir -p /opt/jacop \
 && curl -fsSL -o /opt/jacop/jacop.jar https://repo1.maven.org/maven2/org/jacop/jacop/4.10.0/jacop-4.10.0.jar \
 && curl -fsSL -o /opt/jacop/json.jar https://repo1.maven.org/maven2/org/json/json/20250517/json-20250517.jar \
 && echo "4c7b5aa42739b2157a6763b6c0f109e35e469fbe5b63dd10ce4a5715c5635585  /opt/jacop/jacop.jar" | sha256sum -c - \
 && echo "3ea61b2a06e31edf1c91134fe9106b0ebb16628be169f3db75bc7a2b06b45796  /opt/jacop/json.jar" | sha256sum -c -
# The harness is compiled once here; at run time only the submission is compiled.
COPY solvers/jacop_java/java /opt/jacop/src
RUN javac --release 21 -cp /opt/jacop/jacop.jar:/opt/jacop/json.jar -d /opt/jacop/classes \
      /opt/jacop/src/dcp/jacop/*.java \
 && jar --create --file /opt/jacop/dcp-jacop.jar -C /opt/jacop/classes . \
 && rm -rf /opt/jacop/classes /opt/jacop/src
COPY runner/runtime.py /opt/runner/runtime.py
COPY solvers/jacop_java/run.py /opt/runner/run.py
ENTRYPOINT ["python3", "/opt/runner/run.py"]
