import json
import Getter
import Sender
import Saver
import pymysql
import argparse
import threading
import os
from sys import exit
from datetime import datetime, timedelta
from time import sleep, strftime, localtime, time

timeout_n, cf_n, is_None, zs_n, = 0, 0, 0, 0
cf_dir_n = 0
hs_id_ph = []
search_dir = {}
error_dir = {}
lock = threading.Lock()
threading.Semaphore(3)
parser = argparse.ArgumentParser()

parser.add_argument(
    '-m', '--mc', help='使用画师名称的  ', required=False)
parser.add_argument(
    '-d', '--date', help='指定日期的 , 形如:2021-01-01 ', required=False)
parser.add_argument(
    '-t', '--today', help='今天的,任意参数  ', required=False)
parser.add_argument(
    '-l', '--list', help='指定时间范围 如:2021-01-01 2021-01-02 ',
    nargs='+', required=False)
parser.add_argument(
    '-i', '--id', help='使用画师id的  ', required=False)
parser.add_argument(
    '-g', '--gjc', help='关键词搜索  ', required=False)


def data_really(data, set_all):  # 处理各种返回的数据问题并返回作品字典和画师id
    global cf_dir_n
    if (data == ' ') or (data is None):
        global timeout_n
        timeout_n += 1
        return None
    elif 'token' in data[0:25]:
        print('登录失效, 检查修改setting.txt')
        exit('登录失效')
    if len(data) <= 24 and ('成功' in data):
        global is_None
        is_None += 1
        return None
    search_dir = {}
    search_dir2 = {}
    hs_id_ph = []
    hs_id_ph2 = []
    datas = json.loads(data)
    if ('搜索结果获取' in data[0:25]):  # 关键词搜索成功
        for t in datas['data']:
            try:
                g = t['title'] + '[--]' + str(t['artistId'])  # 名称
                for y in t['imageUrls']:
                    w = y['original'].split('/img')[-1]  # 网址
                    g += '.' + w.split('.')[-1]
                    w = 'https://o.acgpic.net/img-original/img' + w
                    if search_dir.get(g, '1') == '1':
                        if g not in search_dir.keys():
                            search_dir[g] = []
                    if w not in search_dir.values():
                        search_dir[g].append(w)
            except Exception:
                pass
        if set_all[2]['dir_have_pass'] == '0':
            for i in search_dir.keys():
                if not os.path.isdir(
                        os.path.join(set_all[2]['save_path'], str(i))):
                    search_dir2[i] = search_dir[i]
            cf_dir_n += len(search_dir.keys()) - len(search_dir2.keys())
            return search_dir2
        else:
            return search_dir
    elif (('画师' in data[0:25]) and ('画作' in data[0:25])):
        for t in datas['data']:
            try:
                for x in t['imageUrls']:
                    g = t['title'] + '[--]' + str(t['artistId'])  # 名称
                    w = x['original'].split('/img')[-1]  # 网址
                    g += '.' + w.split('.')[-1]
                    w = 'https://o.acgpic.net/img-original/img' + w
                    if search_dir.get(g, '1') == '1':
                        if g not in search_dir.keys():
                            search_dir[g] = [w]
                    elif w not in search_dir.values():
                        search_dir[g].append(w)
            except Exception:
                pass
        if set_all[2]['dir_have_pass'] == '0':
            for i in search_dir.keys():
                if not os.path.isdir(
                        os.path.join(set_all[2]['save_path'], str(i))):
                    search_dir2[i] = search_dir[i]
            cf_dir_n += len(search_dir.keys()) - len(search_dir2.keys())
            return search_dir2
        else:
            return search_dir
    elif('排行' in data[0:25]):  # 使用画师id成功了
        for t in datas['data']:
            try:
                hs_id_ph.append(t['artistId'])
            except Exception:
                pass  # 广告??
        hs_id_ph = list(set(hs_id_ph))
        if set_all[2]['dir_have_pass'] == '0':
            for i in hs_id_ph:
                paths = os.path.join(set_all[2]['save_path'], str(i))
                if not os.path.isdir(paths):
                    hs_id_ph2.append(i)
            cf_dir_n += len(hs_id_ph) - len(hs_id_ph2)
            return hs_id_ph2
        else:
            return hs_id_ph
    elif ('画师' in data[0:25]) and ('搜索' in data[0:25]):  # 使用画师名称成功了
        for t in datas['data']:
            try:
                hs_id_ph.append(t['id'])
            except Exception:
                pass  # 广告??
        hs_id_ph = list(set(hs_id_ph))
        if set_all[2]['dir_have_pass'] == '0':
            for i in hs_id_ph:
                paths = os.path.join(set_all[2]['save_path'], str(i))
                if not os.path.isdir(paths):
                    hs_id_ph2.append(i)
            cf_dir_n += len(hs_id_ph) - len(hs_id_ph2)
            return hs_id_ph2
        else:
            return hs_id_ph


def d_s(sets, hs_mc, date, ider):  # 按日期遍历排行榜，返回作品字典和id
    for x in date:
        for s in range(1, int(sets[1]['ph_page']) + 1):  # 遍历设置中的排行页码
            sets[1]['ph_page'] = str(s)
            url_data = Sender.main(sets, hs_mc, x, ider, None)
            hs_id_ph = data_really(url_data, sets)
            yield hs_id_ph


