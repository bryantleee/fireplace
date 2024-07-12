import random
from typing import List, Tuple, Dict
from collections import deque
from PIL import Image
import cv2
import numpy as np

class Fireplace:
    def __init__(self, rows: int = 18, cols: int = 25):
        self.rows = rows
        self.cols = cols
        self.ember_color = (194, 84, 35)
        self.palette = ((251, 237, 83), (248, 221, 78), (246, 201, 73), (244, 183, 68), (255, 159, 56), (241, 146, 63))
        self.death_chance = self.calculate_death_chance()

        
    def calculate_death_chance(self) -> Dict[int, float]:
        # minimum and maximum death chances
        min_death_chance = 0.05
        max_death_chance = 0.7

        # threshold for zero death chance (e.g., top third of the fire)
        zero_death_threshold = self.rows // 2

        # there is a chance to kill the fire column at each row, increases as you get closer to bound
        return {
            i: 0 if i > zero_death_threshold else abs(min_death_chance + (max_death_chance - min_death_chance) * ((i - zero_death_threshold) / (self.rows - zero_death_threshold)))
            for i in range(self.rows)
        }
    
    def generate_fireplace_frame(self, ember_locations: Dict[int, int], blember_locations: Dict[int, int]) -> List[List[Tuple[int]]]:
        fireplace_matrix = [[(0, 0, 0) for _ in range(self.cols)] for _ in range(self.rows)]
        pixel_states = {j: 0 for j in range(self.cols)}
        
        y = lambda x: -1 / self.cols * ((x - (self.cols / 2)) ** 2) + (self.rows / 1.5)
        
        self.update_embers(ember_locations, blember_locations)
        
        for i in range(self.rows):
            for j in range(self.cols):
                if i == 0 and random.random() < 0.02:
                    blember_locations[j] = 0
                
                bound = y(j)
                bound_delta = bound - i
                
                if bound_delta > 0:
                    self.update_pixel(fireplace_matrix, ember_locations, blember_locations, pixel_states, i, j, bound_delta)
                
                if ember_locations[j] == i:
                    fireplace_matrix[i][j] = self.ember_color
        
        return fireplace_matrix, ember_locations, blember_locations
    
    def update_embers(self, ember_locations: Dict[int, int], blember_locations: Dict[int, int]) -> None:
        for j in ember_locations:
            if ember_locations[j] >= 0:
                ember_locations[j] += 1
                if ember_locations[j] >= self.rows:
                    ember_locations[j] = -1
            if blember_locations[j] >= 0:
                blember_locations[j] += 1
                if blember_locations[j] >= self.rows:
                    blember_locations[j] = -1
    
    def update_pixel(self, fireplace_matrix: List[List[Tuple[int]]], ember_locations: Dict[int, int], 
                     blember_locations: Dict[int, int], pixel_states: Dict[int, int], i: int, j: int, bound_delta: float) -> None:
        modifier = 0.1 if pixel_states.get(j - 1) == 2 else 0
        to_kill = random.random() < self.death_chance.get(int(bound_delta), 0.5) + modifier
        to_flicker = random.random() < 0.02
        
        if i <= bound_delta and not to_kill and pixel_states.get(j) != 2 and not to_flicker and not blember_locations[j] == i:
            fireplace_matrix[i][j] = self.generate_pixel_color(bound_delta)
        
        if pixel_states.get(j) == 1:
            pixel_states[j] = 2
        elif to_kill and pixel_states.get(j) != 2:
            pixel_states[j] = 1 if random.random() < 0.3 else 2
            if pixel_states[j] == 2 and ember_locations[j] == -1 and random.random() < 0.4:
                fireplace_matrix[i][j] = self.ember_color
    
    def generate_pixel_color(self, bound_delta: float) -> Tuple[int]:
        colors = deque(self.palette)
        weights = (50, 25, 15, 10, 0, 0)
        colors.rotate((int(bound_delta) + 1) // 2)
        return random.choices(colors, weights=weights)[0]

    def generate_frame_image(self, fireplace_frame):
        array = np.array(fireplace_frame[::-1], dtype=np.uint8)
        resized = cv2.resize(array, (500, 360), interpolation=cv2.INTER_AREA)
        return Image.fromarray(resized)

    def __iter__(self):
        return FireplaceIterator(self)

class FireplaceIterator:
    def __init__(self, fireplace: Fireplace):
        self.fireplace = fireplace
        self.ember_locations = {j: -1 for j in range(fireplace.cols)}
        self.blember_locations = {j: -1 for j in range(fireplace.cols)}

    def __next__(self):
        fireplace_matrix, self.ember_locations, self.blember_locations = self.fireplace.generate_fireplace_frame(self.ember_locations, self.blember_locations)
        return self.fireplace.generate_frame_image(fireplace_matrix)
