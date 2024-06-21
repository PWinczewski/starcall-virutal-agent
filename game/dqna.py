import random
import numpy as np
from collections import deque
import tensorflow as tf
from tensorflow.keras import layers, models

class DQNAgent:
    def __init__(self, state_size, action_size):
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=2000)
        self.gamma = 0.95  
        self.epsilon = 1.0 
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.model = self._build_model(state_size, action_size)
        self.target_model = self._build_model(state_size, action_size)
        self.update_target_model()

    def _build_model(self, state_size, action_size):
        model = models.Sequential()
        model.add(layers.Dense(128, activation='relu', input_shape=(state_size,)))
        model.add(layers.Dense(128, activation='relu'))
        model.add(layers.Dense(np.prod(action_size), activation='linear'))
        model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.001), loss='mse')
        return model


    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def act(self, state, useRand):
        if np.random.rand() <= self.epsilon and useRand:
            action = [random.randint(0, self.action_size[0] - 1), random.randint(0, self.action_size[1] - 1)]
        else:
            act_values = self.model.predict(state)
            action_idx = np.argmax(act_values[0])
            action = [action_idx // self.action_size[1], action_idx % self.action_size[1]]
        return action

    def replay(self, batch_size):
        minibatch = random.sample(self.memory, batch_size)
        for state, action, reward, next_state, done in minibatch:
            target = self.model.predict(state)
            action_idx = action[0] * self.action_size[1] + action[1]
            if done:
                target[0][action_idx] = reward
            else:
                t = self.target_model.predict(next_state)[0]
                target[0][action_idx] = reward + self.gamma * np.amax(t)
            self.model.fit(state, target, epochs=1, verbose=0)
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay

    def load(self, name):
        self.model.load_weights(name)

    def save(self, name):
        self.model.save_weights(name)
