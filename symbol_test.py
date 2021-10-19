import sympy
import re


NORMAL = 1
FORMULA = 2


def get_type(s):
    if re.search('[a-z]+', s) is not None:
        return FORMULA
    else:
        return NORMAL

# 替换数学符号
def special_char(s):
    s = str.replace(s, ' ', '')
    s = str.replace(s, '×', '*')
    s = str.replace(s, r'\times', '*')
    s = str.replace(s, '÷', '/')
    s = str.replace(s, r'\div', '/')
    s = pow_handle(s)
    s = sqrt_handle(s)
    return s


# 幂符号处理
def pow_handle(s):
    fs = re.findall('\^{.}', s)
    for f in fs:
        nf = '**' + f[2:-1]
        s = str.replace(s, f, nf)
    return s


# 开方符号处理
def sqrt_handle(s):
    reg = re.compile('(\\\sqrt)(\[.])*({[^{};]+})')
    fs = re.findall(reg, s)
    while len(fs) > 0:
        for f in fs:
            tmp = ''.join(f)
            sqrt_num = '2'
            if len(f[1]) > 0:
                sqrt_num = f[1][1:-1]
            tmp2 = '(('+f[2][1:-1] + ')**(1/'+sqrt_num+'))'
            s = str.replace(s, tmp, tmp2)
        fs = re.findall(reg, s)
    return s


# 在连乘中添加乘号
def add_multi(s):
    fs = re.findall('[0-9a-z]+[a-z]', s)
    for f in fs:
        obj = re.search('[a-z]', f)
        if obj is None:
            continue
        i = obj.start()
        tmp_s = f[i:]
        tmp_s = '*'.join(list(tmp_s))
        if i > 0:
            tmp_s = '*' + tmp_s
        s = re.sub(f, f[:i]+tmp_s, s)
    return s


# 移动等式两侧
def move_equal(s):
    s2 = re.split('=', s)
    if len(s2) > 1:
        s2[1] = '-('+s2[1]+')'
    return ''.join(s2)


def preprocess(s):
    # s = special_char(s)
    s = add_multi(s)
    s = move_equal(s)
    return s


def sym_eval(s):
    eq = special_char(s)
    ty = get_type(eq)
    result = ''
    if ty == NORMAL:
        result = sym_eval_normal(eq)
    elif ty == FORMULA:
        result = sym_eval_formula(eq)
    return round(result, 1)
    # return int(result)


def sym_eval_normal(s):
    eq = preprocess(s)
    eq = sympy.simplify(eq)
    answer = sympy.N(eq)
    return answer


def sym_eval_normal_step(s):
    eqs = sympy.sympify(s, evaluate=False).args
    eqs = list(eqs)
    eqs = [str(i) for i in eqs]
    arr = []
    for i in range(len(eqs)): # 乘除法处理
        eq = eqs[i]
        if re.search('[+\-*/]+', eq) is not None:
            obj = re.search('[0-9.]+[+\-*/]{1}[0-9.]+', eq)
            while obj is not None:
                sta, end = obj.span()
                tmp_eq = eq[:end]
                eq = str(round(sympy.N(tmp_eq), 2)) + eq[end:]
                eqs[i] = eq
                obj = re.search('[0-9.]+[+\-*/]{1}[0-9.]+', eq)
                tmp_s = '+'.join(eqs)
                tmp_s.replace('+-', '-')
                arr.append(tmp_s)
    while len(eqs) > 1: #加减法处理
        eq1 = eqs[0]
        eq2 = eqs[1]
        eq3 = str(round(sympy.N(eq1+'+'+eq2), 2))
        if len(eqs) > 2:
            eqs = [eq3] + eqs[2:]
        else:
            eqs = [eq3]
        tmp_s = '+'.join(eqs)
        tmp_s.replace('+-', '-')
        arr.append(tmp_s)
    return arr


def sym_eval_normal_full_step(s):
    s = s.replace(' ','')
    arr = [s]
    eqs = sympy.sympify(s, evaluate=False).args
    eqs = list(eqs)
    eqs = [str(i) for i in eqs]
    if len(eqs) > 1: # 括号处理
        for i in range(len(eqs)):
            eq = eqs[i]
            obj = re.search('\([^\(\)]+\)', eq)
            while obj is not None:
                sta, end = obj.span()
                eq0 = obj.group()
                tmp_arr = sym_eval_normal_step(eq0)
                for idx, tmp_eq in enumerate(tmp_arr):
                    if idx != len(tmp_arr)-1:
                        tmp_eq = eq[:sta] + '(' +  tmp_eq + ')'+ eq[end:]
                    else:
                        tmp_eq = eq[:sta] + tmp_eq + eq[end:]
                    eq = str(tmp_eq)
                    eqs[i] = eq
                    tmp_s = '+'.join(eqs)
                    tmp_s.replace('+-','-')
                    arr.append(tmp_s)
                obj = re.search('\(.+\)', eq)
    arr += sym_eval_normal_step(arr[-1])
    return arr


def sym_eval_formula(s):
    if r'begin{array}' in s:
        s = re.sub(r'\\left\\{\\begin{array}{.}{', '', s)
        s = re.sub(r'}\\end{array}\\right.', '', s)
        s_list = s.split(r'}\\{')
    elif r'\\' in s:
        s_list = s.split(r'\\')
    elif r';' in s:
        s_list = s.split(r';')
    # print(s_list)
    eqs = [] # 方程式序列
    xs = '' # 未知数序列
    for eq in s_list:
        eq = preprocess(eq)
        # print('math : ', eq)
        xs += re.sub('[^a-z]*','',eq)
        eqs.append(sympy.simplify(eq))

    xs = list(set(xs))
    symlist = []  # 未知数的sympy对象序列
    for i in xs:
        sy = sympy.Symbol(i)
        symlist.append(sy)

    answer = sympy.solve(eqs, symlist) # 答案 {sympy对象 : 答案}
    result = {}
    for i in range(len(symlist)):
        result[xs[i]] = answer[symlist[i]]
    return result


if __name__ == '__main__':
    sympy.init_printing()
    a,b,c,d, e, f, g, h, i, j ,k ,x,y,z = sympy.symbols("a,b,c,d, e, f, g, h, i, j ,k ,x,y,z")
    eq = "x+y+z=8;x-y-z=4;x+z=3"
    eq = r'307+180 \div(34-19)'
    # eq = "4+5+6+8"
    eq = r'1+33 \times 4-10^{2}'
    eq = r'1+4^{2}+\sqrt[3]{4 \times 4}+\sqrt{4 \times 4}'
    # eq = r'2 + 4*35 + (3 * 7 + 2*7) * 6'
    # eq = r'6+(2*7) + (3+7)*6*(4+6)'
    # eq = r'3*6*8+7+6*2'
    # eq = r'(3+7)*4+(5-2)*3'
    eq = r'2*7 + 3*7 + (3+5)*9'
    # eq = r'3-4*4+4*5'
    # eq = r'4+4+4'
    # eq = r'876/(180/(45x2))'

    # print(sym_eval_bracket(eq))
    # eq = sympy.sympify(eq,evaluate=False)
    # print(eq.args)
    print(sym_eval_normal_full_step(eq))
    # print(sym_eval_normal_step(eq))
    # print(sympy.Float(-6.78))


