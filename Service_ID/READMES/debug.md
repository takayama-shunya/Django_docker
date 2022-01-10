# Debug



## はじめに

プロジェクト内でデバッグを行う際には`print()`ではなく`logger.debug()` を利用する。`logger.debug()`のメリットは

1. `logger.debug()`は一箇所で設定変更すれば非表示にできるのに対して、`print()`はコード内の全てをコメントアウトする必要があり煩雑であること。
2. `logger.debug()`は他に`logger.info()` `logger.warning()` `logger.error()`があり、出力するログのレベルを変更することができる。
3. `logger.debug()`は出力先をターミナルからログファイルに切り替える(同時出力する)ことができる。

などがある。

一方`print()`は何に利用するのかというと、ユーザー用に必要と考えられるものを出力する際に利用する。



## loggerのセットアップ

### Djangoプロジェクトにて

#### `sample.py`

loggerを使いたいファイルにて以下を書く。

```python
# 各ファイルの冒頭に記載
import logging
logger = logging.getLogger(__name__)

def sample():
    test_var = 'this is variant'
    
    # 			   ↓変数名を書く
	logger.debug('[test_var] {}'.format(test_var))
```

> [test_var] this is variant



#### `settings.py`

- `IS_ON_LOG_FILE`を切り替えることでログファイルを出力するかどうか選択可能。
- 以下の設定では出力されないのでログファイルが必要な場合は`IS_ON_LOG_FILE = True`に設定のこと。

```python
IS_ON_LOG_FILE = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,  

    # 出力フォーマット
    'formatters': {
        # ログファイル用
        'file': {
            'format': '\t'.join([
                "[%(levelname)s]",
                "%(asctime)s",
                "%(module)s",
                "%(message)s",
                "process:%(process)d",
                "thread:%(thread)d",
            ])
        },
        # コンソール出力用
        'console': {
            'format': '\t'.join([
                "[%(levelname)s]",
                "%(module)s",
                "%(message)s",
            ])
        },
    },

    # 出力先設定
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django.log'),
            'formatter': 'file',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'console',
        },
    },

    'root': {
        'handlers': ['console', 'file'] if IS_ON_LOG_FILE else ['console'],
        'level': 'DEBUG',
    },
}
```



##### 上記設定での出力例

同じ内容を出力して比較しています。↓

###### コンソール

レベル名、モジュール、メッセージの順。

> [DEBUG] select_candidates_form  [inputs] ['あらき\u3000あきら', '01-1111-1111', 'A市X区', 'A市Z区']



###### ファイル

コンソールの出力内容に加えて、プロセス番号、スレッド番号が表示。

> [DEBUG] 2021-12-29 09:47:19,550    select_candidates_form [inputs] ['あらき\u3000あきら', '01-1111-1111', 'A市X区', 'A市Z区']  process:11397  thread:12976623616



##### Refference :

- [formatの詳細設定: Python official]( https://docs.python.org/ja/3/library/logging.html)
- [qiita(ここの設定だけだとうまく行かない)](https://qiita.com/sakamossan/items/a98b949738028ad39a6b)





### Djangoを利用しない場合

とりあえず出力するだけなら。

```python
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) 
sh = logging.StreamHandler()
logger.addHandler(sh)

logger.debug('This is DEBUG')
```





## `logger`の使い分け

`settings.py`で設定されているレベル以上のloggerが出力される。上記の`settings.py`の設定(`DEBUG`)だと全て出力される。

| 種類                | レベル | 用途                                                        |
| ------------------- | ------ | ----------------------------------------------------------- |
| `logger.debug()`    | 10     | 基本これをつかう。                                          |
| `logger.info()`     | 20     | 他の開発者に挙動について補足説明する、など                  |
| `logger.warning()`  | 30     | 未実装だが実装が必要な機能がある場所で警告する、など        |
| `logger.error()`    | 40     | raise Exception()と併用して処理を止めたほうが良い気がする。 |
| `logger.critical()` | 50     | システムダウンするような事象。(具体的に誰か教えて)          |



### `logger.info()` `logger.warning()`の使い所

例として、こんな使い方をすることがあります。



#### `logger.info()`

##### レコードがDBに保存されないのが正しい挙動であることを知らせる(そうすることで、ムダなデバッグをすることを防ぐ)

```python
logger.info('{} 重複しているのでセーブされません。'.format(record))
```

##### 挙動についての補足説明をする

```python
logger.info('core_item_idの順序が変わると別の新たなserv_idが生成されて、異なるレコードとして保存されます。')
```



#### `logger.warning()`

##### 実装が必要な機能があることを知らせる

```python
logger.warning('未実装；取り込む項目と記入内容に齟齬がないかバリデーションかける')
```

