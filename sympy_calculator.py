import sympy
import re
from simplify_test import simplify, exchange, expand
from sympy.core.numbers import Integer, Float

NORMAL = 0
COMBINE = 1
DIVIDE = 2
EXCHANGE = 3
BRACKET = 4


def round_or_int(n, r=2):
    if type(n) != Integer and type(n) != Float:
        return n
    n_str = str(n)
    if '.' not in n_str:
        return n
    n_arr = n_str.split('.')
    if len(n_arr) <= 1:
        return n
    n0 = int(n_arr[0])
    if n - n0 == 0:
        n = int(n)
    else:
        n = round(n, r)
        pass
    return n


class Calculator():
    def __init__(self, question):
        self.question = question.replace(' ', '')
        self.symp_question = sympy.sympify(self.question, evaluate=False)
        self.steps = [self.question]
        # self.check_expandable()

        self.focus_area = self.set_focus()
        self.args = sympy.sympify(self.get_focus(), evaluate=False).args
        self.args = list(self.args)
        self.args = [str(round_or_int(i)) for i in self.args]
        self.done = False
        self.sig_arr = re.findall('[+\-*/]+', self.get_focus())
        self.cur_method = NORMAL

    def symp(self):
        if self.done:
            return
        s0 = self.raw_join()
        s1 = None
        if self.cur_method == NORMAL:
            for i in self.args:
                if re.search('[0-9.]+[+\-*]{1}[0-9.]+', i) is not None:# \
                    s1, t = simplify(s0)
                    if t:
                        self.cur_method = COMBINE
                    break
        if self.cur_method == NORMAL and len(self.args) >= 3: #or (len(self.args) == 3 and self.args[-1] != 'x'):
            s1, t = exchange(s0)
            if t:
                self.cur_method = EXCHANGE
        if self.cur_method == NORMAL:
            a, t = self.check_expandable()
            if t:
                s1 = a[-1]
                self.steps += a[:-1]
                self.focus_area = [0, len(self.question)]
                self.cur_method = BRACKET
        if s1 is None:
            return
        s1 = s1.replace(' ', '')
        if s1 == s0:
            return
        self.args = sympy.sympify(s1, evaluate=False).args
        self.args = list(self.args)
        self.args = [str(i) for i in self.args]
        tmp_s = self.question[:self.focus_area[0]] +s1 + self.question[self.focus_area[1]:]
        self.refresh(tmp_s)

    def calc(self):
        if self.done:
            return
        calced = False
        # 处理单个arg内运算
        for i in range(len(self.args)):
            s = self.args[i]
            if re.search('^1/[0-9.]+$', s) is not None:
                continue
            obj = re.search('[(]*[0-9.]+[*]{1}[0-9.]+[)]*', s)
            if obj is not None:
                sta, end = obj.span()
                tmp_s = str(round_or_int(sympy.N(obj.group())))
                s = s[:sta] + tmp_s + s[end:]
                self.args[i] = s
                calced = True
                break
        #处理前两个arg间运算
        if not calced:
            if len(self.args)>1 :#and self.args[0] != 'x' and self.args[1] != 'x':
                sig = re.search('[*/]+', self.get_focus())
                if sig is not None:
                    tmp_s = str(round_or_int(sympy.N(self.args[0] + sig.group() + self.args[1])))
                    # tmp_s = str(sympy.N(self.args[0] + sig.group() + self.args[1]))
                else:
                    tmp_s = str(round_or_int(sympy.N(self.args[0] + '+' + self.args[1])))
                if len(self.args)>2:
                    self.args = [tmp_s] + self.args[2:]
                else:
                    self.args = [tmp_s]

        if len(self.args) == 1:
            self.focus_area[2] = False
            self.refresh(self.join())
            if len(self.args) <= 1:
                # if len(self.args) == 0:
                #     ret = str(sympy.sympify(self.get_focus(), evaluate=False))
                #     ret = ret.replace(' ','')
                #     self.steps.append(ret)
                self.done = True
        else:
            self.refresh(self.join())
        # self.cur_method = NORMAL

    def refresh(self, s):
        s = s.replace('*1/', '/')
        self.steps.append(s)
        self.question = self.steps[-1]

        self.focus_area = self.set_focus()
        symp = sympy.sympify(self.get_focus(), evaluate=False)
        self.args = symp.args

        if len(self.args) == 0:
            symp = str(symp).replace(' ','')
            a = re.findall('[0-9]+', symp)
            b = re.findall('[0-9]+', self.question)
            if len(a) != len(b):
                self.steps.append(symp)
                self.question = self.steps[-1]

        self.args = list(self.args)
        self.args = [str(round_or_int(i)) for i in self.args]
        self.sig_arr = re.findall('[+\-*/]+', self.get_focus())

    def set_focus(self):
        sta = 0
        end = len(self.question)
        obj = re.search('\([^\(\)]+\)', self.question)
        is_bracket = False
        if obj is not None:
            sta, end = obj.span()
            is_bracket = True
        return [sta, end, is_bracket]

    def get_focus(self):
        return self.question[self.focus_area[0]:self.focus_area[1]]

    def join(self):
        s = self.raw_join()
        if self.focus_area[2] is True:
            tmp_q = self.question[:self.focus_area[0]] + '+(' + s + ')+' + self.question[self.focus_area[1]:]
        else:
            tmp_q = self.question[:self.focus_area[0]] + '+' + s + '+' + self.question[self.focus_area[1]:]
        tmp_q = self.correct(tmp_q)
        return tmp_q

    def raw_join(self):
        if re.search('[^*/0-9.()]+', self.get_focus()) is None:
            s = '*'.join(self.args)
            s = s.replace('*1/', '/')
        else:
            s = '+'.join(self.args)
        s = self.correct(s)
        return s

    def correct(self, tmp_q):
        if len(tmp_q) == 0:
            return tmp_q
        if re.search('[+\-*/]+', tmp_q) is None:
            return tmp_q
        tmp_q = tmp_q.replace('+-', '-')
        tmp_q = tmp_q.replace('-+', '-')
        tmp_q = tmp_q.replace('++', '+')
        tmp_q = tmp_q.replace('*+', '*')
        tmp_q = tmp_q.replace('+*', '*')
        tmp_q = tmp_q.replace('/+', '/')
        tmp_q = tmp_q.replace('+/', '/')
        tmp_q = tmp_q.replace('(+', '(')
        tmp_q = tmp_q.replace('+)', ')')
        if tmp_q[0] == '+':
            tmp_q = tmp_q[1:]
        if tmp_q[-1] == '+':
            tmp_q = tmp_q[:-1]
        return tmp_q

    def check_expandable(self):
        tmp = self.question
        obj = re.search('\({0,1}[^\(\)]*[\(]{1}[^\(\)]+[\)]{1}[^\(\)]*\){0,1}', tmp)
        if obj is None:
            return None, False
        tmp = obj.group()
        if obj.span()[0] != 0:
            tmp = tmp[1:-1]
        s1 = expand(tmp)
        s1 = s1.replace(' ', '')
        s2, t = exchange(s1, start_p=1)
        if t:
            if obj.span()[0] != 0:
                s1 = self.question[:obj.span()[0]] + '(' + s1 + ')' + self.question[obj.span()[1]:]
            if s1 == s2:
                ret = [s1]
            else:
                if obj.span()[0] != 0:
                    s2 = self.question[:obj.span()[0]] + '(' + s2 + ')' + self.question[obj.span()[1]:]
                ret = [s1, s2]
            # self.steps.append(str(s1))
            # self.steps.append(str(s2))
            # self.question = self.steps[-1]
            return ret, True
        return None, False


