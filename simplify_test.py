import re
import sympy
from sympy.parsing.sympy_parser import parse_expr


SIGNAL = 0
NUMBER = 1

base = 'abcdefghijklmn'

def pre(expr, arr):
    s = str(expr)
    # arr.append(s)
    if len(re.findall('[+\-*/]', s)) <= 1:
        arr.append(s)
        return
    for arg in expr.args:
        pre(arg, arr)


def base_split(s):
    arr = []
    now = -1
    for i in s:
        if re.match('[0-9A-z.]', i):
            if now == NUMBER:
                arr[-1] += i
            else:
                arr.append(i)
                now = NUMBER
        else:
            arr.append(i)
            now = SIGNAL
    return arr


def get_tables(s):
    table = {}
    rev_table = {}
    num_able = {}
    arr = re.findall("[0-9.]+", s)
    index = 0
    for n, i in enumerate(arr):
        if i not in table.keys():
            key_alp = base[index]
            table[i] = key_alp
            rev_table[key_alp] = i
            num_able[key_alp] = 1
            index += 1
        else:
            num_able[table[i]] += 1
    return table, rev_table, num_able


def num_to_alpbet(s, num_alp_table, ignore_pos=None):
    iter = re.finditer("[0-9.]+",s)
    new = ''
    last = 0
    for n, i in enumerate(iter):
        start, end = i.span()
        new += s[last:start]
        if ignore_pos is not None and n in ignore_pos:
            new += s[start:end]
        else:
            new += num_alp_table[s[start:end]]
        last = end
    if last < len(s):
        new += s[last:]
    return new


def alpbet_to_num(s, table):
    iter = re.finditer("["+base+"]+", s)
    for i in iter:
        s = str.replace(s, i.group(), table[i.group()])
    return s


def pow_to_mult(s):
    if type(s) != str:
        s = str(s)
    obj = re.search('[0-9A-z.]+\*\*[0-9A-z.]+', s)
    while obj is not None:
        tmp_arr = obj.group().split('**')
        n = tmp_arr[0]
        m = tmp_arr[1]
        for i in range(int(m) - 1):
            n += '*' + tmp_arr[0]
        s = s[:obj.span()[0]] + n + s[obj.span()[1]:]
        obj = re.search('[0-9.]+\*\*[0-9.]+', s)
    return s


# 结合律
def simplify(s, ignore_pos=None):
    n_a_table, a_n_table, num_table = get_tables(s)
    s2 = num_to_alpbet(s, n_a_table, ignore_pos)
    col_arr = []
    for k, v in num_table.items():
        if v >= 2:
            col_arr.append(n_a_table[a_n_table[k]])
    if len(col_arr) > 0:
        s2 = combine(s2, col_arr)
        s2 = alpbet_to_num(str(s2), a_n_table)
        if '(' in s2:
            return s2, True
        return s2, False
    else:
        return s, False


def combine(s, col=None):
    if type(s) == str:
        s_str = s
        s = sympy.sympify(s, evaluate=False)
    else:
        s_str = str(s)
    if col is not None and len(col) > 0:
        s1 = sympy.collect(s, col)
        s1 = pow_to_mult(s1)
        s1_str = str(s1)
        s1_str = s1_str.replace(' ', '')
        if s1_str == s_str:
            s1 = sympy.combsimp(s)
            s1 = pow_to_mult(s1)
    else:
        s1 = sympy.combsimp(s)
    s1 = sympy.sympify(s1, evaluate=False)
    return s1


# 拆括号
def expand(s, ignore_pos=None):
    if type(s) != str:
        s = str(s)
    n_a_table, a_n_table, num_table = get_tables(s)
    s2 = num_to_alpbet(s, n_a_table, ignore_pos)
    s2 = sympy.expand(s2)
    s2 = alpbet_to_num(str(s2), a_n_table)
    return s2


