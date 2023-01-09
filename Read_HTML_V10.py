import csv
import glob
import pprint
import shutil
import zipfile
from datetime import date
from pathlib import Path

from bs4 import BeautifulSoup


def csv_open(csv_file_path):
    """
    csvファイルの読み込み
    """
    with csv_file_path.open(mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            key = row['銘柄コード']
            sec_codes.append(key)


def sec_code_fifth(sec_code):
    """
    sec_codeが4桁の時に5桁にする関数
    """
    if len(str(int(sec_code))) == 4:
        sec_code = str(int(sec_code)) + '0'
        return sec_code


def del_folder(bath_path):
    """
    解凍フォルダーが存在したら削除する
    """
    fold_path = Path.joinpath(bath_path, 'XBRL')
    if fold_path.exists():
        shutil.rmtree(fold_path)


def sec_code_reserch(sec_codes, bath_path, find_word1, find_words, find_words2):
    """
    銘柄コード毎に調査をする
    """
    for sec_code in sec_codes:
        sec_code = sec_code_fifth(sec_code)
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
        rearch_data(files, find_word1, sec_code, dow_data, *find_words)
        del_folder

def rearch_data(files, find_word1, sec_code, dow_data, *find_words):
    """
    作業回数を1回にしたいのでカウンタ－設定。counterが1以上ならル－プ抜ける
    ダウンロ－ドされたHTMLを順に調べる関数。find_word1は調べる財務諸表。word3はその項目
    """
    counter = 0
    for target_file in files:
        print(target_file)
        if counter > 0:
            break
        with open(target_file, encoding='utf-8') as f:
            html = f.read()

        # htmデータの取得
        soup = BeautifulSoup(html, 'html.parser')
        # ヘッダーの文字の大きさが定まらない為可変にする
        for i in range(6):
            if counter > 0:
                break
            hs = "h" + str(i)
            h5s = soup.select(hs)
            if h5s:
                for h5 in h5s:
                    if counter > 0:
                        break
                    h5_word = h5.get_text()
                    # HTMLから連結キャッシュフロー計算書計算書の文字を探し、単位を求める
                    if h5_word.find(find_word1) > 0:
                        tani_moto = soup.select('tr p')
                        data_moto = soup.select('tr')
                        data_get(tani_moto, data_moto, find_words, find_words2, sec_code, dow_data)

    return cash_flow_list

def data_get(tani_moto,data_moto, find_words, find_words2, sec_code, dow_data):
    """
    データを取得する関数
    """
    find_word2 = '円'
    for tani_gp in tani_moto:
        tani_words = tani_gp.get_text()
        if tani_words:
            if tani_words.find(find_word2) > 0:
                cash_flow_tani = tani_words
                break
    for find_word3 in find_words:
        if find_word3 in ('営業活動によるキャッシュ・フロー', '減価償却費'):
            word_counter = 1
        else:
            word_counter = 0
        data_list = []
        count = 0
        for data_gp in data_moto:
            if count > 0:
                data_list = []
                count = 0
            if word_counter > 1:
                break
            datas = data_gp.select('p')
            for data in datas:
                data_word = data.get_text()
                data_word_ex = data_word.replace("\n", "")
                if len(data_word_ex.split()) > 0:
                    if data_word_ex.find(find_word3) >= 0 or count > 0:
                        data_list.append(data_word_ex)
                        count += 1
                    if count == 3:
                        if word_counter == 0:
                            find_words2_counter = 0
                            for find_words_2 in find_words2:
                                if data_list[0].find(find_words_2) > 0:
                                    find_words2_counter += 1
                            if find_words2_counter == 0:
                                data_list = []
                                count = 0
                                break
                        data_list.append(cash_flow_tani)
                        data_dict = {
                            '銘柄コード': sec_code,
                            'デ－タ': dow_data,
                            '項目': data_list[0],
                            '前年': data_list[1],
                            '当年': data_list[2],
                            '単位': data_list[3],
                        }
                        cash_flow_list.append(data_dict)
                        data_list = []
                        counter = 1
                        if word_counter > 0:
                            word_counter += 1
                        if word_counter > 1:
                            break
    return counter

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

if __name__ == "__main__":
    find_word1 = '連結キャッシュ・フロー計算書'
    find_words = ['営業活動によるキャッシュ・フロー', '減価償却費', '固定資産']
    find_words2 = ['支出', '収入']
    bath_path = Path(__file__).resolve().parent
    cash_flow_list = []
    sec_codes = []
    csv_file_path = bath_path / 'screening' / 'csv_differ.csv'
    csv_open(csv_file_path)
    print(sec_codes)
    del_folder(bath_path)
    sec_code_reserch(sec_codes, bath_path, find_word1, find_words, find_words2)
    del_folder(bath_path)
    pprint.pprint(cash_flow_list)
    title = 'CASAFLOWDATA_'
    create_csv(title, cash_flow_list)
    print('done!')
