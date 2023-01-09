import csv
from datetime import date
from pathlib import Path


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
