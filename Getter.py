settings = ''


def fileload():
    sets = []
    with open('settings.txt', 'r', encoding='utf-8') as f:
        global settings
        settings = f.read().split('---\n')  # 按格式分隔数据，读取数据
    header = {}
    for g in range(0, len(settings)):
        if g == 1:
            # values = {}
            data = settings[g].replace(' ', '').split('\n')
            for i in data:
                if i:
                    key, value = i.split(':', maxsplit=1)
                    header[key] = value
            sets.append(header)
        elif g > 1:  # 其他请求数据设置
            valuess = locals()
            values = {}
            data2 = settings[g].replace('\n', ' ').split(' ')
            for x in range(len(data2)):
                if data2[x] == '=':
                    values[data2[x-1]] = data2[x+1]  # = 前后 赋与字典键值
            valuess[g] = values
            sets.append(values)
    return sets


if __name__ == '__main__':
    print('Please use Leader!')
else:
    print('Getter is running ^o^ ...\n')
