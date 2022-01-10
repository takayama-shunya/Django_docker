# Service ID



## Start Project

### Trouble shoot

#### DBを再生成したあとのmigrateの実行順序

1. settings.pyにて以下の箇所をコメントアウト

   ```python
   INSTALLED_APPS = [
       'django.contrib.admin', # here
   
       ...
       
   AUTH_USER_MODEL = 'offices.Officer' # here
   ```

2. root/urls.pyにて以下をコメントアウト

   ```python
   urlpatterns = [
       path('admin/', admin.site.urls), #here
   ```

3. offices/models.pyにて以下を変更
   変更前

   ```python
   class Officer(AbstractUser):
       ...
       def __str__(self):
           return self.username
   ```

   変更前()

   ```python
   class Officer(models.Model):
       ...
       def __str__(self):
           return self.USERNAME_FIELD
   ```

4. この状態で以下を実行

   ```bash
   python3 manage.py migrate
   python3 manage.py makemigrations words
   python3 manage.py makemigrations offices
   python3 manage.py makemigrations peace_keeping
   python3 manage.py makemigrations restore_order
   python3 manage.py sqlmigrate words 0001
   python3 manage.py sqlmigrate offices 0001
   python3 manage.py sqlmigrate peace_keeping 0001
   python3 manage.py sqlmigrate restore_order 0001
   python3 manage.py migrate
   ```

   

5. 実行語、先程の変更をもとに戻して、以下を実行

   ```bash
   python3 manage.py migrate
   python3 manage.py makemigrations offices
   python3 manage.py sqlmigrate offices 0002
   python3 manage.py migrate
   ```

   



## 用語・概念集

用語が示す内容の詳細については、

以下のリンクから最新版の`顧客説明用資料_技術詳細`を確認のこと。

[Google Drive 顧客説明用資料](https://drive.google.com/drive/u/0/folders/1GaQC7nQsyV8LZvHBndl7LPR6p9f-XsoM)



### 用語一覧

以下がよく用いられる用語。インデントは概念の包含関係を示す。

#### サービスID・サービス名

- サービスID・サービス名
  - コアサービスID・コアフォーム
    - コア項目ID・コア項目
  - カスタムフォーム・オプションサービスID
    - オプション項目ID・オプション項目
  - 地域コード
  - バージョン



#### 標準・非標準

- サービス名
  - 標準名
  - 非標準名
- サービス項目
  - 標準項目
    - コア項目
    - オプション項目
  - 非標準項目



#### ワードファミリー

- ワードファミリー・ワード親戚
  - ワード
    - 語頭
    - 接続語
    - 語尾



### システム内での表記(コーディングルール)

モデル設計時のクラス名・変数名、テンプレートと値をやり取りする際のキー名・nameプロパティ名、に利用のこと。

| 資料内での表記         | 英語表記          | システム内における略表記 | 備考                                                         |
| ---------------------- | ----------------- | ------------------------ | ------------------------------------------------------------ |
| 混乱の平定             | Restore Order     | restore_order            |                                                              |
| 秩序の維持             | Peace Keeping     | peace_keeping            |                                                              |
|                        |                   |                          |                                                              |
| サービスID             | Service ID        | serv_id                  |                                                              |
| サービス名(**名前**)   | Service Name      | serv_name                |                                                              |
| サービス項目(**項目**) | Service Item      | serv_item                | core_item、opt_item、n_std_itemの総称                        |
|                        |                   |                          |                                                              |
| コアサービスID         | Core Service ID   | core_serv_id             |                                                              |
| コアフォーム           | Core Form         | core_form                |                                                              |
| コア項目ID             | Core Item ID      | core_item_id             |                                                              |
| コア項目               | Core Item         | core_item                |                                                              |
|                        |                   |                          |                                                              |
| オプションサービスID   | Option Service ID | opt_serv_id              |                                                              |
| カスタムフォーム       | Custom Form       | custom_form              |                                                              |
| オプション項目ID       | Option Item ID    | opt_item_id              |                                                              |
| オプション項目         | Option Item       | opt_item                 |                                                              |
|                        |                   |                          |                                                              |
| 地域コード             | Area Code         | area_code                |                                                              |
| バージョン             | Version           | ver                      |                                                              |
| 標準                   | Standard          | std                      | サービス内で実際に利用されるサービス名・サービス項目は標準   |
| 非標準                 | Non-Standard      | n_std                    | 非標準は「類似しているが利用されない」の意                   |
| 非標準名               | Non-Standard Name | n_std_name               | 同上                                                         |
| 非標準項目             | Non-Standard Item | n_std_item               | 同上                                                         |
|                        |                   |                          |                                                              |
| ワードファミリー       | Word Family       | word_family              | ex. 1                                                        |
| ワード親戚             | Word Relative     | word_relative            | word_familyと近い意味合いのfamily同士をワード親戚としてパイプつなぎする。ex. 1\|2\|5 |
| ワード                 | Word              | word                     |                                                              |
| 語頭                   | Start             | name_start, item_start   |                                                              |
| 接続語                 | Joint             | joint                    |                                                              |
| 語尾                   | End               | name_end, item_end       |                                                              |
|                        |                   |                          |                                                              |
| 表現                   | Phrase            | phrase                   | DB内にて各レコードの日本語表現を保存するカラム名。旧来はnameとitemが混在。 |
| 紙                     | Paper             | paper                    | 各自治体が持っている提出された紙の束                         |
| マイナンバー           | my number         | my_num                   |                                                              |
| マイナンバーID         | my number id      | my_num_id                |                                                              |
| ナンバー               | number            | num                      |                                                              |



## アプリ構成

- peace_keeping
  - 役割：サービスのストック、入力された内容の保存
  - モデル
    - Service_Stock : 全国自治体で作成された全サービスの保管場所
    - Used_Service : 住民が利用したサービスと入力した内容の保管場所
- restore_order
  - 役割：OCRから取得してあるデータの、サービス名&項目の整理、統合、記入内容の保存。
  - モデル
    - Raw_Item : **紙から吸い出した項目**とそれに対応するサービス名・サービス項目の対応を保存。
    - Archived_Data : **紙から吸い出した記入内容**を、Raw_Itemに対応させながら保存。DBとして再利用可能な状態。
- words
  - 役割：サービス名・項目、バリデーション用の非標準名・項目の生成・保存。
  - モデル
    - Joint
    - Item_Start
    - Item_End
    - Name_Start
    - Name_End
    - Service_Name
    - Service_Item
- offices
  - 役割：中央政府役人、地方役人のユーザー登録用。
  - モデル
    - Officer
    - Large_Area
    - Small_Area
- readmes
  - 役割：URLが一覧できるなど開発しやすくする機能(開発中)
  - モデルなし。



