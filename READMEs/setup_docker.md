# Setup Docker for Django project



## Setup

### Directory

```
django-app
├── docker-compose.yml
├── mysql
│   ├── initdb.d
│   |   └── init.sql
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
    platform: linux/x86_64 #1 M1チップMac対応のため追記
    build: ./docker/mysql
    command: --default-authentication-plugin=mysql_native_password
    volumes:
      - db-store:/var/lib/mysql
      #2 MySQLにDBを生成してテーブル・レコードをリストア
      - ./docker/mysql/initdb.d/:/docker-entrypoint-initdb.d

  web:
    image: nginx:1.21.3-alpine
    ports:
      - 8000:8000
    volumes:
      - ./Service_ID:/workspace
      - ./docker/nginx/default.conf:/etc/nginx/conf.d/default.conf
      - ./docker/nginx/uwsgi_params:/etc/nginx/uwsgi_params
      - ./Service_ID/static:/static
    working_dir: /workspace
    depends_on:
      - root

  root:
    build: ./docker/python
    command: uwsgi --socket :8001 --module root.wsgi --py-autoreload 1 --logto /tmp/tmp.log
    volumes:
      - ./Service_ID:/workspace
    expose:
      - "8001"
    depends_on:
      - db

volumes:
  db-store:
```

`#1` : M1チップMac以外では削除

`#2` : `./docker/mysql/initdb.d/`内の`sql`アルファベット順に実行後、 `sh`ファイルをアルファベット順に実行。



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
asgiref==3.4.1
backports.zoneinfo==0.2.1
defusedxml==0.7.1
diff-match-patch==20200713
Django==4.0.1
django-boost==1.7.2
django-debug-toolbar==3.2.4
django-import-export==2.7.1
django-seed==0.3.1
et-xmlfile==1.1.0
Faker==11.3.0
import-export==0.2.67.dev6
MarkupPy==1.14
mysqlclient==2.1.0
odfpy==1.4.1
openpyxl==3.0.9
python-dateutil==2.8.2
PyYAML==6.0
six==1.16.0
sqlparse==0.4.2
tablib==3.1.0
text-unidecode==1.3
toposort==1.7
ua-parser==0.10.0
user-agents==2.2.0
uwsgi==2.0.20
xlrd==2.0.1
xlwt==1.3.0
```



### MySQL

#### `mysql/initdb.d/init.sql`

ここで`create`と`use`をしていなかったので`docker-entrypoint-initdb.d`をしてもDBのセットアップが完了できなかった。

```sql
/* add create database and use service_id  */
CREATE DATABASE IF NOT EXISTS `service_id`;
use `service_id`;

/* existing query by sqldump below */
DROP TABLE IF EXISTS `auth_group`;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```





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

- `server root:8001`の`root`の部分は`docker-compose.yml`内のDjangoプロジェクトのを表す表現と揃える。
- `static`を参照するための`alias`の設定を追加(これがないとCSS, JSが利かない)。[Refference](https://rurukblog.com/post/dockercompose-nginx-django-mysql/)

```
upstream django {
  ip_hash;
  server root:8001;
}

server {
  listen      8000;
  server_name 127.0.0.1;
  charset     utf-8;

  // for static files setting
  location /static {
	alias /static;
  }
  
  location / {
    uwsgi_pass  django;
    include     /etc/nginx/uwsgi_params;
  }
}

server_tokens off;
```





### Django

`settings.py`

- `docker-entrypoint-initdb.d`でDB`sevice_id`が生成されているのでこの設定でいける。

```python
DATABASES = {
  'default': {
  'ENGINE': 'django.db.backends.mysql',
  'NAME': 'service_id',
  'USER': 'root',
  'PASSWORD': 'secret',
  'HOST': 'db',
  'POST': 3306
  }
}
```





## Boot

### Build

設定後最初の操作。

```bash
docker-compose build
```



#### Trouble shoot

以下のエラーの際にのみ実行。

> ERROR: Service 'app' failed to build : Build failed

```bash
docker-compose run web bundle update
```





### Boot Container

`-d`でバックグラウンドで実行。

```bash
docker-compose up -d
```



### Access

http://localhost:8000/admin

プロジェクトがない場合は作成後に上記にアクセス。



### Create Django Project

- ゼロからプロジェクトをDocker内に作る場合。
- `root`は`docker-compose.yml`内でDjangoプロジェクトの定義に用いられている部分に由来。

```bash
docker-compose exec root django-admin.py startproject app .
```



#### Restart Docker

プロジェクト作成後、コンテナをRestart。

```bash
docker-compose restart
```





## Commands

### Django

`migrate`

```bash
docker-compose exec root ./manage.py migrate
```



`collectstatic`

```bash
docker-compose exec root ./manage.py collectstatic
```





### MySQL

#### コンテナIDを確認

以下を実行して、`IMAGE`の項目の末尾に`_db`がついているものの`CONTAINER ID`を調べる。

```
docker ps
```

> CONTAINER ID   IMAGE                    COMMAND                  CREATED       STATUS       PORTS                            NAMES
> 55c685e2015c   django_mysql_nginx_db    "docker-entrypoint.s…"   2 hours ago   Up 2 hours   3306/tcp, 33060/tcp              django_mysql_nginx_db_1

この場合、`55c685e2015c`。以降のコマンドは`docker ps`で得られたMySQLのコンテナIDを当てはめて実行。



#### Start

```bash
docker exec -it __container_id__ mysql.server start
```



#### Login

```bash
docker exec -it __container_id__ mysql -u root -p
```

pswdはsettings.pyにある値(`secret`)。



#### Backup

```bash
docker exec __container_id__ mysqldump -u root -p'secret' service_id > files/sqls/service_id_full.sql
```



#### Restore

```bash
docker exec __container_id__ mysql -u root -p'secret' service_id < files/sqls/service_id_full.sql
```





## Refference

https://note.com/digiangler777/n/n5af9bf35b0c0

