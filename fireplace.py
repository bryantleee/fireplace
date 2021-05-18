import random
from typing import List


def generate_fireplace_frame(fireplace_matrix: List[List[int]]) -> List[List[int]]:
    '''
    Generates a single frame of a fireplace, with 1's representing a fire pixel present, and 0 representing no fire pixel present
        - fireplace_matrix: 18 x 24 list of list of 0's
    
    Returns the a 18 x 24 list of list of 0's and 1's
    '''
    pixel_states = {}

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
                to_kill = random.random() < death_chance[int(bound_delta)]
                
                # Pixel is valid under certain conditions
                if i <= bound and not to_kill and pixel_states.get(j) != 2:
                    fireplace_matrix[i][j] = generate_pixel_color(bound_delta)
                
                # only allow for one-pixel wide fire gaps
                if pixel_states.get(j) == 1:
                    pixel_states[j] = 2
                
                # randomly determine if we allow for a pixel gap
                if to_kill and pixel_states.get(j) != 2:
                    pixel_states[j] = 1 if random.random() < 0.3 else 2
    
    return fireplace_matrix


def generate_pixel_color(bound_delta):
    # possible pixel colors
    colors = [(251, 237, 83),(248, 221, 78), (246, 201, 73), (244, 183, 68), (241, 160, 63)]
    #         # [30, 25, 15, 15, 10, 5]
    # bound_delta = int(bound_delta)
    return random.choice(colors)



def inverse_print(fireplace_matrix: List[List[int]]) -> List[List[int]]:
    '''
    Prints by inverting the rows upside-down, for easier visualization
    '''
    for row in reversed(fireplace_matrix):
        print(row)


if __name__ == '__main__':
    fireplace_matrix = [[(0,0,0) for i in range(25)] for i in range(18)]
    fireplace_frame = generate_fireplace_frame(fireplace_matrix)
    inverse_print(fireplace_frame)