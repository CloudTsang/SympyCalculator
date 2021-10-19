import random
import numpy as np
import json
import re
from symbol_test import special_char

SIG_ARR = ['+', '-', '*', '/']

NUM_CELL = 3 #[个位数， 不重复编号， 位置]
MAX_NUM = 4 #支持最大式子长度

def save_map(fpath='q_type_map.txt'):
    with open(fpath, 'w+') as f:
        global all_map
        f.write(json.dumps(all_map))

def save_act(fpath='action_map.txt'):
    with open(fpath, 'w+') as f:
        global act_map
        f.write(json.dumps(act_map))


def load_map(fpath='q_type_map.txt'):
    try:
        with open(fpath, 'r+') as f:
            jstr = f.read()
            ret = json.loads(jstr)
    except Exception as err:
        print(err)
        ret = {}
    return ret


all_map = load_map(r'G:\pythonproject\calc\q_type_map.txt')
act_map = load_map(r'G:\pythonproject\calc\action_map.txt')


def f1(length):
    indexes = int('1' * length)
    pattern_num = 4 ** length
    arr = []
    while len(arr) < pattern_num:
        indexes_str = str(indexes)
        tmp_a = []
        for i in indexes_str:
            tmp_i = int(i) - 1
            tmp_a.append(SIG_ARR[tmp_i])
        arr.append(tmp_a)
        for idx in range(len(indexes_str) - 1, -1, -1):
            tmp_i = int(indexes_str[idx])
            tmp_i += 1
            if tmp_i == 5:
                tmp_i = 1
                indexes_str = indexes_str[:idx] + str(tmp_i) + indexes_str[idx + 1:]
            else:
                indexes_str = indexes_str[:idx] + str(tmp_i) + indexes_str[idx + 1:]
                break
        indexes = int(indexes_str)
    return arr


def q_type_map_gen(max_lmt=5):
    arr = []
    for i in range(max_lmt):
        i2 = i+1
        arr += f1(i2)
    for i in range(len(arr)):
        tmp = ''.join(arr[i])
        if tmp in all_map.keys():
            continue
        all_map[tmp] = i


def action_map_gen(max_lmt=5):
    global act_map
    # pref = ['normal', 'combine', 'exchange', 'devide']
    pref = ['normal', 'combine']
    for i in pref:
        for a in range(1, max_lmt):
            for b in range(a+1, max_lmt):
                k = i + '_'+str(a)+'_'+str(b)
                act_map[k] = len(act_map)
    print(act_map)


def get_q_type(s):
    arr = re.findall('[+\-*/]', s)
    if len(arr) == 0 or (s[0] == '-' and len(arr)==1):
        return -1
    sigs = ''.join(arr)
    global all_map
    if sigs not in all_map.keys():
        all_map[sigs] = len(all_map)
    return all_map[sigs]


def get_q_data2(s, feature=True):
    s = str(s)
    qt = get_q_type(s)
    if(qt==-1):
        return [-1], s
    arr = re.finditer('[+\-*/]*[0-9]+', s)
    feat_arr = []
    tmp_table = {}
    for i, m in enumerate(arr):
        cont = m.group()
        if len(cont)>1:
            n = cont[1:]
        else:
            n = cont
        if '.' not in n:
            n = int(n)
        else:
            n = round(float(n), 2)

        if cont[0] == '-':
            sig_n = -n
        else:
            sig_n = n

        if not feature:
            feat_arr.append(n)
            continue

        if sig_n in tmp_table.keys():
            feat_arr.append(int(tmp_table[sig_n]))
            continue
        else:
            for k in tmp_table.keys():
                if (sig_n + k) % 10 == 0 and (sig_n + k) != 0:
                    tmp_table[sig_n] = -tmp_table[k]
                    break

        if sig_n not in tmp_table.keys():
            tmp_table[sig_n] = len(tmp_table)+1
        feat_arr.append(int(tmp_table[sig_n]))

    while len(feat_arr) < MAX_NUM:
        feat_arr.append(0)
    return np.array([qt] + feat_arr), s


def normal_gen(exchanglable=True):
    types = ['+++', '++-', '+--', '---']
    base = types[random.randint(0, len(types) - 1)]
    base = list(base)
    base = [''] + base
    max_n = 10
    for i in range(len(base)):
        n = random.randint(1, max_n-1)
        base[i] = base[i] + str(n)
    base = ''.join(base)
    return base


def combine_gen():
    types = ['*+*', '*-*', '/+/', '/-/']
    base_str = types[random.randint(0, len(types) - 1)]
    base = list(base_str)
    base.append('')
    max_n = 10
    same = random.randint(1, max_n-1)
    last = None
    tmp = []
    for i in range(0, len(base), 2):
        if last is not None:
            if last < max_n:
                n1 = max_n - last
            last = None
        else:
            n1 = random.randint(1, max_n-1)
            while n1 == 5:
                n1 = random.randint(1, max_n - 1)
            last = n1
        tmp.append(n1)
        tmp.append(same)
        if '/' not in base_str:
            random.shuffle(tmp)
        base[i] = str(tmp[0]) + base[i]
        base[i+1] = str(tmp[1]) + base[i+1]
        tmp = []
    base = ''.join(base)
    return base


def bracket_gen():
    base = normal_gen()


if __name__ == '__main__':
    eq = '4+3+6+3'
    eq = '3/2+7/2'
    eq = '4*6-6*6'
    # eq = '4+4+4'
    # a = combine_gen()
    # a = normal_gen()
    a = bracket_gen()
    # print(a)
    print(get_q_data2(a))
    # b = normal_gen()
    # print(b)
    # print(get_q_data2(b))
    # print(get_q_data(eq))
    # print(get_q_data2(eq))
    # print(normal_gen())
    # print(combine_gen())
    # _, a = get_q_data(eq)
    # _, b = get_q_data('')
    # print(a)
    # print(b)

    # action_map_gen()
    # save_act()
    # print(act_map)


    pass