# 交换律
def exchange(s, start_p=2):
    if type(s) == str:
        s_str = s
        s = sympy.sympify(s, evaluate=False)
    else:
        s_str = str(s)
    s_str = s_str.replace(' ', '')
    if '*' in s_str or '/' in s_str:
        ty = 1
    else:
        ty = 0
    args = list(s.args)
    if len(args) <= 2:
        return s_str, False
    for i in args:
        if len(i.args) > 2:
            return s_str, False

    s_arr = re.findall('[+\-*/]*[0-9.A-z]+', s_str)
    for i in range(len(args)-1):
        str_arg_i = str(args[i])
        for j in range(start_p, len(args), 1):
            str_arg_j = str(args[j])
            exchangeable = False
            n1 = args[i]
            n2 = args[j]
            if '/' not in str_arg_i:
                n1 = float(args[i])
            if '/' not in str_arg_j:
                n2 = float(args[j])
            if ty == 0:
                if (n1 + n2) % 10 == 0:
                    exchangeable = True
            # elif ty == 1:
            #     if args[i]%10 != 0:
            elif ty == 1:
                if args[i] % 10 == 0:
                    continue
                while n1 % 10 == 0:
                    n1 = n1/10
                while n2 % 10 == 0:
                    n2 = n2/10
                if '/' not in str_arg_i and '/' not in str_arg_j:
                    i_no0 = str_arg_i.replace('0', '')
                    j_no0 = str_arg_j.replace('0', '')
                    if len(i_no0) > 1 and len(j_no0) > 1 and args[i] != args[j]:
                        continue

                if (n1 * n2) % 10 == 0 or n1 * n2 == 1 or 1/(n1 * n2) % 10 == 0:
                    exchangeable = True
            if exchangeable:
                tmp = s_arr[i+1]
                s_arr[i+1] = s_arr[j]
                s_arr[j] = tmp
                if i > 0:
                    s_arr[i] = s_arr[i][0] + '(' + s_arr[i][1:]
                    s_arr[i+1] += ')'
                    if s_arr[i][0] == '-':
                        if s_arr[i + 1][0] == '+':
                            s_arr[i + 1] = '-'
                        elif s_arr[i + 1][0] == '-':
                            s_arr[i + 1] = '+' + s_arr[i + 1][1:]
                    elif s_arr[i][0] == '/':
                        if s_arr[i + 1][0] == '*':
                            s_arr[i + 1] = '/' + s_arr[i + 1][1:]
                        elif s_arr[i + 1][0] == '/':
                            s_arr[i + 1] = '*' + s_arr[i + 1][1:]
                return ''.join(s_arr), True
    return ''.join(s_arr), False


if __name__ == '__main__':
    s = '13*12+(7+99)*12-8*19'
    s = '13*99 +12*99+14*4+18*99 + 14*5 + 99*14'
    s = '9+5/8*4+1'
    s = '3+3+4+5+6+2'
    s = '101*101-101'
    s = '2+9-5/8*4+1'
    s = '20/4+a'
    s = '3+3*3*3+a'
    s = '4+5+6+x'
    s = '3+20/20+x'
    s = '26.78-(6.78+13.5)'
    s = '85*(720/(100-76))'
    s = '(4/9)*(1/5)/(4/5)'
    s = '(4/9+1)*(3/8+2)'
    s = '85*720/(100-76)'
    s = '8.00'
    print(sympy.sympify(s, evaluate=False))
    # s = '6/5-5/8-(13/28)/(26/21)'
    # s = '6/5-5/8'
    # s = '5*(8+1)'
    # s = '99*100'
    # s = '120*(5/6)/(4/5)'
    # s = '26.78 - (13.5 + 16.78)'
    # s = '1-(4+9.5)'
    # s = '26.78-(6.78+13.5)'
    # s = '26.78-(13.5+6.78)'
    # s = 'a-(b+c)'
    # a, b, c = sympy.symbols('a,b,c')
    # s = sympy.sympify(s, evaluate=True)
    # s = sympy.sympify(s, evaluate=False)
    # print(s)
    # print(s.args)
    # print(type(s.args[0]))
    # p
    # s = expand(s)
    # print(s)
    s, t = exchange(s, start_p=2)
    print(s, t)

    pass
