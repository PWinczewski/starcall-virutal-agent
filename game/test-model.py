import random
import matplotlib.pyplot as plt
import numpy as np
from gameEnv import GameEnv
from dqna import DQNAgent

env = GameEnv()
state_size = env._get_state().shape[0]
action_size = (3, 2)
agent = DQNAgent(state_size, action_size)

agent.load("dump5/dqn_model_episode_95.weights.h5")

action_frequency = 3

test_episodes = 5

test_rewards = []
test_scores = []

for episode in range(test_episodes):
    state = env.reset()

    state = np.reshape(state, [1, state_size])
    total_reward = 0
    score = 0
    
    done = False
    timer=0
    while not done:
        if timer % action_frequency == 0:
          action = agent.act(state, False)

        next_state, reward, done = env.step(action)
        next_state = np.reshape(next_state, [1, state_size])
        
        state = next_state
        total_reward += reward
        score = env.score

        env.render()

        timer+=1

    test_rewards.append(total_reward)
    test_scores.append(score // 10)
    
    print(f'Episode: {episode + 1}, Score: {score // 10}, Reward: {round(total_reward)}')

env.close()

plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
plt.plot(test_rewards, label='Total Reward')
plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.title('Total Reward per Episode (Test)')
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(test_scores, label='Score')
plt.xlabel('Episode')
plt.ylabel('Score')
plt.title('Score per Episode (Test)')
plt.legend()

plt.tight_layout()
plt.show()
