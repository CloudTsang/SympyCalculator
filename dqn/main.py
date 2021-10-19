import numpy as np
from dqn.agent import DQNAgent
from dqn.env import Env


if __name__ == '__main__':
    num_frames = 100000
    memory_size = 1000
    batch_size = 32
    target_update = 100
    epsilon_decay = 1 / 20000

    env = Env('2*3+5*3', is_test=True)
    agent = DQNAgent(env, memory_size, batch_size, target_update, epsilon_decay)
    agent.train(num_frames)
    # agent.save()

    # env = Env('2*3+5*3', is_test=False)
    # agent = DQNAgent(env, memory_size, batch_size, target_update, epsilon_decay, max_epsilon=0)
    # agent.test(gen_q=False)