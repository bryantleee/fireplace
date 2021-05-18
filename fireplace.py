import random
from typing import List, Tuple
from collections import deque

from PIL import Image
import numpy as np

def generate_fireplace_frame(fireplace_matrix: List[List[Tuple(int)]]) -> List[List[Tuple(int)]]:
    '''
    Generates a single frame of a fireplace, with each Tuple's representing an RGB pixel color
        - fireplace_matrix: 18 x 24 list of list of 0's
    
    Returns the a 18 x 24 list of list of Tuples of RGB pixel colors
    '''
    pixel_states = {j : 0 for j in range(len(fireplace_matrix[0]))}

    # formula to determine fire max height
    y = lambda x : -(1/15)*((x - 12)**2) + 12

    # there is a chance to the kill the fire column at each row, increases as you get closer to bound
    death_chance = {
        12 : 0,
        11 : 0,
        10 : 0,
        9 : 0,
        8 : 0,
        7 : 0,
        6 : 0,
        5 : .20,
        4 : .30,
        3 : .35,
        2 : .40,
        1 : .40,
        0 : .45
    }
    
    for i, row in enumerate(fireplace_matrix):
        for j, pixel in enumerate(row):
            
            # max pixel height
            bound = y(j)
            
            bound_delta = bound - i

            if bound_delta > 0:
                # Determine whether to kill using death chances
                modifier = 0.1 if pixel_states.get(j - 1) == 2 else 0
                to_kill = random.random() < death_chance[int(bound_delta)] + modifier
                
                to_flicker = random.random() < 0.02

                # Pixel is valid under certain conditions
                if i <= bound and not to_kill and pixel_states.get(j) != 2 and not to_flicker:
                    fireplace_matrix[i][j] = generate_pixel_color(bound_delta)
                
                # only allow for one-pixel wide fire gaps
                if pixel_states.get(j) == 1:
                    pixel_states[j] = 2
                
                # randomly determine if we allow for a pixel gap
                if to_kill and pixel_states.get(j) != 2:
                    pixel_states[j] = 1 if random.random() < 0.3 else 2
    
    return fireplace_matrix


def generate_pixel_color(bound_delta: float) -> Tuple[int]:
    '''
    Generates the pixel color of the fire, with a different probability depending on region
        
        - bound_delta: distance between pixel and upper bound of the fire
    
    Returns a tuple of three integers in representing the RGB color of pixels
    '''
    # possible pixel colors
    colors = deque([(251, 237, 83),(248, 221, 78), 
                    (246, 201, 73), (244, 183, 68), (255, 159, 56), (241, 146, 63)])
    
    # change probabilities depending on distance to the upper bound
    colors.rotate((int(bound_delta) + 1) // 2)
    return random.choices(colors, weights=[50, 25, 15, 10, 0, 0])[0]
    # return random.choices(colors, weights=[100, 0, 0, 0, 0, 0])[0]


if __name__ == '__main__':
    
    for i in range(10):
        fireplace_matrix = [[(0,0,0) for i in range(25)] for i in range(18)]
        fireplace_frame = generate_fireplace_frame(fireplace_matrix)
        
        # Convert the pixels into an array using numpy
        array = np.array(fireplace_frame[::-1], dtype=np.uint8)

        # Use PIL to create an image from the new array of pixels
        new_image = Image.fromarray(array)
        new_image.save('image_samples/{}.png'.format(i))