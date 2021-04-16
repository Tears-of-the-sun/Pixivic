import re
import json
import Sender
import Getter
import argparse
import threading
from sys import exit
from datetime import datetime, timedelta
from time import sleep, strftime, localtime


thread_max_num = threading.Semaphore(5)

parser = argparse.ArgumentParser()
parser.add_argument(
    '-m', '--mc', help='使用画师名称的  ', required=False)
parser.add_argument(
    '-d', '--date', help='指定日期的 , 形如:2021-01-01 ', required=False)
parser.add_argument(
    '-n', '--now', help='今天的,指定任意参数  ', required=False)
parser.add_argument(
    '-l', '--list', help='指定时间范围 如:2021-01-01 2021-01-02 ',
    nargs='+', required=False)
parser.add_argument(
    '-i', '--id', help='使用画师id的  ', required=False)

dicts = {}


def thread_get(tp_header, setting2, x):
    sleep(1)
    url_data = Sender.main(
        ider=x, tp_header=tp_header, setting=None, setting2=setting2)
    if ('画师' in url_data) and ('画作' in url_data) and len(url_data) > 25:
        # 搜索画师作品成功了
        artists = json.loads(url_data)
        sleep(1)
        for t in artists['data']:
            lists = []
            for y in t['imageUrls']:
                sleep(1)
                u = y['original']
                picture_url = 'https://o.acgpic.net/img-original/img'
                u = u.split('/img')[-1]
                sleep(1)
                lists.append(picture_url + u)
            dicts[t['title'] + '--' + str(x)] = lists
        sleep(3)
    elif 'token' in url_data[0:25]:
        print('登录失效, 检查修改setting.txt')
        exit('登录失效')
    elif len(url_data) <= 25 and '成功' in url_data:
        print('该页没有数据')
    else:
        print('??????')


def main(hs_mc, date, ider):
    try:
        tp_header, setting, setting2 = Getter.fileload()
    except Exception as e:
        print(e)
        input(' >_< Woops, settings is wrong!')
        exit(1)
    hs_id_ph = []
    for s in range(1, int(setting['ph_page']) + 1):  # 遍历设置中的排行页码
        setting['ph_page'] = str(s)
        url_data = Sender.main(
            tp_header, setting, setting2, hs_mc,
            date, ider)
        if ('排行' in url_data[0:25]) and (len(url_data) > 25):
            sleep(1)
            # 使用排行抓取数据成功了
            try:
                artists = json.loads(url_data[0:25])
                for x in artists['data']:
                    hs_id_ph.append(x['artistId'])
            except Exception:
                try:
                    f = re.findall(r'"artistId":[0-9]+', url_data)
                    # 抓取排行上的画师的id
                    for i in f:
                        i = i.split(':')[-1]
                        if i:
                            hs_id_ph.append(i)
                        # 存入列表
                except Exception as e:
                    print(e)
        elif ('画师' in url_data[0:25]) and ('搜索' in url_data[0:25]):
            sleep(1)
            # 使用画师名称成功了
            try:
                artists = json.loads(url_data)
                for t in artists['data']:
                    hs_id_ph.append(t['id'])
            except Exception:
                try:
                    f = re.findall(r'"id":[0-9]+', url_data)
                    for i in f:
                        i = i.split(':')[-1]
                        if i:
                            hs_id_ph.append(i)
                except Exception as e:
                    print(e)
        elif '成功' in url_data:
            print('没有数据，也许未更新')
            break
        else:
            print('未知错误...')
            print(url_data)
            break
    if hs_id_ph:
        print('开始抓取%s图片...' % date)
        hs_id_ph = list(set(hs_id_ph))
        for x in hs_id_ph:
            sleep(1)
            for s in range(1, int(setting2['hs_page']) + 1):
                setting2['hs_page'] = str(s)
                threadss = threading.Thread(target=thread_get, args=(
                    tp_header, setting2, x,))
                threadss.start()
        while threading.Thread.isAlive(threadss):
            sleep(3)
        if dicts == {}:
            print('数据为空...')
        else:
            import Saver
            sleep(1)
            Saver.download(dicts, tp_header, setting2)


def datelist(start, end):
    date_list = []
    begin_date = datetime.strptime(start, r"%Y-%m-%d")
    end_date = datetime.strptime(end, r"%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime(r"%Y-%m-%d")
        date_list.append(date_str)
        # 日期加法days=1 months=1等等
        begin_date += timedelta(days=1)
    return date_list


if __name__ == '__main__':
    sets = parser.parse_args()
    hs_mc, date, ider, lists = sets.mc, sets.date, sets.id, sets.list
    if sets.id:  # 如果有id参数
        ider.append(sets.id)
    if sets.now:  # 如果有now参数
        now = strftime("%Y-%m-%d", localtime())
        date = now
    if hs_mc or date or lists or ider:
        if lists:  # 如果有list参数
            try:
                date_list = datelist(lists[0], lists[1])
            except Exception:
                print('日期填写有误!')
                exit(0)
            for v in date_list:
                main(hs_mc, v, ider)
        else:
            main(hs_mc, date, ider)
    else:  # 如果一个参数都没有
        print('Whoops!\tPlease use -h to get help...')
        input('\nPut any key to exit...')
else:
    print(' >_< ')
