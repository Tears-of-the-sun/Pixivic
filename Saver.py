import requests
import os
import time
# from pybloom_live import BloomFilter


# def connection():
#     bf = BloomFilter(capacity=105000, error_rate=0.006)
#     return bf


def download(dicts, tp_header, setting2):
    try:
        for i in dicts.keys():
            for x in dicts[i]:
                try:
                    image_data = requests.get(
                        x, headers=tp_header, timeout=10).content
                except Exception:
                    try:
                        image_data = requests.get(
                            x, headers=tp_header, timeout=10).content
                    except Exception:
                        image_data = None
                if image_data:
                    hz = x.split('.')[-1]
                    image_name = i.split('-')[0] + '.' + hz
                    image_name_or = i + '.' + hz  # 图片全称
                    fixdata = image_data[20:-5:80]
                    ider = i.split('-')[-1]
                    image_name, part, is_one = image_fix(
                        image_name, ider, hz, fixdata, setting2['save_path'])
                    # 对图片路径进行修复
                    if is_one:
                        # if part > 1:
                        #     if bf.add(fixdata):
                        #         pass
                        #     else:
                        #         is_one = False
                        if is_one:  # 简单去重
                            with open(image_name, 'wb') as f:
                                f.write(image_data)
                            # pic = image_name.split()
                            print(
                                'Download: ' + image_name_or + '-p' + str(part)
                                )
                            time.sleep(0.5)
                        else:
                            print(image_name_or + '  重复--bloom')
                            # time.sleep(1)
                    else:
                        print(image_name_or + '  重复--数据筛选')
                else:
                    print(image_name_or + '-p' + str(part) + '下载失败')
    except RuntimeError:
        time.sleep(5)
        download(dicts, tp_header, setting2)


def image_fix(name, hs_id, hz, fixdata, paths):  # 修复图片各种的问题
    error_list = ['?', '*', ':', '"', '<', '>', '\\', '/', '|']
    for i in error_list:
        if i in name:
            name = name.replace(i, '')  # 特殊符号
    dictory = paths
    if os.path.isdir(dictory):
        pass
    else:
        os.mkdir(dictory)
    dictory = os.path.join(dictory, hs_id)
    if os.path.isdir(dictory):
        pass
    else:
        os.mkdir(dictory)
    dictory = os.path.join(dictory, name)
    n = 1
    is_one = True
    while os.path.isfile(dictory):
        num = 0
        with open(dictory, 'rb') as f:
            data = f.read()
            data = data[20:-5:80]
            for i in range(len(data)):
                try:
                    if fixdata[i] == data[i]:
                        num += 1
                except Exception:
                    pass
        if num >= len(data)*0.7:
            is_one = False
            return dictory, n, is_one
        else:
            n += 1
            if n >= 3:
                dictory = dictory.replace('-p' + str(n-1), '-p' + str(n))
            else:
                dictory = dictory.replace('.' + hz, '-p' + str(n) + '.' + hz)
    # 重名和目录
    return dictory, n, is_one


bf = ''

if __name__ == '__main__':
    print('Use Leader!')
else:
    print('Sender is running...')
    # bf = connection()
