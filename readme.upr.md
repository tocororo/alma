# run 

```bash

invenio-cli install

podman-compose -f podman-compose.dev.yml up -d

invenio-cli services setup --no-demo-data  --no-services



invenio vocabularies update --vocabulary names  --filepath ./app_data/vocabs.yaml

invenio vocabularies update --vocabulary uprfacultades  --filepath ./app_data/vocabularies.yaml

invenio rdm-records fixtures

invenio rdm-records add-to-fixtures upr:facultades

invenio roles create community-creator

invenio-cli assets build

invenio-cli run all --celery-log-file ./.data/celery.log --no-debug --no-services


```