# EdinetAPI説明

## 手順

1. 導入先のディレクトリを作る

2. 導入先のディレクトリに移動する

3. 以下のコマンドを実行する

   ```git clone https://github.com/UtsuboHiroaki/Eq_sclayPing.git.```

***

## 環境作成

1. 仮想環境を作る

``` shell
python -m venv venv
```

2. 仮想環境に入る

``` shell
venv\Scripts\activate
```

3. 必要なパッケージをインストール

```shell
pip install -r requirements.txt
```

## 使用方法

1. screeningフォルダにcsv_differ.csvの名称でcsvファイルを格納
   - 参考用にサンプルファイルを追加
   - 銘柄コードの項目と銘柄コ－ドの数値が最低限必要項目

2. EDINET_API_main.pyを開く

3. 参照したい財務諸表及び項目によって設定を行う
   - ここではキャッシュフロー計算書から'営業活動によるキャッシュ・フロー', '減価償却費', '固定資産'のデ－タを算出
   - 固定資産には'支出', '収入'の項目があるので追加している

4. year month day で前日から何日前の日付からEdinetの帳票を調べるか指定する
   - 前日から何年、何か月、何日前の日付のデ－タを調べるか指定する
   - 下記のように後ろ側の日付をマイナスすれば調査期間を短縮することも可能
   - あまりに長期間指定すると調べるだけで時間を要するので注意
   ---python
   date.today() + relativedelta(months=-17))
   ---

5. 設定を行ったら実行

6. 完了すれば　\CASAFLOWDATA　フォルダにCSVファイルが作成されるの






