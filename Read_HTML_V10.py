import csv
import glob
import pprint
import shutil
import zipfile
from datetime import date
from pathlib import Path

from split01 import rearch_data


# ダウンロ－ドされたHTMLを順に調べる関数。find_word1は調べる財務諸表。word3はその項目

def create_csv(title, cash_flow_list):
    """
    csvファイルの生成
    """
    path = Path(__file__).absolute().parent
    today = date.today()
    csv_path = path  / 'CASAFLOWDATA' /  f"{title}{today}.csv"

    # csv.Dictwiter 2行目以降はwriterowsメソッドでrowオブジェクトのイテラブルの全ての要素を指定する
    with csv_path.open(mode="w", encoding="utf-8_sig", newline="") as f:
        field_names = (
            "銘柄コード", "デ－タ", "単位", "項目", "前年", "当年"
        )
        writer = csv.DictWriter(f, fieldnames=field_names, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(cash_flow_list)

bath_path = Path(__file__).resolve().parent
cash_flow_list = []
sec_codes = []
csv_file_path = bath_path / 'screening' / 'csv_differ.csv'
with csv_file_path.open(mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        key = row['銘柄コード']
        sec_codes.append(key)

#sec_codes = [ '16050', '15180']
print(sec_codes)
fold_path = Path.joinpath(bath_path, 'XBRL')
if fold_path.exists():
    shutil.rmtree(fold_path)

for sec_code in sec_codes:
    if len(str(int(sec_code))) == 4:
        sec_code = str(int(sec_code)) + '0'
    folder = Path.joinpath(bath_path, sec_code)
    if folder.exists():
        items = folder.glob('*.zip')
        for item in items:
            print(item.name)

    with zipfile.ZipFile(item) as existing_zip:
        existing_zip.extractall()

    filepath = str(Path.joinpath(bath_path, 'XBRL', 'PublicDoc'))
    files = glob.glob(filepath + '/*.htm')  # htmファイルの取得
    files = sorted(files)  # ファイルを並び替えているだけ

    dow_data = item.name
    # キャッシュフロー系のデ-タを取り入れるリストを作成

    find_word1 = '連結キャッシュ・フロー計算書'
    find_words = ['営業活動によるキャッシュ・フロー', '減価償却費', '固定資産']
    find_words2 = ['支出', '収入']
    cash_flow_datas = rearch_data(files, find_word1, sec_code, dow_data, *find_words)
    if fold_path.exists():
        shutil.rmtree(fold_path)
pprint.pprint(cash_flow_list)
title = 'CASAFLOWDATA_'
create_csv(title, cash_flow_list)
print('done!')
