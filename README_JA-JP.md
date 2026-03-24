# wanlogger

NTPで時刻補正しながらログを出力できるシンプルなPythonロガー
コンソール(カラー表示)とファイル出力に対応

## 使い方

```py
log(text,level)
```
で作成可能
`level`を書かない場合は`info`になる

例
```py
import wanlogger

logger=wanlogger.Logger()
log=logger.log

log("hello")        # [info ] [20:50:19] hello
log("warning", 1)   # [warn ] [20:50:19] warning
log("error", 2)     # [error] [20:50:19] error
```

## ログレベル
値|内容
-|-
0|info
1|warn
2|error
3|debug

文字列でも指定可能
```py
logger.log("custom", "TEST")
```

## フォーマット変更
class作成時または`logger.formatchanger`で変更可能

変数|内容
-|-
%t|時刻
%i|レベル
%e|メッセージ

デフォルトでは以下のように表示される
![default style log](normalstyle.png)

カスタムフォーマットの例
![custom style log](customstyle.png)

## ファイル出力
標準ではオフ

同名ファイルは自動で連番になる

例
```
logger = Logger(outputfile=True, file_path="logs")
```

## NTP時刻同期
NTPで取得した時間を使用する
デフォルトで30分ごとに再同期する
class作成時に`timesync`をFalseにすることでオフにできる


## その他
- timestyle
  - logに出る時間のフォーマットを変更できる
- offset
  - ローカルとNTPサーバーの間のオフセットを出力する
  - 同期は更新されない
