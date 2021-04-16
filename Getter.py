settings = ''


def fileload():
    with open('settings.txt', 'r', encoding='utf-8') as f:
        global settings
        settings = f.read().split('---\n')  # 按格式分隔数据，读取数据
    header = {}
    setting_dir = {}
    setting_dir2 = {}
    for g in range(0, len(settings)):
        if g == 1:
            data = settings[g].replace(' ', '')
            data = data.split('\n')
            for i in data:
                if i:
                    key, value = i.split(':', maxsplit=1)
                    header[key] = value
        elif g == 2:  # 其他请求数据设置
            data2 = settings[g].replace('\n', ' ')
            data2 = data2.split(' ')
            for x in range(len(data2)):
                if data2[x] == '=':
                    setting_dir[data2[x-1]] = data2[x+1]
        elif g == 3:  # 其他请求数据设置
            data2 = settings[g].replace('\n', ' ')
            data2 = data2.split(' ')
            for x in range(len(data2)):
                if data2[x] == '=':
                    setting_dir2[data2[x-1]] = data2[x+1]
    return header, setting_dir, setting_dir2


def passwd():
    passdict = {}
    with open('settings.txt', 'r', encoding='utf-8') as f:
        settings = f.read().split('---\n')[-1]
        settings = settings.split('\n')
        for x in settings:
            x = x.split(' ')
            passdict[x[0]] = x[-1]
    return passdict


if __name__ == '__main__':
    print('Please use Leader!')
    # main()
else:
    print('Getter is running ^o^ ...\n')
