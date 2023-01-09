import glob
import zipfile
from pathlib import Path

from Split.get_data import rearch_data
from Split.code_fifth import sec_code_fifth
from Split.funcs import del_folder


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
