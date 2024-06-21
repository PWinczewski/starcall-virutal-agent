import matplotlib.pyplot as plt
from gameEnv import GameEnv 
from dqna import DQNAgent
import numpy as np

import datetime
import time

env = GameEnv()
state_size = env._get_state().shape[0]
action_size = (3,2)
agent = DQNAgent(state_size, action_size)
# agent.load("weights/v4/dqn_best_model_reward.weights.h5")
episodes = 100
batch_size = 32

action_frame_lock = 2
model_update_frequency = 5
render=False

rewards = []
scores = []

running=True
stop_time = datetime.time(10, 00, 0)
current_time = datetime.datetime.now().time()

best_reward = -float('inf')
best_score = -float('inf')

print(stop_time, current_time, current_time >= stop_time)
while running:
    current_time = datetime.datetime.now().time()
    for episode in range(episodes):

        state = env.reset()
        state = np.reshape(state, [1, state_size])
        total_reward = 0
        score=0
        
        for time in range(5000): 
            if time % action_frame_lock == 0:
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
            agent.save("dump5/dqn_best_model_reward.weights.h5")
        
        if score // 10 > best_score: 
            best_score = score // 10
            agent.save("dump5/dqn_best_model_score.weights.h5")

        if episode % model_update_frequency == 0:
            agent.update_target_model()
            agent.save(f"dump5/dqn_model_episode_{episode}.weights.h5")

        if current_time >= stop_time:
            running = False
            agent.save(f"dump5/dqn_model_episode_{episode}.weights.h5")
            break


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