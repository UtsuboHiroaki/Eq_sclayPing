import csv
import shutil
from datetime import date
from pathlib import Path

from Split.Read_HTML_V10 import sec_codes


def create_csv(title, cash_flow_list):
    """
    csvファイルの生成
    """
    path = Path(__file__).absolute().parent
    today = date.today()
    csv_path = path / 'CASAFLOWDATA' / f"{title}{today}.csv"

    # csv.Dictwiter 2行目以降はwriterowsメソッドでrowオブジェクトのイテラブルの全ての要素を指定する
    with csv_path.open(mode="w", encoding="utf-8_sig", newline="") as f:
        field_names = (
            "銘柄コード", "デ－タ", "単位", "項目", "前年", "当年"
        )
        writer = csv.DictWriter(f, fieldnames=field_names, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(cash_flow_list)


def csv_open(csv_file_path):
    """
    csvファイルの読み込み
    """
    with csv_file_path.open(mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row['銘柄コード']
            sec_codes.append(key)


def del_folder(bath_path):
    """
    解凍フォルダーが存在したら削除する
    """
    fold_path = Path.joinpath(bath_path, 'XBRL')
    if fold_path.exists():
        shutil.rmtree(fold_path)
