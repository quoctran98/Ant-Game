"""Run the battle simulation using a pygame window.

This is the main file to be run to simulate a battle. 
It instantiates the ants and manages them using provided pre-programmed .py files.
It also manages the pygame window and displays the ants on the screen.
"""

import multiprocessing
import math
import pygame
from models import Battle, Ant

# Import the antgorithms form ./antgorithms .py files
from antgorithms import wandering_ant, attacking_ant, scared_ant, circle_ant, test_ant, marching_ant, squadron_ant

battle = Battle()
battle.bounds = (800, 800)

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([battle.bounds[0], battle.bounds[1]])

# Run until the user asks to quit
running = True


BASIC_ANT_STATS = {
    "size": 10,
    "health": 2,
    "speed": 1,
    "block_damage": 1,
    "bite_damage": 1,
    "bite_range": 10,
    "bite_angle": math.pi/4,
    "smell_range": 100
}

for i in range(100):
    x = i*7 + 10
    y = 700
    rot = 3/2*math.pi
    red_ant = Ant(battle, "red",
                  stats_dict=BASIC_ANT_STATS,
                  init_position=(x,y,rot),
                  antgorithm=squadron_ant.antgorithm)
    
for i in range(100):
    x = i*7 + 10
    y = 100
    rot = 1/2*math.pi
    blue_ant = Ant(battle, "blue", 
                   stats_dict=BASIC_ANT_STATS,
                   init_position=(x,y,rot), 
                   antgorithm=scared_ant.antgorithm)

# Draw the ants
def draw_ants(screen, battle):
    """Draw the ants on the screen."""
    for ant in battle.ants:
        if ant.alive:
            # Rotate the ant's surface to match its rotation
            rotated_ant = pygame.transform.rotate(ant.body_surf, -ant.rotation*180/math.pi - 90 % 360)
            rotated_ant.set_colorkey((255, 255, 255))
            # Draw the ant's surface (centered at the ant's position)
            screen.blit(rotated_ant, (ant.x - rotated_ant.get_width()/2, ant.y - rotated_ant.get_height()/2))
            
            # Draw the ant's hitbox
            # pygame.draw.circle(screen, (255, 0, 0), (int(ant.x), int(ant.y)), ant.size, 1)

def execute_antgorithm(ant):
    """Wrapper to execute the ant's antgorithm."""
    ant_copy = ant.copy() # So the ant can't be modified by the antgorithm
    new_memory = ant_copy.memory.copy() # Memory is allowed to be modified :)
    method_name, kwargs_dict = ant_copy.antgorithm(ant_copy)
    return(method_name, kwargs_dict, new_memory)

# Main loop
while running:

    # Did the user click the window close button?
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Fill the background with white
    screen.fill((255, 255, 255))

    # Draw the ants
    draw_ants(screen, battle)

    # Flip the display
    pygame.display.flip()

    # Execute the ants' programs (using multiprocessing)
    # with multiprocessing.Pool() as pool:
    #     instructions = pool.map(execute_antgorithm, battle.ants)
    #     for method, kwargs, ant in zip(instructions, battle.ants):
    #         callable_method = getattr(ant, method)
    #         callable_method(**kwargs)

    for ant in battle.ants:
        if ant.alive:
            # Execute the ant's antgorithm, update memory, and log the instruction
            method_name, kwargs_dict, new_memory = execute_antgorithm(ant)
            ant.memory = new_memory
            battle.instruction_queue[ant.id] = (method_name, kwargs_dict)

    # End of tick housekeeping
    battle.resolve_instructions()
    battle.resolve_attacks()
    battle.resolve_messages()
    battle.game_tick += 1

    # Wait 10 ms
    pygame.time.wait(10)

# Done! Time to quit.
pygame.quit()