def connect(sets):  # 传入数据库参数，返回连接对象
    try:
        if sets[4]:
            host, user, password, port, database = sets[4].values()
            if password == "''":
                password = None
            ret = pymysql.connect(
                host=host, user=user, passwd=password,
                port=int(port), db=database)
        else:
            ret = pymysql.connect(host='127.0.0.1', user='root', db='pixivic')
    except Exception as e:
        print(e)
        ret = None
    if ret and sets[5]:
        cur = ret.cursor()
        dirs = sets[5]
        sqli = "INSERT INTO {}({}, {}) VALUES({}, {});".format(
            dirs['table'], dirs['insert_1'], dirs['insert_2'], '1', '1')
        try:
            cur.execute(sqli)
            ret.commit()
            err = False
        except Exception as e:
            print(e)
            err = True
        if err:
            ret = None
            print('数据库参数设置不对...')
        else:
            sqli = "DELETE FROM {} WhERE {}='1';".format(
                dirs['table'], dirs['insert_1'])
            cur.execute(sqli)
            ret.commit()
    return ret


def main(ider=None, gjc=None, date=None, hs_mc=None):
    error_dir = {}
    print('读取设置的参数...')
    try:
        set_all = Getter.fileload()
    except Exception as e:
        print(e)
        input(' >_< Woops, settings is wrong!')
        exit(1)
    print('读取完成...')
    b = input('Use mysql?(y/n):')
    if b == 'y':
        if set_all[4] != {} and set_all[5] != {}:
            print('连接数据库中...')
            ret = connect(set_all)
            if not ret:
                print('连接数据库失败,调整检查设置...')
                a = input('键入yes退出，否则将使用磁盘检测重复图片...')
                if a == 'yes':
                    exit('用户取消...')
            else:
                print('连接数据库成功...')
    else:
        ret = None
    start = time()
    if ider:  # 基于画师id
        url_data = Sender.main(set_all, ider=ider)
        dirs = data_really(url_data, set_all)
        arry = Saver.main(dirs, set_all, ret=ret)
        zips(arry, set_all)
    elif gjc:  # 基于关键词
        for x in range(1, int(set_all[3]['page']) + 1):
            set_all[3]['page'] = str(x)
            url_data = Sender.main(set_all, gjc=gjc)
            dirs = data_really(url_data, set_all)
            arry = Saver.main(dirs, set_all, gjc=gjc, ret=ret)
            zips(arry, set_all)
    else:  # 基于时间和画师搜索
        if type(date) == list:
            a = d_s(set_all, hs_mc, date, ider)
        else:
            a = d_s(set_all, hs_mc, [date], ider)
        while True:
            try:
                hs_id_ph = next(a)
                if hs_id_ph:
                    for t in hs_id_ph:
                        for r in range(1, int(set_all[2]['hs_page']) + 1):
                            set_all[2]['hs_page'] = str(r)
                            url_data = Sender.main(set_all, ider=t)
                            dir = data_really(url_data, set_all)
                            if dir:
                                if hs_mc:
                                    hs_mc += ' - search resault'
                                    arry = Saver.main(
                                        dir, set_all, gjc=hs_mc, ret=ret)
                                else:
                                    arry = Saver.main(dir, set_all, ret=ret)
                                zips(arry, set_all)
                            else:
                                if r == 1:
                                    print(str(t) + ' 没有画作...')
                                else:
                                    pass
                else:
                    pass
            except StopIteration:
                break
    print('集中处理剩下的失败的请求...')
    sleep(2)
    n = 0
    while n <= 2:
        if n == 0:
            arry = Saver.main(error_dir, set_all, ret=ret, last=True)
        else:
            zips(arry, set_all, cou=0, ret=None)
            arry = Saver.main(error_dir, set_all, ret=ret, last=True)
        n += 1
        if len(arry) == 0:
            break
        print('第{}次，共3次...'.format(n))
        sleep(2)
    print('全部图片执行完成...')
    if set_all[2]['dir_have_pass'] == '0':
        global cf_dir_n
        print('重复路径: {}'.format(cf_dir_n))
    else:
        print('未开启目录筛选...')
    print('图片总抓取次数: {} 图片响应数: {}'.format(Saver.zs_n, Saver.cg_n))
    print('重复图片数: {} 图片丢失数: {}'.format(Saver.cf_n, Saver.not_f_n))
    print('失败图片数: {} 没有权限: {}'.format(Saver.sb_n, Saver.qs_n))
    end = time()
    print('Running time: %s Seconds' % (end-start))


def zips(arry, set_all, cou=0, ret=None):  # 失败的请求写入列表，过多重试
    global error_dir
    error_dir = {}
    if len(arry) != 0:
        for i, o in arry:
            for r in o:
                if i not in error_dir.keys():
                    error_dir[i] = [r]
                else:
                    error_dir[i].append(r)
    if len(error_dir.keys()) >= 10 and cou <= 2:
        cou += 1
        print('失败次数过多...重新下载...第{}次, 共3次'.format(cou))
        arry = Saver.main(error_dir, set_all, ret=ret, last=True)
        zips(arry, set_all, cou, ret=ret)


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
    # sets.date = '2021-05-07'
    # sets.mc = 'Snow is'
    # sets.list = ['2021-01-05', '2021-01-31']
    if sets.mc:
        main(hs_mc=sets.mc)
    elif sets.date:
        main(date=sets.date)
    elif sets.id:
        main(ider=sets.id)
    elif sets.gjc:
        main(gjc=sets.gjc)
    elif sets.list:
        try:
            date = datelist(sets.list[0], sets.list[1])
        except Exception:
            print('日期填写有误!')
            exit('参数错误...')
        main(date=date)
    elif sets.today:  # 如果有now参数
        now = strftime("%Y-%m-%d", localtime())
        main(date=now)
    else:  # 如果一个参数都没有
        print('Whoops!\tPlease use -h to get help...')
        input('\nPut any key to exit...')
else:
    print(' >_< ')
