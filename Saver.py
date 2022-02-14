import requests
import hashlib
import threading
from os import path, mkdir
from time import sleep
from pymysql import OperationalError

lock = threading.Lock()
error_list = {}
sb_n, not_f_n, qs_n, cg_n, zs_n, cf_n = 0, 0, 0, 0, 0, 0
xz_n = 0
threading.Semaphore(3)


def yield_dir_one(dirs):  # 把画师的数据或者所有的线程 全部迭代
    for i in dirs.keys():
        for q in dirs[i]:
            yield i, q


def is_one(paths, im_data, ret=None, sets=None, name=None):
    # 使用数据库或者文件读取的方式判断是否重复
    # 返回路径，同名图片数和是否重复
    if ret and sets:  # 数据库连接成功并且有参数
        dirs = sets[5]
        cur = ret.cursor()
        if sets:
            sets = sets[4]
            sqli = "select {} from {} where {} = '{}'".format(
                dirs['insert_2'], dirs['table'], dirs['insert_1'], name)
        else:
            sqli = "select hex from pictures where name = '{}'".format(name)
        try:
            cur.execute(sqli)
            res = cur.fetchall()
        except OperationalError:
            res = ()
        hex = hashlib.sha512(
            str(im_data).replace('/', '').encode()).hexdigest()
        if (hex,) in res:
            # paths = paths.replace('.', '', 1)
            # paths = paths.strip('.', ' -p' + str(len(res) + 1) + '.')
            return None, None, False
        else:
            name = "'" + name + "'"
            hex = "'" + hex + "'"
            sqli = "INSERT INTO {}({}, {}) VALUES({}, {});".format(
                dirs['table'], dirs['insert_1'], dirs['insert_2'], name, hex)
            cur.execute(sqli)
            ret.commit()
            return paths, 1, True
    else:  # 使用磁盘io处理重复图片

        fixdata = im_data[20:-5:80]
        n = 1
        while path.isfile(paths):
            num = 0
            with open(paths, 'rb') as f:
                data = f.read()
                data = data[20:-5:80]
                for i in range(len(data)):
                    try:
                        if fixdata[i] == data[i]:
                            num += 1
                    except Exception:
                        pass
            if num >= len(data)*0.7:
                return paths, n, False
            else:
                n += 1
                paths = paths.replace('.', '', 1)
            if n >= 3:
                paths = paths.replace(' -p' + str(n-1), ' -p' + str(n))
            else:
                paths = paths.replace('.', ' -p' + str(n) + '.')
            # 重名和目录
            if n != 1:
                paths = '.' + paths
        return paths, n, True


def image_fix(name, paths, gjc=None, hs_id=None):  # 创建目录，修复图片名称，返回图片路径和图片名字
    error_fh = ['?', '*', ':', '"', '<', '>', '\\', '/', '|', '\b', ' ']
    for i in error_fh:
        if i in name:
            name = name.replace(i, '')  # 特殊符号
    names = name.split('[--]')
    name1 = names[0]
    name2 = names[-1].split('.')[-1]
    name = name1 + '.' + name2
    if path.isdir(paths):
        pass
    else:
        mkdir(paths)
    if hs_id:
        dictory = path.join(paths, hs_id)
    else:
        dictory = path.join(paths, gjc)
    if path.isdir(dictory):
        pass
    else:
        mkdir(dictory)
    dictory = path.join(dictory, name)
    return dictory, name


def thread_run(key, value, head, ret, sets, gjc):  # 请求网址判断数据是否正常
    global error_list
    global sb_n, not_f_n, qs_n, cg_n, zs_n, cf_n, xz_n
    if not (key and value):
        return None
    try:  # 检测图片是否有问题, 赋值给code
        im_data = requests.get(value, headers=head, timeout=5).content
    except Exception:
        im_data = ''
    if type(im_data) != str:
        if b'404' in im_data:
            code = '404'
        elif len(im_data) <= 58:
            code = 'qs falied'
        else:
            code = 'yes'
    else:
        sleep(1)
        code = 'error'
    if code == 'yes':
        if gjc:
            hs_id = None
        else:
            hs_id = key.split('[--]')[-1].split('.')[0]
        lock.acquire()
        paths, im_name = image_fix(
            key, sets[2]['save_path'], gjc, hs_id)
        if ret:
            im_path, part, one_ = is_one(
                paths, im_data, ret, sets, im_name)
        else:
            im_path, part, one_ = is_one(
                paths, im_data)
        lock.release()
        if one_ and im_path and part:
            lock.acquire()
            with open(im_path, 'wb') as f:
                f.write(im_data)
            print('Download: ' + im_name + '  part: ' + str(part))
            xz_n += 1
            lock.release()
        else:
            cf_n += 1
            print('与  ' + im_name + '  part: ' + str(part) + ' 相同...')
    elif code == 'error':
        if key in error_list.keys():
            if value not in error_list[key]:
                error_list[key].append(value)
                sb_n += 1
        else:
            error_list[key] = [value]
            sb_n += 1
            sleep(1)
    elif code == '404':
        not_f_n += 1
    elif code == 'qs falied':
        qs_n += 1
    # 除非错误，否则视为成功
    if code != 'error':
        lock.acquire()
        if key in error_list.keys():
            if len(error_list[key]) >= 1:
                if value in error_list[key]:
                    error_list[key].remove(value)
                    sb_n -= 1
            if error_list[key] == []:
                error_list.pop(key)
        cg_n += 1
        lock.release()


def main(dirs, sets, gjc=None, ret=None, last=False):
    global zs_n
    head = {
        'referer': 'https://sharemoe.net/',
    }
    yield_items2 = yield_dir_one(dirs)  # 线程生成器
    while True:
        try:
            a, b = next(yield_items2)
            c = threading.Thread(
                    target=thread_run, args=(
                        a, b, head, ret, sets, gjc))
            c.start()
            if not last:
                zs_n += 1
            if threading.active_count() >= 15:
                c.join()
            if last:
                c.join()
        except StopIteration:
            break
    while True:
        try:
            threading.current_thread().join()
        except RuntimeError:
            break
    return error_list.items()


if __name__ == '__main__':
    print('Use Leader!')
else:
    print('Saver is running...')
