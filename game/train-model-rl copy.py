import matplotlib.pyplot as plt
from gameEnv import GameEnv 
from dqna import DQNAgent
import numpy as np
import multiprocessing as mp

import datetime
import time

def run_episodes(env, agent, episodes, batch_size, action_frame_lock, model_backup_frequency, model_update_frequency, render, rewards, scores):
    for episode in range(episodes):
        state = env.reset()
        state = np.reshape(state, [1, state_size])
        total_reward = 0
        score = 0

        for t in range(5000):
            if t % action_frame_lock == 0:
                action = agent.act(state, True)

            next_state, reward, done = env.step(action)
            next_state = np.reshape(next_state, [1, state_size])

            agent.remember(state, action, reward, next_state, done)

            state = next_state
            total_reward += reward

            score = env.score

            if done:
                break
            if render:
                env.render()

        rewards.append(total_reward)
        scores.append(score // 10)

        if len(agent.memory) > batch_size:
            agent.replay(batch_size)

        print('Episode:{} Score:{} Reward:{}'.format(episode+1, score//10, round(total_reward)))

        if total_reward > best_reward:
            best_reward = total_reward
            agent.save("dqn_best_model_reward.weights.h5")

        if score > best_score:
            best_score = score
            agent.save("dqn_best_model_score.weights.h5")

        if episode % model_update_frequency == 0:
            agent.update_target_model()

        if episode % model_backup_frequency == 0:
            agent.save(f"dump/dqn_model_v3_episode_{episode}.weights.h5")


env = GameEnv()
state_size = env._get_state().shape[0]
action_size = (3,2)
agent = DQNAgent(state_size, action_size)
# agent.load("dqn_model_promising_v2.weights.h5")
episodes = 100
batch_size = 32

action_frame_lock = 4
model_backup_frequency = 10
model_update_frequency = 10
render=True

rewards = []
scores = []

running=True
stop_time = datetime.time(23, 50, 0)
current_time = datetime.datetime.now().time()

best_score = -float('inf')
best_reward = -float('inf')

if __name__ == '__main__':
    num_processes = 4  # Adjust the number of processes based on your system and performance needs
    pool = mp.Pool(num_processes)

    envs = [GameEnv() for _ in range(num_processes)]
    agents = [DQNAgent(state_size, action_size) for _ in range(num_processes)]

    results = [pool.apply_async(run_episodes, args=(envs[i], agents[i], episodes, batch_size, action_frame_lock, model_backup_frequency, model_update_frequency, render, rewards, scores)) for i in range(num_processes)]

    for result in results:
        result.get()  # Wait for each process to finish

    pool.close()
    pool.join()

env.close()

plt.figure(figsize=(12, 5))

# Plot total rewards
plt.subplot(1, 2, 1)
plt.plot(rewards, label='Total Reward')
plt.xlabel('Episode')
plt.ylabel('Total Reward')
plt.title('Total Reward per Episode')
plt.legend()

# Plot scores
plt.subplot(1, 2, 2)
plt.plot(scores, label='Score')
plt.xlabel('Episode')
plt.ylabel('Score')
plt.title('Score per Episode')
plt.legend()

plt.tight_layout()
plt.show()