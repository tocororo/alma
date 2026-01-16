FROM localhost/invenioupr:1

# Create working directory
ENV WORKING_DIR=/opt/invenio
ENV INVENIO_INSTANCE_PATH=${WORKING_DIR}/var/instance

# Copy site folder and install its dependencies
COPY site ./site
# RUN if [ -f "./site/setup.py" ]; then pip install -e ./site; fi

COPY Pipfile ./
RUN pipenv lock 
RUN pipenv install --deploy --system

COPY ./docker/uwsgi/ ${INVENIO_INSTANCE_PATH}
COPY ./invenio.cfg ${INVENIO_INSTANCE_PATH}
COPY ./templates/ ${INVENIO_INSTANCE_PATH}/templates/
COPY ./app_data/ ${INVENIO_INSTANCE_PATH}/app_data/
COPY ./translations/ ${INVENIO_INSTANCE_PATH}/translations/

RUN rm -R ${INVENIO_INSTANCE_PATH}/static/

COPY ./static/ ${INVENIO_INSTANCE_PATH}/static/ 

RUN  ls -alh ${INVENIO_INSTANCE_PATH}/static/

COPY ./assets/ ${INVENIO_INSTANCE_PATH}/assets/ 

RUN  ls -alh ${INVENIO_INSTANCE_PATH}/assets/

RUN invenio alma i18n-distribute-js-translations --input-directory ${INVENIO_INSTANCE_PATH}/translations/

RUN  ls -alh ${INVENIO_INSTANCE_PATH}/assets/

RUN invenio collect --verbose 

RUN invenio webpack buildall



# RUN rm -R ${INVENIO_INSTANCE_PATH}/static/

# RUN cp -r ./static/. ${INVENIO_INSTANCE_PATH}/static/ && \
#     cp -r ./assets/. ${INVENIO_INSTANCE_PATH}/assets/ && \
#     invenio collect --verbose  && \
#     invenio webpack buildall

# COPY ./invenio-cli /opt/invenio-cli
# RUN ls /opt/invenio-cli
# RUN pip install /opt/invenio-cli

ENTRYPOINT [ "bash", "-c"]
