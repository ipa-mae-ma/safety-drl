import os
from copy import deepcopy
import pygame
import numpy as np
import time
# or FruitCollectionLarge or FruitCollectionMini
from fruit_collection import FruitCollection, FruitCollectionSmall, FruitCollectionLarge

# RGB colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 100, 255)
WALL = (80, 80, 80)

class TrainFruitCollection(FruitCollection):
    def init_with_mode(self):
        self.is_ghost = False
        self.is_fruit = True
        self.reward_scheme = {'ghost': -10.0, 'fruit': +1.0, 'step': 0.0, 'wall': 0.0}
        self.nb_fruits = 4
        self.scr_w = 5
        self.scr_h = 5
        self.possible_fruits = [[0, 0], [0, 4], [4, 0], [4, 4]]
        self.rendering_scale = 50
        self.walls = [[1, 0], [2, 0], [4, 1], [0, 2], [2, 2], [3, 3], [1, 4]]
        if self.is_ghost:
            self.ghosts = [{'colour': RED, 'reward': self.reward_scheme['ghost'], 'location': [0, 1],
                            'active': True}]
        else:
            self.ghosts = []

    def _reset_targets(self):
        while True:
            self.player_pos_x, self.player_pos_y = np.random.randint(0, self.scr_w), np.random.randint(0, self.scr_h)
            if [self.player_pos_x, self.player_pos_y] not in self.possible_fruits + self.walls:
                break
        self.fruits = []
        self.active_fruits = []
        if self.is_fruit:
            for x in range(self.scr_w):
                for y in range(self.scr_h):
                    self.fruits.append({'colour': BLUE, 'reward': self.reward_scheme['fruit'],
                                        'location': [x, y], 'active': False})
                    self.active_fruits.append(False)
            fruits_idx = deepcopy(self.possible_fruits)
            np.random.shuffle(fruits_idx)
            fruits_idx = fruits_idx[:self.nb_fruits]
            self.mini_target = [False] * len(self.possible_fruits)
            for f in fruits_idx:
                idx = f[1] * self.scr_w + f[0]
                self.fruits[idx]['active'] = True
                self.active_fruits[idx] = True
                self.mini_target[self.possible_fruits.index(f)] = True

    def main(self):
        reward = []
        env = FruitCollectionLarge(rendering=True, lives=1, is_fruit=True, is_ghost=True, image_saving=False)
        env.reset()
        env.render()

        for _ in range(50):
            action = np.random.choice(env.legal_actions)
            obs, r, terminated, info = env.step(action)
            env.render()
            if terminated == False:
                reward.append(r)
            time.sleep(.01)
            if terminated == True:
                print(sum(reward))
                reward = []
                self.main()

if __name__ == '__main__':
    afc = TrainFruitCollection()
    afc.main()
