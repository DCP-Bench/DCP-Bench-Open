FROM eclipse-temurin:21-jdk-noble@sha256:b468c3fc688b14450571494f588bd939378e7fd542ed5a73f8efc13f17872a87
RUN apt-get update && apt-get install -y --no-install-recommends python3=3.12.3-0ubuntu2.1 && rm -rf /var/lib/apt/lists/*
# MaxiCP 0.0.3, the latest release on Maven Central (org.maxicp:maxicp), with the
# sha256 that Maven Central publishes for it, and Gson 2.11.0 for the request JSON.
ADD --checksum=sha256:904df52ac0b0125661abfc9a3eedfdef7f95c241a84ac571ae194f05ff7c90d6 \
    https://repo1.maven.org/maven2/org/maxicp/maxicp/0.0.3/maxicp-0.0.3.jar /opt/java/maxicp.jar
ADD --checksum=sha256:57928d6e5a6edeb2abd3770a8f95ba44dce45f3b23b7a9dc2b309c581552a78b \
    https://repo1.maven.org/maven2/com/google/code/gson/gson/2.11.0/gson-2.11.0.jar /opt/java/gson.jar
COPY solvers/maxicp_java/java/dcp /opt/java/src/dcp
RUN chmod 0644 /opt/java/*.jar \
 && javac -encoding UTF-8 -cp "/opt/java/maxicp.jar:/opt/java/gson.jar" -d /opt/java/classes /opt/java/src/dcp/*.java \
 && jar --create --file /opt/java/dcp.jar -C /opt/java/classes . \
 && rm -rf /opt/java/classes /opt/java/src
COPY --chmod=0755 runner/runtime.py solvers/maxicp_java/run.py /opt/runner/
ENTRYPOINT ["python3", "/opt/runner/run.py"]
