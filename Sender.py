def main(dirs, hs_mc=None, date=None, ider=None, gjc=None):
    import requests
    if date:  # 基于时间, 抓取排行榜
        dirs[1]['date'] = date
        get_url1 = 'https://pix.ipv4.host/ranks?page={}'.format(
            dirs[1]['ph_page'])
        get_url2 = '&date={}&mode={}&pageSize={}'.format(
            dirs[1]['date'], dirs[1]['mode'], dirs[1]['pagesize'])
        get_url = get_url1 + get_url2
    elif ider:  # 基于id
        get_url1 = 'https://pix.ipv4.host/artists/{}'.format(ider)
        get_url2 = '/illusts/illust?page={}'.format(dirs[2]['hs_page'])
        get_url3 = '&pageSize={}&maxSanityLevel={}'.format(
            dirs[2]['pagesize'], dirs[2]['max'])
        get_url = get_url1 + get_url2 + get_url3
    elif hs_mc:  # 基于名称
        get_url1 = 'https://pix.ipv4.host/artists?artistName='
        get_url2 = '{}&page={}&pageSize={}'.format(
            hs_mc, dirs[1]['ph_page'], dirs[1]['pagesize'])
        get_url = get_url1 + get_url2
    elif gjc:  # 基于关键词
        get_url1 = 'https://pix.ipv4.host/illustrations?'
        get_url2 = 'illustType={}&searchType={}'.format(
            dirs[3]['Type'], dirs[3]['searchType'])
        get_url3 = '&maxSanityLevel={}&page={}'.format(
            dirs[3]['maxSanityLevel'], dirs[3]['page']
        )
        get_url4 = '&keyword={}&pageSize={}'.format(
            gjc, dirs[3]['pageSize'])
        get_url = get_url1 + get_url2 + get_url3 + get_url4
    else:
        return None
    try:
        a = requests.get(url=get_url, headers=dirs[0], timeout=10)
    except Exception:
        try:
            a = requests.get(url=get_url, headers=dirs[0], timeout=10)
        except Exception:
            return ' '
    return a.text


if __name__ == '__main__':
    print('Please use Leader!')
else:
    print('Sender is running ^o^ ...\n')
