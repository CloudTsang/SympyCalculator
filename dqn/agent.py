import numpy as np
import torch
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple
from IPython.display import clear_output
from dqn.env import Env
from dqn.replay_buffer import ReplayBuffer
from dqn.network import Network
import torch.nn.functional as F
import torch.optim as optim
import os
import utils

MODEL_PATH = 'model.pth' # featured
# MODEL_PATH = 'model2.pth' # non-featured

class DQNAgent:
    def __init__(
            self,
            env: Env,
            memory_size: int,
            batch_size: int,
            target_update: int,
            epsilon_decay: float,
            max_epsilon: float = 1.0,
            min_epsilon: float = 0.1,
            gamma: float = 0.99,
    ):
        obs_dim = env.observation_space.shape[0]
        action_dim = env.action_space.n
        # print(obs_dim, action_dim)

        self.env = env
        self.memory = ReplayBuffer(obs_dim, action_dim, memory_size, batch_size)
        self.batch_size = batch_size
        self.epsilon = max_epsilon
        self.epsilon_decay = epsilon_decay
        self.max_epsilon = max_epsilon
        self.min_epsilon = min_epsilon
        self.target_update = target_update
        self.gamma = gamma
        # device: cpu / gpu
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        print(self.device)

        self.dqn = Network(obs_dim, action_dim).to(self.device)
        if os.path.exists(MODEL_PATH):
            print('read model')
            self.dqn.load_state_dict(torch.load(MODEL_PATH))
            self.dqn.eval()
        self.dqn_target = Network(obs_dim, action_dim).to(self.device)
        self.dqn_target.load_state_dict(self.dqn.state_dict())
        self.dqn_target.eval()

        # optimizer
        self.optimizer = optim.Adam(self.dqn.parameters())

        # transition to store in memory
        self.transition = list()
        pass

    def select_action(self, state: np.ndarray) -> np.ndarray:
        a = np.random.random()
        if self.epsilon > a or self.env.cur_step_count >= 5:
            selected_action = np.array(self.env.action_space.sample(), np.int64)
        else:
            selected_action = self.dqn(
                torch.FloatTensor(state).to(self.device)
            )
            selected_action = selected_action.argmax()
            selected_action = selected_action.detach().cpu().numpy()
            # print(selected_action)
        if not self.is_test:
            self.transition = [state, selected_action]
        return selected_action

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, np.float64, bool]:
        next_state, reward, done, _ = self.env.step(action)
        if not self.is_test:
            self.transition += [reward, next_state, done]
            # print(self.transition, '  ', self.env.cur_question)
            # print(self.transition)
            self.memory.store(*self.transition)
        return next_state, reward, done

    def train(self, num_frames: int, plotting_interval: int = 2000):
        """Train the agent."""
        self.is_test = False

        state = self.env.reset()
        update_cnt = 0
        epsilons = []
        losses = []
        scores = []
        score = 0

        for frame_idx in range(1, num_frames + 1):
            action = self.select_action(state)
            next_state, reward, done = self.step(action)
            state = next_state
            score += reward
            # if episode ends
            if done:
                state = self.env.reset()
                scores.append(score)
                score = 0

            # if training is ready
            if len(self.memory) >= self.batch_size:
                loss = self.update_model()
                losses.append(loss)
                update_cnt += 1

                # linearly decrease epsilon
                self.epsilon = max(
                    self.min_epsilon, self.epsilon - (
                            self.max_epsilon - self.min_epsilon
                    ) * self.epsilon_decay
                )
                epsilons.append(self.epsilon)

                # if hard update is needed
                if update_cnt % self.target_update == 0:
                    self._target_hard_update()

            # plotting

            if frame_idx % plotting_interval == 0:
                print(frame_idx, round(score, 1), round(loss, 3), round(self.epsilon, 1))
        self._plot(frame_idx, scores, losses, epsilons)
        self.env.close()

    def test(self, gen_q=True) -> List[np.ndarray]:
        """Test the agent."""
        self.is_test = True
        if gen_q:
            self.env.rand_q()
        state = self.env.reset()
        print(self.env.cur_question, ' -> ', state)
        done = False
        score = 0
        frames = []
        while not done:
            action = self.select_action(state)
            next_state, reward, done = self.step(action)
            state = next_state
            score += reward
            print('action:', action," reward:"+str(reward), " ques:", self.env.cur_question, " observ:", self.env.render())
            frames.append(self.env.render())
        print("score: ", score)
        self.env.close()
        return frames, score

    def update_model(self) -> torch.Tensor:
        """Update the model by gradient descent."""
        samples = self.memory.sample_batch()
        loss = self._compute_dqn_loss(samples)
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        return loss.item()

    def save(self):
        torch.save(self.dqn.state_dict(), MODEL_PATH)

    def _compute_dqn_loss(self, samples: Dict[str, np.ndarray]) -> torch.Tensor:
        """Return dqn loss."""
        device = self.device  # for shortening the following lines
        state = torch.FloatTensor(samples["obs"]).to(device)
        next_state = torch.FloatTensor(samples["next_obs"]).to(device)
        action = torch.LongTensor(samples["acts"].reshape(-1, 1)).to(device)
        # action = torch.LongTensor(samples["acts"]).to(device)
        reward = torch.FloatTensor(samples["rews"].reshape(-1, 1)).to(device)
        done = torch.FloatTensor(samples["done"].reshape(-1, 1)).to(device)

        # G_t   = r + gamma * v(s_{t+1})  if state != Terminal
        #       = r                       otherwise
        # print(action)
        curr_q_value = self.dqn(state).gather(1, action)
        next_q_value = self.dqn_target(
            next_state
        ).max(dim=1, keepdim=True)[0].detach()
        mask = 1 - done
        target = (reward + self.gamma * next_q_value * mask).to(self.device)

        # calculate dqn loss
        loss = F.smooth_l1_loss(curr_q_value, target)
        return loss

    def _target_hard_update(self):
        """Hard update: target <- local."""
        self.dqn_target.load_state_dict(self.dqn.state_dict())

    def _plot(
            self,
            frame_idx: int,
            scores: List[float],
            losses: List[float],
            epsilons: List[float],
    ):
        """Plot the training progresses."""
        clear_output(True)
        plt.figure(figsize=(20, 5))
        plt.subplot(131)
        plt.title('frame %s. score: %s' % (frame_idx, np.mean(scores[-10:])))
        plt.plot(scores)
        plt.subplot(132)
        plt.title('loss')
        plt.plot(losses)
        plt.subplot(133)
        plt.title('epsilons')
        plt.plot(epsilons)
        plt.show()
