import numpy as np
import random
import sympy
from math_gen import get_q_data2, combine_gen, normal_gen, act_map
from simplify_test import simplify
from symbol_test import sym_eval
import re


class Actions():
    def __init__(self):
        # self.qtype_map = {'normal':0, 'combine':1, 'exchange':2, 'devide':3,}
        self.qtype_map = {'normal': 0, 'combine': 1}
        self.rev_act_map = {}
        self.qtype = []
        for k, v in act_map.items():
            self.rev_act_map[v] = k
            self.qtype.append(v)
        # self.qtype = np.array(self.qtype)
        # self.n = self.qtype.shape[0]
        self.qtype = np.array([0, 1])
        self.n = 2

    def sample(self):
        a = random.randint(0,len(self.qtype) - 1)
        return a


class Env():
    def __init__(self, question, is_test=True):
        self.ori_question = question
        self.is_test = is_test
        if len(self.ori_question) > 0:
            self.expr = sympy.sympify(self.ori_question, evaluate=False)
        self.cur_step_count = 0
        self.action_space = Actions()
        self.observation_space, self.ori_question = get_q_data2(self.ori_question)
        self.cur_question = self.ori_question
        self.cur_type = 0
        self.exchange_pair = []
        self.combined = False
        self.done = False

    def step(self, action):
        if self.done:
            return self.observation_space, 0, self.done, None
        if action == 0:
            tmp_s = sym_eval(self.cur_question)
            self.observation_space, self.cur_question = get_q_data2(tmp_s)
            reward = 0;
            if(self.observation_space[0] == -1):
                reward == 2
            self.done = reward == 2
        elif action == 1:
            tmps = simplify(self.cur_question)[0]
            tmps = tmps.replace("(", "").replace(")", "")
            tmps2 = self.cur_question.replace("(", "").replace(")", "")
            if(len(tmps)<len(tmps2)):
                reward = 1
                self.observation_space, self.cur_question = get_q_data2(tmps)
            else:
                reward = -0.5
        self.cur_step_count += 1
        return self.observation_space, reward, self.done, None

    def rand_q(self, forced=-1):
        f = random.randint(0, 1)
        if forced!=-1:
            f = forced
        if f == 0:
            self.observation_space, self.ori_question = get_q_data2(normal_gen())
        else:
            self.observation_space, self.ori_question= get_q_data2(combine_gen())

    def reset(self):
        self.exchange_pair = []
        self.cur_step_count = 0
        self.cur_question = self.ori_question
        self.combined = False
        self.done = False
        return self.observation_space

    def close(self):
        self.reset()
        pass

    def render(self):
        return self.observation_space


if __name__ == '__main__':
    # print(np.zeros([2], dtype=np.float32))
    env = Env(question='')
    # env.reset()
    # print(env.action_space.rev_act_map)
    # print(env.action_space.qtype)

    env.reset(forced=1)
    print(env.observation_space, env.cur_question)
    print(env.step(1))
    print(env.observation_space, env.cur_question)
    print(env.step(0))
    print(env.observation_space, env.cur_question)
    print(env.step(0))
    print(env.observation_space, env.cur_question)
    # samp_act = env.action_space.sample(env.observation_space)
    # print(samp_act)
    # print(env.step(samp_act))