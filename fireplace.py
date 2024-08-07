import random
from typing import List, Tuple, Dict
from collections import deque
from PIL import Image
import cv2
import numpy as np

class Fireplace:
    def generate_fireplace_frame(self, fireplace_matrix: List[List[Tuple[int]]], 
        ember_locations: Dict, blember_locations: Dict, palette=((251, 237, 83),(248, 221, 78), 
                        (246, 201, 73), (244, 183, 68), (255, 159, 56), (241, 146, 63))) -> List[List[Tuple[int]]]:
        '''
        Generates a single frame of a fireplace, with each Tuple representing an RGB pixel color
        '''
        rows = len(fireplace_matrix)
        cols = len(fireplace_matrix[0])
        pixel_states = {j: 0 for j in range(cols)}

        # Each column can have 1 ember on the screen max at a time
        ember_color = (194, 84, 35)
        
        # formula to determine fire max height
        y = lambda x: -1 / cols * ((x - (cols / 2)) ** 2) + (rows / 1.5)

        # minimum and maximum death chances
        min_death_chance = 0.05
        max_death_chance = 0.7

        # threshold for zero death chance (e.g., top third of the fire)
        zero_death_threshold = rows // 2

        # there is a chance to kill the fire column at each row, increases as you get closer to bound
        death_chance = {
            i: 0 if i > zero_death_threshold else abs(min_death_chance + (max_death_chance - min_death_chance) * ((i - zero_death_threshold) / (rows - zero_death_threshold)))
            for i in range(rows)
        }

        # move all embers up by one
        for j in ember_locations:
            if ember_locations[j] >= 0:
                ember_locations[j] += 1

                if ember_locations[j] >= rows:
                    ember_locations[j] = -1

            if blember_locations[j] >= 0:
                blember_locations[j] += 1
                
                if blember_locations[j] >= rows:
                    blember_locations[j] = -1

        for i, row in enumerate(fireplace_matrix):
            for j, pixel in enumerate(row):
                
                if i == 0 and random.random() < 0.02:
                    blember_locations[j] = 0

                # max pixel height
                bound = y(j)
                
                bound_delta = bound - i

                if bound_delta > 0:
                    # Determine whether to kill using death chances
                    modifier = 0.1 if pixel_states.get(j - 1) == 2 else 0
                    to_kill = random.random() < death_chance.get(int(bound_delta), 0.5) + modifier
                    
                    # Each pixel has a chance of flickering (being black)
                    to_flicker = random.random() < 0.02

                    # Pixel is valid under certain conditions
                    if i <= bound and not to_kill and pixel_states.get(j) != 2 and not to_flicker and not blember_locations[j] == i:
                        fireplace_matrix[i][j] = self.generate_pixel_color(bound_delta, palette)
                    
                    # only allow for one-pixel wide fire gaps
                    if pixel_states.get(j) == 1:
                        pixel_states[j] = 2

                    elif to_kill and pixel_states.get(j) != 2:
                        # randomly determine if we allow for a pixel gap
                        pixel_states[j] = 1 if random.random() < 0.3 else 2

                        # sometimes a killed fire can make an ember
                        if pixel_states[j] == 2 and ember_locations[j] == -1 and random.random() < 0.4:
                            fireplace_matrix[i][j] = ember_color
                            ember_locations[j] = i

                if ember_locations[j] == i:
                    fireplace_matrix[i][j] = ember_color
        return fireplace_matrix, ember_locations, blember_locations

    
    def generate_pixel_color(self, bound_delta: float, palette) -> Tuple[int]:
        '''
        Generates the pixel color of the fire, with a different probability depending on region
            
        - bound_delta: distance between pixel and upper bound of the fire
        
        Returns a tuple of three integers representing the RGB color of pixels
        '''
        # possible pixel colors
        colors = deque(palette)
        weights = (50, 25, 15, 10, 0, 0)

        # change probabilities depending on distance to the upper bound
        colors.rotate((int(bound_delta) + 1) // 2)
        return random.choices(colors, weights=weights)[0]


    def generate_frame_image(self, fireplace_frame):
        '''
        Generate image
        '''    
        array = np.array(fireplace_frame[::-1], dtype=np.uint8)
        # new_image = Image.fromarray(array)
        resized = cv2.resize(array, (500, 360), interpolation=cv2.INTER_AREA)
        return Image.fromarray(resized)


    def __iter__(self):
        '''
        Iterator to easily access future frames in the image
        '''
        return FireplaceIterator(self)


class FireplaceIterator:
    def __init__(self, fireplace: Fireplace, rows: int = 18, cols: int = 25):
        self.fireplace = fireplace
        self.rows = rows
        self.cols = cols
        self.fireplace_matrix = [[(0, 0, 0) for _ in range(cols)] for _ in range(rows)]
        self.ember_locations = {j: -1 for j in range(cols)}
        self.blember_locations = {j: -1 for j in range(cols)}

    def __next__(self):
        self.fireplace_matrix = [[(0, 0, 0) for _ in range(self.cols)] for _ in range(self.rows)]
        fireplace_frame, self.ember_locations, self.blember_locations = self.fireplace.generate_fireplace_frame(self.fireplace_matrix, self.ember_locations, self.blember_locations)
        return self.fireplace.generate_frame_image(fireplace_frame)
