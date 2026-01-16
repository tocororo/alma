# setup local...



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