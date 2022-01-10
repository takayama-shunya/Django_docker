# 新規に参画したメンバーにやってほしいこと



## READMESに含まれるMDファイル

- このファイル
- [start_project.md](start_project.md) : 新規加入エンジニアの開発環境の設定、開発サーバー情報
- [debug.md](./debug.md) : loggingの使い分けルールなど
- [frequent_commands.md](frequent_commands.md) : よく使うSQLコマンド、マイグレーションコマンド



## 最初にやること

1. [README](https://gitlab.com/ecbatana-tsukuba/service_id/database/-/tree/main)(そこに含まれるスライドを含む)と[READMES](https://gitlab.com/ecbatana-tsukuba/service_id/database/-/tree/0.0.6/READMES)内のMDファイルを通読して、プロジェクトの目的や技術的な点について理解する。不明点については最初のミーティングで確認のこと。
2. [start_project](https://gitlab.com/ecbatana-tsukuba/service_id/database/-/blob/0.0.6/READMES/start_project.md)を参照しプロジェクトをセットアップする
3. DiscordのService_IDのスレッドにて、荒川宛に自分のGMAILアドレスを送付。
4. 荒川のカレンダーの閲覧権限を得たら、初回MTの予定候補を2~3個連絡する。
5. MTで自分のタスクを確認する。タスクの内容は次項の**実現したいこと**に記載(担当範囲は全てではなく一部)。
6. 自分のタスクを[OpenProject](https://task.cafelatte.jp/projects/sabisuidpurototaipuzuo-cheng/work_packages)に追加する&進度を都度更新する。(リンク先にアクセスできない場合は松居さんに連絡)





## 実現したいこと

### タスク全体に適用される事柄

基本的なタスクの一覧は以下の通り。

ただし、荒川が見落としているタスクに対応することや、エンジニアが自分の裁量で柔軟に対応する必要のある「明示されていない事柄」があることを予め理解しておくこと。



### 1: サービスIDで適用条件を扱えるようにする

#### 実装の概略

[ http://127.0.0.1:8000/peace_keeping/create_serv/3/](http://127.0.0.1:8000/peace_keeping/create_serv/3/)(末尾の数字は任意)で新規生成しようとしているサービスID`c1c2c3--901000-1`のうち、c3が「世帯年収400万円以下」を意味する適用条件である場合(is_app_con=True)、submitした際に対象となる住民を自動的に抽出して`peace_keeping/service_stock/register_serv.html`にて一覧表示できるようにする。



#### 実装内容

1. テストデータ作成。

   1. 以下のCSVファイルを`peace_keeping/static/peace_keeping/csv/`に複製。

      1. restore_order/static/restore_order/csv/神奈川県相模原市.csv
      2. restore_order/static/restore_order/csv/神奈川県相模原市_2.csv
      3. restore_order/static/restore_order/csv/神奈川県相模原市__3.csv

   2. 複製したあとの上記CSVファイルの末尾にパラメータを追加してテストデータを作る。パラメータは、世帯年収。1~3のCSVファイルに対して値はそれぞれ`4000000`,`6000000`,`8000000`の値を追加。なお、例として`神奈川県相模原市.csv`の内容は以下の通り。

      ```
      住民異動届,
      氏名,あらき　あきら
      連絡先,01-1111-1111
      住所,A市X区
      新住所,A市Z区
      世帯年収,4000000 　//<-追加内容の例
      ```

   3. 以下のコマンドを実行してstatcファイルを利用できるようにする。

      ```python
      python3 manage.py collectstatic
      ```



2. Service_Itemモデルの改修
   1. `words/models/service_item.py`にて、クラス変数`is_app_con`を追加する。
   2. [ http://127.0.0.1:8000/words/set_is_standard/serv_item/](http://127.0.0.1:8000/words/set_is_standard/serv_item/)で標準項目を登録する際に、`is_app_con`のbool値をチェックボックスで設定できるようにする(チェックありが`is_app_con=True`)。
   3. これを実装するためにService_Itemモデルを呼び出すViewやテンプレートを適宜改修する。
      - ~~テンプレート内のJavascriptは、addボタンを押した際に入力欄を増やす機能を担っている。テンプレートの改修にはこの機能が正しく動作することを含む。~~



3. [ http://127.0.0.1:8000/peace_keeping/create_serv/3/](http://127.0.0.1:8000/peace_keeping/create_serv/3/)にて、

   1. **世帯年収**の項目(DBにすでにある)を入力すると、**適用条件**を設定するための入力欄の属性と入力欄とが表示されるようにする(未実装：Javascript)。
   2. 入力欄の属性

      1. 完全一致
      2. 部分一致
      3. 前方一致
      4. 後方一致
      5. 範囲指定：
         - より少ない
         - 以下
         - 以上
         - より多い
         - 以上・以下
         - 以上・より少ない
         - より多い・以下
         - より多い・より少ない
   3. これを実装するために上記URIを呼び出す際に利用される各種モデル、View及びテンプレートを適宜改修する。

   

4. 上記3.でsubmitした内容を`ValidateServiceStock`クラスで受け取ってバリデーション後に保存。
   1. `words/models/service_item.py`を利用してDBに保存。
   2. バリデーションの内容については、実装時に改めて確認する(プロトタイプでは本番環境と同等のバリデーションは不要であるため)。
   3. これを実装するために上記URIを呼び出す際に利用される各種モデル、View及びテンプレートを適宜改修する。



5. `peace_keeping/templates/peace_keeping/service_stock/register_serv.html`にて、適用条件に当てはまったテストデータの氏名と世帯年収を表示する。



### 2: サービスのバージョン変更履歴の実装

#### 現状の問題点

住民異動届を表すサービスIDが`c1c2c3-901000-1`であるとする(含まれるサービス項目は、届出人氏名、住所、電話番号と仮定)。

サービスIDは定期的にサービス全体のアップデートを行う事になっており、住民異動届に新たなサービス項目(マイナンバーID)を設定し、IDとしてc4を割り振ることになったとする。

上記の状況では現状、住民異動届を表すサービスIDは`c1c2c3c4-901000-1`となる(c4を追加)。この実装ではバージョンの履歴を追うことができなくなってしまう問題がある。そこで、バージョン変更履歴が残せるような実装を行う。



#### 実装の概略

すでに作成されている住民異動届(サービスID`c1c2c3-901000-1`)に新たなコア項目を加えて変更すると、サービスID`c1c2c3c4-901000-2`が発行されるようにする(バージョンを表す末尾の数字が1から2に変わっている点に注意)。

また、住民異動届の変更履歴として`c1c2c3-901000-1` `c1c2c3c4-901000-2`が一覧表示されるようにする。



#### 実装内容

1. `Service_Stock`モデルにクラス変数`ex_serv_id=models.CharField(unique=True, max_length=255, null=True, blank=True)`を追加。
2. `peace_keeping/views/update_service_stock.py`を作成し、新規作成済みのサービスのバージョンアップを行うための一連のView、テンプレートを作成する。以下は各ページの機能の説明。
   1. 最初のページで更新するサービスの選択を入力欄で行う(`Service_Stock.fuzzy_search()`を利用すると早いはず)
   2. 2番めのページで、現状の項目&追加用に1つ分の入力欄の表示。
      1. addボタンを押すと、さらに入力欄が追加される(Javascriptで実装)。
      2. 追加項目が適用条件である場合は、適用条件に関する入力も表示(この部分は[サービスIDで適用条件を扱えるようにする](https://gitlab.com/ecbatana-tsukuba/service_id/database/-/tree/0.0.6/READMES#%E5%AE%9F%E7%8F%BE%E3%81%97%E3%81%9F%E3%81%84%E3%81%93%E3%81%A8%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9id%E3%81%A7%E9%81%A9%E7%94%A8%E6%9D%A1%E4%BB%B6%E3%82%92%E6%89%B1%E3%81%88%E3%82%8B%E3%82%88%E3%81%86%E3%81%AB%E3%81%99%E3%82%8B)の実装完了後)。
   3. 2番めのページでsubmitを行った後、3番めのページで変更内容の確認。
   4. 3番めのページでsubmitされたら`Service_Stock`に各種変更内容を保存。
   5. 4番めのページで旧バージョンと新バージョンのサービスIDを表示。





