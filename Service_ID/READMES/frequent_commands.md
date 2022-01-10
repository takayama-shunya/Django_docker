# Frequent Commands



## Migration

DB再生成後のマイグレーションのエラーに対しては[Re-Start-Project](../README.md##Re-Start-Project)を参照のこと。すでにエラーが出ていたらDBをdrop&createしなおして、まっさらな状態でマイグレーションする。



## MySQL



### Initialize : Drop & Re-Create

```mysql
drop database service_id;
create database service_id;
use service_id;
```

DB再生成後のマイグレーションの手順は[Re-Start-Project](../README.md##Re-Start-Project)を参照のこと。**この手順を間違うとエラー地獄になる。**



### Backup Table 

 定義のみの場合は `-d`オプション

```
mysqldump -u root -d service_id peace_keeping > files/sqls/service_id_table.sql
```



### Backup DB

```bash
mysqldump -u root service_id > files/sqls/service_id_full.sql
```



### Restore BD

```bash
mysql -u root -D service_id < files/sqls/service_id_full.sql
```



### Delete records

#### All

```mysql
DELETE FROM table_name;
```



#### Partial

```mysql
DELETE FROM table_name WHERE id > 5 AND del_flg = 1;
```





## Seeding

- dumpdataとloaddata共に、必要に応じて通し番号は適宜変更のこと。



### dumpdata

DBのテーブルに変更を加えたあとに不具合が生じた場合のバックアップとして利用する。

```bash
python3 manage.py dumpdata peace_keeping --indent 1 > peace_keeping/seed/0006_peace_keeping.json
python3 manage.py dumpdata words --indent 1 > words/seed/0006_word_full.json
python3 manage.py dumpdata offices --indent 1 > offices/seed/0006_office.json
python3 manage.py dumpdata restore_order --indent 1 > restore_order/seed/0006_restore_order.json
```



### loaddata

DBを再生成したあとに各アプリ内の`seed`ディレクトリのseed用ファイルをDBに対してロードする際のコマンド。

```bash
python3 manage.py loaddata words/seed/0006_word_full.json
python3 manage.py loaddata offices/seed/0006_office.json
python3 manage.py loaddata peace_keeping/seed/0006_peace_keeping.json
python3 manage.py loaddata restore_order/seed/0006_restore_order.json
```



