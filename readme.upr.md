# setup local...



```bash

invenio-cli install

podman-compose -f podman-compose.dev.yml up -d

invenio-cli services setup --no-demo-data  --no-services

invenio vocabularies update --vocabulary names  --filepath ./app_data/vocabs.yaml

invenio rdm-records fixtures

invenio rdm-records add-to-fixture upr:entidades

invenio rdm-records add-to-fixture upr:materias

invenio roles create community-creator

invenio-cli assets build

invenio users create --password "Rme.2024" --active --confirm rafael.martinez@upr.edu.cu
invenio roles add rafael.martinez@upr.edu.cu admin

invenio-cli run all --celery-log-file ./.data/celery.log --no-debug --no-services


```

# setup production

## 1- prepare alma vm, ejecutar una vez

```bash
podman image pull public.ecr.aws/opensearchproject/opensearch:2.17.1
podman image pull registry.cern.ch/inveniosoftware/almalinux:1
podman image pull quay.io/lib/redis:7
podman image pull quay.io/lib/postgres:14.13
podman image pull quay.io/lib/rabbitmq:3-management
podman image pull quay.io/lib/nginx:latest

sudo mkdir -p /alma/data/{redis,postgres,opensearch,rabbitmq,static,uploaded,archived}
sudo mkdir /alma/code
```

## 2- sincronizar codigo
```bash
rsync -avzP --no-perms --no-owner --no-group --delete --exclude='.venv' --exclude='.git' --exclude='.data' -e 'ssh' ../ root@10.2.6.168:/alma/code
```
## 3- construir la image base para invenio

```bash
podman build -f Dockerfile.base  --no-cache -t localhost/invenioupr:1
```


## 3- rebuild and reload compose..

``` bash
podman-compose -f podman-services.prod.yml build --no-cache --build-arg HTTP_PROXY=http://rafael.martinez:Rme.2021@proxy.upr.edu.cu:8080 --build-arg HTTPS_PROXY=http://rafael.martinez:Rme.2021@proxy.upr.edu.cu:8080 app

podman-compose -f podman-services.prod.yml build --no-cache --build-arg HTTP_PROXY=http://rafael.martinez:Rme.2021@proxy.upr.edu.cu:8080 --build-arg HTTPS_PROXY=http://rafael.martinez:Rme.2021@proxy.upr.edu.cu:8080 frontend

podman-compose -f podman-compose.prod.yml up -d --force-recreate

```

## 4- initial data 

```bash
# podman exec code_web-api_1 invenio db drop --yes-i-know
# podman exec code_web-api_1 invenio index destroy --force --yes-i-know && \


podman exec code_web-api_1 invenio db init create && \
podman exec code_web-api_1 invenio files location create --default default-location file:///opt/invenio/var/instance/data && \
podman exec code_web-api_1 invenio roles create admin && \
podman exec code_web-api_1 invenio access allow superuser-access role admin && \
podman exec code_web-api_1 invenio index init && \
podman exec code_web-api_1 invenio rdm-records custom-fields init && \
podman exec code_web-api_1 invenio communities custom-fields init && \
podman exec code_web-api_1 invenio rdm fixtures && \
podman exec code_web-api_1 invenio queues declare && \
podman exec code_web-api_1 invenio rdm-records fixtures && \

podman exec code_web-api_1 invenio users create admin@alma.upr.edu.cu --active --confirm --password /*Alma.Admin.2026*/ && \

podman exec code_web-api_1 invenio roles add admin@alma.upr.edu.cu admin

podman exec code_web-api_1 invenio rdm-records add-to-fixture creatorsroles && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture contributorsroles && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture resourcetypes && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture affiliations && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture descriptiontypes && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture datetypes && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture relationtypes && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture removalreasons && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture titletypes && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture communitytypes && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture code:developmentStatus && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture upr:entidades && \
podman exec code_web-api_1 invenio rdm-records add-to-fixture upr:materias && \

podman exec code_web-api_1 invenio rdm-records add-to-fixture subjects && \


podman exec code_web-api_1 invenio vocabularies update --vocabulary names  --filepath /opt/invenio/var/instance/app_data/vocabs.yaml
# output
#  44104 items succeeded
# 2015 contained errors



```
