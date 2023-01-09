import pprint
from pathlib import Path

from Split.code_reserch import sec_code_reserch
from Split.funcs import create_csv, csv_open, del_folder

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
