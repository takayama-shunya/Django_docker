# Docker for Service ID

**Version**

荒川Mac：*Docker Desktop 4.3.2 (72729)* 



## Index

1. [Quick Start](#Quick_Start)
2. [Log](#Log)
3. [DB](#DB)
3. [Django](#Django)



## Quick_Start

### Download Docker

https://www.docker.com/get-started



### Only for Windows

Windows10ユーザーは最初に以下を実行のこと。

1. powershellを**管理者として**起動して以下を実行。

```powershell
wsl --install
```



2. Ubuntuをインストール
```powershell
wsl --install -d Ubuntu-20.04
wsl --set-default-version 2
```

   

3. ~~設定 > `有効化`で検索して`Windowsの機能の有効化または無効化`を確認。~~この手続不要かも。
   - ~~Hyper-V ：チェックon~~
   - ~~Linux用Windows サブシステム（表記違う可能性あり）：チェックon~~
   - ~~仮想マシンプラットフォーム：チェックon~~
   
4. Dockerを起動する。
   - 成功する場合は`For Mac & Windows`へ。
   - 起動が失敗する場合は次を実行。
   
5. BIOSの設定を変更。
   1. `再起動 -> [DELETE]key長押し`(メーカーによってキーが`F2` `F12`など異なる)で以下のような画面に入る。
   2. `CPUの設定項目` > `Intel Virtualization Technology`の項目を探して有効化する。**メーカーによって表現が違うので注意。**以下は参考。

<img src="READMEs/files/images/BIOS.jpg" alt="BIOS" style="zoom: 25%;" align="left" />





### For Mac & Windows

Mac : 最初からここからスタート。

Windows : `Only for Windows`を完了後、以下を実行。

**コマンドが使えない場合は、書いてある説明を手動で実行すること。**



1. 自分のローカルの作業用ディレクトリに`service-id-on-docker`をクローン & ディレクトリに入る。

```bash
git clone https://gitlab.com/ecbatana-tsukuba/service_id/service-id-on-docker.git
cd service-id-on-docker
```




2. PCが`M1 Mac`ではない場合、以下のコマンドを実行。(`docker-compose.yml`の5行目`platform: linux/x86_64`を削除)
```bash
sed -i.bak -e '5d' docker-compose.yml
```

   

3. 以下のコマンドで、Service IDのプロジェクトをDockerプロジェクト内にクローン。ディレクトリ名を`Service_ID`に変更。

```bash
git clone https://gitlab.com/ecbatana-tsukuba/service_id/database.git
mv database Service_ID
```

   

4. Dockerを起動後、Dockerのプロジェクトをビルド&起動。

```bash
docker-compose build
docker-compose up
```

設定完了。



## Log

Dockerで動かしているプロジェクトは、コンソールでログを表示できないので、debug_toolbarのタブを開いてログを表示する。

<img src="READMEs/files/images/debug_toolbar_3.png" alt="toolbar_1" style="zoom:33%;" align="left" />







## MySQL

### Backup

1. 以下のコマンドで`sql`ファイルを生成

```bash
cd service_id_on_docker
docker exec -it service-id-on-docker_db_1 mysqldump -u root -p"secret" django_local > ./docker/mysql/initdb.d/0010_backup.sql
```



2. **<u>`./docker/mysql/initdb.d/0010_backup.sql`の1行目(もしくは1行目からの数行)に、余計なコメントが入ってエラーを起こすので目視で確認して削除。</u>**
   (Docker Desctop for Mac 4.4.2 (73305)での現象)



### Restore

`Docker Desktop`で、利用しているvolume `service-id-on-docker_db-store`を削除(このVolumeを削除するためにコンテナ削除が必要かも)して以下を実行。

注：以下を実行すると自動的に`./docker/mysql/initdb.d/0010_backup.sql`を読み込む。

```shell
# volumeがとまってないと削除できないので停止
docker-compose down

# volume削除
docker volume rm service-id-on-docker_db-store

# volumeを初期化してDBをバックアップから再構築
docker-compose build
docker-compose exec root ./manage.py collectstatic
docker-compose up -d
```



### Delete records

#### Login

```plaintext
docker exec -it service-id-on-docker_db_1 mysql -u root -p
```



#### Delete All

```plaintext
DELETE FROM table_name;
```



#### Delete Partially

```plaintext
DELETE FROM table_name WHERE id > 5 AND del_flg = 1;
```

### 	  



## Django

### Basic usage

```shell
# collectstatic
docker-compose exec root ./manage.py collectstatic

# migrate
docker-compose exec root ./manage.py migrate

# makemigrations
docker-compose exec root ./manage.py makemigrations
```



### Makemigrations

```bash
docker-compose exec root python3 manage.py makemigrations offices 
docker-compose exec root python3 manage.py makemigrations peace_keeping
docker-compose exec root python3 manage.py makemigrations restore_order 
docker-compose exec root python3 manage.py makemigrations words 

docker-compose exec root python3 manage.py migrate
```





### Seed Backup

#### All

```bash
docker-compose exec root python3 manage.py dumpdata peace_keeping --indent 1 > peace_keeping/seed/0020_peace_keeping.json
docker-compose exec root python3 manage.py dumpdata words --indent 1 > words/seed/0020_word_full.json
docker-compose exec root python3 manage.py dumpdata offices --indent 1 > offices/seed/0020_office.json
docker-compose exec root python3 manage.py dumpdata restore_order --indent 1 > restore_order/seed/0020_restore_order.json
```



#### partial backup

```
docker-compose exec root python3 manage.py dumpdata words -e words.service_item -e words.service_name --indent 1 > words/seed/0020_word.json
docker-compose exec root python3 manage.py dumpdata words -e words.service_name --indent 1 > words/seed/0020_word.json
```



### Load seed to MySQL

```bash
docker-compose exec root python3 manage.py loaddata offices/seed/0010_office.json
docker-compose exec root python3 manage.py loaddata words/seed/0020_word_full.json
docker-compose exec root python3 manage.py loaddata peace_keeping/seed/0020_peace_keeping.json
docker-compose exec root python3 manage.py loaddata restore_order/seed/0020_restore_order.json
```


