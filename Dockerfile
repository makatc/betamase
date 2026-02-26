###################
# STAGE 1: builder
###################

FROM ubuntu:22.04 AS builder

ARG MB_EDITION=oss
ARG VERSION=v0.48.0-custom

ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV JAVA_HOME=/usr/lib/jvm/temurin-21
ENV PATH="$JAVA_HOME/bin:/usr/local/bin:$PATH"

WORKDIR /app

# 1) Instalar dependencias del sistema: Java 21 (Temurin), Node 22, git, curl
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl git gpg apt-transport-https ca-certificates \
    build-essential python3 rlwrap \
    && wget -qO - https://packages.adoptium.net/artifactory/api/gpg/key/public \
    | gpg --dearmor -o /etc/apt/trusted.gpg.d/adoptium.gpg \
    && echo "deb https://packages.adoptium.net/artifactory/deb $(. /etc/os-release; echo $VERSION_CODENAME) main" \
    > /etc/apt/sources.list.d/adoptium.list \
    && apt-get update && apt-get install -y temurin-21-jdk \
    && curl -fsSL https://deb.nodesource.com/setup_22.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# 2) Instalar Clojure CLI (instala en /usr/local/bin/clojure)
RUN curl -L -O https://download.clojure.org/install/linux-install-1.12.0.1488.sh \
    && chmod +x linux-install-1.12.0.1488.sh \
    && ./linux-install-1.12.0.1488.sh \
    && rm linux-install-1.12.0.1488.sh \
    && clojure --version

# 3) Instalar pip y uv (necesario para las dependencias Python del build)
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv \
    && uv --version

# 5) Instalar bun
RUN npm install -g bun

# 6) Copiar fuentes
COPY . .

# 5) Git safe dir (necesario porque el Dockerfile corre como root)
RUN git config --global --add safe.directory /app

# 6) Instalar dependencias JS
RUN bun install

# 7) Compilar todo (Frontend + Backend JAR)
RUN INTERACTIVE=false CI=true MB_EDITION=$MB_EDITION \
    bin/build.sh :version "$VERSION"

# ###################
# # STAGE 2: runner
# ###################

## Remember that this runner image needs to be the same as bin/docker/Dockerfile with the exception that this one grabs the
## jar from the previous stage rather than the local build

FROM eclipse-temurin:21-jre-alpine AS runner

ENV FC_LANG=en-US LC_CTYPE=en_US.UTF-8

# dependencies
RUN apk add -U bash fontconfig curl font-noto font-noto-arabic font-noto-hebrew font-noto-cjk java-cacerts && \
    apk upgrade && \
    rm -rf /var/cache/apk/* && \
    mkdir -p /app/certs && \
    curl https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem -o /app/certs/rds-combined-ca-bundle.pem  && \
    /opt/java/openjdk/bin/keytool -noprompt -import -trustcacerts -alias aws-rds -file /app/certs/rds-combined-ca-bundle.pem -keystore /etc/ssl/certs/java/cacerts -keypass changeit -storepass changeit && \
    curl https://cacerts.digicert.com/DigiCertGlobalRootG2.crt.pem -o /app/certs/DigiCertGlobalRootG2.crt.pem  && \
    /opt/java/openjdk/bin/keytool -noprompt -import -trustcacerts -alias azure-cert -file /app/certs/DigiCertGlobalRootG2.crt.pem -keystore /etc/ssl/certs/java/cacerts -keypass changeit -storepass changeit && \
    mkdir -p /plugins && chmod a+rwx /plugins

# add Metabase script and uberjar
COPY --from=builder /app/target/uberjar/metabase.jar /app/
COPY bin/docker/run_metabase.sh /app/

# expose our default runtime port
EXPOSE 3000

# run it
ENTRYPOINT ["/app/run_metabase.sh"]