if __name__ == '__main__':
    # s = '1+90.0+2'
    # s = '13*99 +12*99+14*4+18*99 + 14*5 + 99*14'
    # s = '1+(3*(2+3*3*3.2)+3)+2' #98.4
    # s = '3*(2+3*3*3.2)+3'
    # s = '1+(2+3)'

    ss = ["65+54+135+246","900-116-384","278+598","1000-399","7*96+96*93",
         "125*81","13*98","64*125","176*25-76*25",
         "101*101-101","2800/25/4","(905-185)/15/6",
         "22+29+38","74-16-15","74-19+25","6*6/9","33-8*4","(24-6)/2", '26.78-(6.78+13.5)','487+30.18+113+19.82']

    s = '65+54+135+246'
    # s = '900-116-384'
    # s = '7*96+96*93'
    # s = '176*25-76*25'
    s = '45*28+45*74-45*2'
    # s = '101*101-101'
    # s = '9+7+3'
    # s = '100*101+101-101'
    # s = '1+3+2-2'
    # s = '101*101+102-100'
    # s = '98*3+2'
    # s = '2800/25/4'
    # s = '(905-185)/15/6'
    # s = '22+29+38'
    # s = '74-16-25'
    # s = '74-19+25'
    # s = '6*6/9'
    # s = '33-8*4'
    # s = '(24-6)/2'
    # s = '26.78-(13.5+6.78)'
    # s = '(237+43)*5/14'
    # s = '487+30.18+113+19.83'
    # s = '487+30.18+113+19.82'
    # s = '(237+43)*5/14'
    # s = '99*78-78*39+40*78'
    # s = '85*(720/(100-76))'
    # s = '1001-399+99+12-405'
    # s = '47+33*3'
    # s = '876/(180/(45*2))'
    # s = '78*101+3'
    # s = '4700/25/4'

    # s = '26.78-(6.78+13.5)'
    # s = '(4/9)*(1/5)/(4/5)'
    # s = '25*24'
    # s = '3*25*4'
    # s = '25*4*6'
    # s = '6/5-5/8'

    # s = '3*(3+2)'
    # s = '(24-6)/2'
    # s = '20/4'
    # s = '4+5+6'
    # s = '20*4'
    # s = '20-4'
    # s = '20/4/5+x'
    # s = '3+(5+7)'
    # s = '2*(6*(7*5))'
    # s = '101*99'
    # s = '125*81'
    # s += '+x'
    # s = sympy.sympify(s, evaluate=False)
    # print(s.args)


    calc = Calculator(s)
    while not calc.done:
        calc.symp()
        calc.calc()

    for i in calc.steps:
        obj = re.search('[+\-*/]{1}\-[0-9.]+', i)
        while obj is not None:
            tmp_s = '(' + obj.group()[1:] +')'
            i = i[:obj.span()[0]+1] + tmp_s + i[obj.span()[1]:]
            obj = re.search('[+\-*/]{1}\-[0-9.]+', i)
        i = re.sub('[+]*x[+]*', '', i)
        print(i)












