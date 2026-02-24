# ===== STAGE 1: Builder =====
# Esta etapa maneja todas las dependencias de construcción y compilación
FROM docker.uclv.cu/python:3.12-slim-bookworm AS builder

# Set locale (igual que la imagen base)
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    rm -rf /var/lib/apt/lists/*

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install ALL system dependencies needed for building
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    libcairo2-dev \
    libffi-dev \
    libpq-dev \
    libxml2-dev \
    libxslt-dev \
    libxmlsec1-dev \
    imagemagick \
    libssl-dev \
    libbz2-dev \
    liblzma-dev \
    libsqlite3-dev \
    fonts-dejavu \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js v22 (needed for webpack asset compilation)
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs

# Upgrade pip and install build tools
RUN python -m pip install --upgrade pip wheel setuptools

# Create working directory structure
ENV WORKING_DIR=/opt/invenio
ENV INVENIO_INSTANCE_PATH=${WORKING_DIR}/var/instance

RUN mkdir -p ${INVENIO_INSTANCE_PATH} && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/data ${INVENIO_INSTANCE_PATH}/archive ${INVENIO_INSTANCE_PATH}/static && \
    mkdir -p ${WORKING_DIR}/src

WORKDIR ${WORKING_DIR}/src

# Copy requirements first for better layer caching
COPY requirements.prod.txt ./

# Copy site folder and install alma module (non-editable)
COPY site ./site

# Install production dependencies with build tools
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.prod.txt

# Copy application files needed for asset building
COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}/
COPY ./invenio.cfg ${INVENIO_INSTANCE_PATH}/
COPY ./templates/ ${INVENIO_INSTANCE_PATH}/templates/
COPY ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data/
COPY ./translations/ ${INVENIO_INSTANCE_PATH}/translations/

# Copy static assets
COPY ./static/ ${INVENIO_INSTANCE_PATH}/static/
COPY ./assets/ ${INVENIO_INSTANCE_PATH}/assets/

# Build and collect assets - this is the expensive part that needs build tools
RUN invenio alma i18n-distribute-js-translations --input-directory ${INVENIO_INSTANCE_PATH}/translations/ 

RUN invenio collect --verbose

RUN invenio webpack buildall

# ===== STAGE 2: Runtime =====
# Esta etapa es la imagen final minimalista
FROM docker.uclv.cu/python:3.12-slim-bookworm

# Set locale (same as base image)
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales && \
    sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen && \
    rm -rf /var/lib/apt/lists/*

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

# Install ONLY runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2 \
    libffi8 \
    libpq5 \
    libxml2 \
    libxslt1.1 \
    libxmlsec1 \
    imagemagick \
    libssl3 \
    libbz2-1.0 \
    liblzma5 \
    libsqlite3-0 \
    fonts-dejavu \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create working directory structure
ENV WORKING_DIR=/opt/invenio
ENV INVENIO_INSTANCE_PATH=${WORKING_DIR}/var/instance
ENV INVENIO_USER_ID=1000

RUN mkdir -p ${INVENIO_INSTANCE_PATH} && \
    mkdir -p ${INVENIO_INSTANCE_PATH}/data ${INVENIO_INSTANCE_PATH}/archive ${INVENIO_INSTANCE_PATH}/static && \
    mkdir -p ${WORKING_DIR}/src && \
    chgrp -R 0 ${WORKING_DIR} && \
    chmod -R g=u ${WORKING_DIR} && \
    useradd invenio --uid ${INVENIO_USER_ID} --gid 0 && \
    chown -R invenio:root ${WORKING_DIR}

WORKDIR ${WORKING_DIR}

# Copy binaries
COPY --from=builder /usr/local/bin/celery /usr/local/bin/celery
COPY --from=builder /usr/local/bin/uwsgi /usr/local/bin/uwsgi
COPY --from=builder /usr/local/bin/invenio /usr/local/bin/invenio
COPY --from=builder /usr/local/bin/flask /usr/local/bin/flask
COPY --from=builder /usr/local/bin/pybabel /usr/local/bin/pybabel
COPY --from=builder /usr/local/bin/ipython /usr/local/bin/ipython

# copy python packages...
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages

# Copy application files (excluding the directories that will be volumes)
COPY --from=builder ${INVENIO_INSTANCE_PATH}/uwsgi_rest.ini ${INVENIO_INSTANCE_PATH}/uwsgi_rest.ini
COPY --from=builder ${INVENIO_INSTANCE_PATH}/uwsgi_ui.ini ${INVENIO_INSTANCE_PATH}/uwsgi_ui.ini
COPY --from=builder ${INVENIO_INSTANCE_PATH}/invenio.cfg ${INVENIO_INSTANCE_PATH}/invenio.cfg
COPY --from=builder ${INVENIO_INSTANCE_PATH}/templates ${INVENIO_INSTANCE_PATH}/templates
COPY --from=builder ${INVENIO_INSTANCE_PATH}/translations ${INVENIO_INSTANCE_PATH}/translations
COPY --from=builder ${INVENIO_INSTANCE_PATH}/assets ${INVENIO_INSTANCE_PATH}/assets

# Copy application instance files (only runtime necessary files)
COPY --from=builder ${INVENIO_INSTANCE_PATH} ${INVENIO_INSTANCE_PATH}


# Production optimizations - clean up unnecessary files
RUN find ${INVENIO_INSTANCE_PATH} -type f -name '*.pyc' -delete && \
    find ${INVENIO_INSTANCE_PATH} -type d -name '__pycache__' -delete && \
    find ${INVENIO_INSTANCE_PATH}/static -name '*.map' -delete && \
    find ${INVENIO_INSTANCE_PATH}/assets -name '*.map' -delete && \
    rm -rf ${INVENIO_INSTANCE_PATH}/translations/*.po && \
    rm -rf /root/.cache

# Set proper permissions
RUN chown -R invenio:root ${WORKING_DIR} && \
    chmod -R g=u ${WORKING_DIR}



# Switch to non-root user for security
USER invenio

# ===== DECLARE VOLUME MOUNT POINTS =====
# These directories will be mounted as volumes at runtime
VOLUME [ \
    "${INVENIO_INSTANCE_PATH}/static", \
    "${INVENIO_INSTANCE_PATH}/data", \
    "${INVENIO_INSTANCE_PATH}/archive", \
    "${INVENIO_INSTANCE_PATH}/app_data" \
]

ENTRYPOINT [ "bash", "-c"]