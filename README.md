# Docker

Refference

https://note.com/digiangler777/n/n5af9bf35b0c0



## Setup Files

### Directory

```
django-app
├── docker-compose.yml
├── mysql
│   ├── Dockerfile
│   └── my.cnf
└── python
    ├── Dockerfile
    └── requirements.txt
```



### yml

#### `docker-compose.yml`

- M1 Macの場合は`db:`内に `platform: linux/x86_64`を追記。
- Intel Mac, Windowsの場合は `platform: linux/x86_64`を削除。

```yaml
version: "3.8"

services:
  db:
    platform: linux/x86_64 # M1チップ対応のため追記
    build: ./docker/mysql
    command: --default-authentication-plugin=mysql_native_password
    volumes:
      - db-store:/var/lib/mysql

  app:
    build: ./docker/python
    command: uwsgi --socket :8001 --module app.wsgi --py-autoreload 1 --logto /tmp/tmp.log
    volumes:
      - ./src:/workspace
    expose:
      - "8001"
    depends_on:
      - db

volumes:
  db-store:
```



### Python

#### `python/Dockerfile`

```dockerfile
FROM python:3.8.3

ENV PYTHONUNBUFFERED 1
RUN mkdir /workspace
WORKDIR /workspace
ADD requirements.txt /workspace/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . /workspace/
```



#### `python/requirements.txt`

```
Django==3.2.7
uwsgi==2.0.19
mysqlclient
autopep8
```



### MySQL

#### `mysql/Dockerfile`

```dockerfile
FROM mysql:8.0

ENV MYSQL_DATABASE=django_local \
  MYSQL_USER=django_user \
  MYSQL_PASSWORD=secret \
  MYSQL_ROOT_PASSWORD=secret \
  TZ=Asia/Tokyo

COPY ./my.cnf /etc/mysql/conf.d/my.cnf
RUN chmod 644 /etc/mysql/conf.d/my.cnf
```



#### `mysql/my.cnf`

```
[mysqld]
default-authentication-plugin = mysql_native_password
character_set_server = utf8mb4
collation_server = utf8mb4_0900_ai_ci


# timezone
default-time-zone = SYSTEM
log_timestamps = SYSTEM

# Error Log
log-error = mysql-error.log

# Slow Query Log
slow_query_log = 1
slow_query_log_file = mysql-slow.log
long_query_time = 1.0
log_queries_not_using_indexes = 0

# General Log
general_log = 1
general_log_file = mysql-general.log

[mysql]
default-character-set = utf8mb4

[client]
default-character-set = utf8mb4
```



### Nginx

不要かと思って設定してなかったら動かなかった。Nginxの設定は必要です。

`nginx/uwsgi_params`

```
uwsgi_param  QUERY_STRING       $query_string;
uwsgi_param  REQUEST_METHOD     $request_method;
uwsgi_param  CONTENT_TYPE       $content_type;
uwsgi_param  CONTENT_LENGTH     $content_length;

uwsgi_param  REQUEST_URI        $request_uri;
uwsgi_param  PATH_INFO          $document_uri;
uwsgi_param  DOCUMENT_ROOT      $document_root;
uwsgi_param  SERVER_PROTOCOL    $server_protocol;
uwsgi_param  REQUEST_SCHEME     $scheme;
uwsgi_param  HTTPS              $https if_not_empty;

uwsgi_param  REMOTE_ADDR        $remote_addr;
uwsgi_param  REMOTE_PORT        $remote_port;
uwsgi_param  SERVER_PORT        $server_port;
uwsgi_param  SERVER_NAME        $server_name;
```



`nginx/default.conf `

```
upstream django {
  ip_hash;
  server app:8001;
}

server {
  listen      8000;
  server_name 127.0.0.1;
  charset     utf-8;

  location / {
    uwsgi_pass  django;
    include     /etc/nginx/uwsgi_params;
  }
}

server_tokens off;
```





## Boot

### Build

設定後最初の操作。

```bash
docker-compose build
```



### Boot Container

```bash
docker-compose up -d
```



### Access

http://localhost:8000

プロジェクトがない場合は作成後にアクセス。



### Create Django Project

ゼロからプロジェクトをDocker内に作る場合。

```bash
docker-compose exec app django-admin.py startproject app .
```



#### Restart Docker

プロジェクト作成後、コンテナをRestart。

```bash
docker-compose restart
```





### 

## Django

`settings.py`

```python
DATABASES = {
  'default': {
  'ENGINE': 'django.db.backends.mysql',
  'NAME': 'django_local',
  'USER': 'django_user',
  'PASSWORD': 'secret',
  'HOST': 'db',
  'POST': 3306
  }
}
```





`migrate`

```bash
docker-compose exec app ./manage.py migrate
```

