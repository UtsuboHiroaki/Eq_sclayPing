def sec_code_fifth(sec_code):
    """
    sec_codeが4桁の時に5桁にする関数
    """
    if len(str(int(sec_code))) == 4:
        sec_code = str(int(sec_code)) + '0'
        return sec_code
