def main(tp_header, setting, setting2, hs_mc=None, date=None, ider=None):
    import requests
    if date:  # 基于时间, 抓取排行榜
        if setting:
            setting['date'] = date
            get_url1 = 'https://pix.ipv4.host/ranks?page={}'.format(
                setting['ph_page'])
            get_url2 = '&date={}&mode={}&pageSize={}'.format(
                setting['date'], setting['mode'], setting['pagesize'])
            get_url = get_url1 + get_url2
        else:
            get_url1 = 'https://pix.ipv4.host/ranks?page=1'
            get_url2 = '&date=' + date + '&mode=day&pageSize=30'
        a = requests.get(get_url)
        # print('请求:' + get_url)
        return a.text
    elif ider:  # 基于id
        if setting2:
            get_url1 = 'https://pix.ipv4.host/artists/{}'.format(ider)
            get_url2 = '/illusts/illust?page={}'.format(setting2['hs_page'])
            get_url3 = '&pageSize={}&maxSanityLevel={}'.format(
                setting2['pagesize'], setting2['max'])
            get_url = get_url1 + get_url2 + get_url3
        a = requests.get(url=get_url, headers=tp_header)
        # print('id 请求:' + get_url)
        return a.text
    elif hs_mc:  # 基于名称
        if setting:
            get_url1 = 'https://pix.ipv4.host/artists?artistName='
            get_url2 = '{}&page={}&pageSize={}'.format(
                hs_mc, setting['ph_page'], setting['pagesize'])
            get_url = get_url1 + get_url2
        a = requests.get(url=get_url, headers=tp_header)
        # print('mc请求:' + get_url)
        return a.text
    else:
        print('未开放...')


if __name__ == '__main__':
    print('Please use Leader!')
else:
    print('Sender is running ^o^ ...\n')
