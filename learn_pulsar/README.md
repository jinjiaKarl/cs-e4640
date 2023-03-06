## Core concepts
https://streamnative.cn/blog/engineering/2021-06-03-quickly-get-started-with-apache-pulsar-zh-cn/

components:
* ZookKeeper
* BookKeeper
* Broker

### Pulsar
6650端口供client连接，8080端口暴露一些监控指标  :8080/metrics有Prometheus指标


### Pulsar Manager
Pulsar Manager is divided into front-end and back-end, the front-end service port is 9527 and the back-end service port is 7750.

## Run in a standalone mode


### start

```
mkdir ./data
docker-compose up
```


### set admin user

https://pulsar.apache.org/docs/2.11.x/administration-pulsar-manager/#set-the-administrator-account-and-password

```
CSRF_TOKEN=$(curl http://localhost:7750/pulsar-manager/csrf-token)
curl \
   -H 'X-XSRF-TOKEN: $CSRF_TOKEN' \
   -H 'Cookie: XSRF-TOKEN=$CSRF_TOKEN;' \
   -H "Content-Type: application/json" \
   -X PUT http://localhost:7750/pulsar-manager/users/superuser \
   -d '{"name": "admin", "password": "apachepulsar", "description": "test", "email": "username@test.org"}'

# go to http://localhost:9527
```


### run python test
https://alpha2phi.medium.com/apache-pulsar-development-setup-bbdc82314cf

```
pip3 install -r requirements.txt
python3 consumer.py
python3 producer.py
```



## Run in a cluster mode
https://github.com/apache/pulsar/blob/master/docker-compose/kitchen-sink/docker-compose.yml
https://pulsar.apache.org/docs/2.11.x/deploy-docker/#deploy-a-cluster-by-using-composeyml

it doesn't work, why?
```
docker compose -f docker-compose-cluster.yml up
```