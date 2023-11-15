"""Run the battle simulation using a pygame window.

This is the main file to be run to simulate a battle. 
It instantiates the ants and manages them using provided pre-programmed .py files.
It also manages the pygame window and displays the ants on the screen.
"""

import multiprocessing
import math
import pygame
import random
from models import Battle, Ant

# Import the antgorithms form ./antgorithms .py files
from antgorithms import wandering_ant, attacking_ant, scared_ant, circle_ant, test_ant, marching_ant, squadron_ant

battle = Battle()
battle.bounds = (800, 800)

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([battle.bounds[0] + 400, battle.bounds[1]])
arena = pygame.Surface(battle.bounds)
arena.fill((255, 255, 255))
screen.blit(arena, (0, 0))

# Draw a border around the arena
pygame.draw.rect(screen, (0, 0, 0), (0, 0, battle.bounds[0], battle.bounds[1]), 1)

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
    "smell_range": 50
}

N_ANTS = 100

red_center = (400, 50)
red_antgorithm = squadron_ant.antgorithm
for _ in range(N_ANTS):
    x = red_center[0] + random.randint(-50, 50)
    y = red_center[1] + random.randint(-50, 50)
    rot = random.random() * 2 * math.pi
    red_ant = Ant(battle, "red",
                  stats_dict=BASIC_ANT_STATS,
                  init_position=(x,y,rot),
                  antgorithm=squadron_ant.antgorithm)
    
blue_center = (400, 750)
blue_antgorithm = attacking_ant.antgorithm
for _ in range(N_ANTS):
    x = blue_center[0] + random.randint(-50, 50)
    y = blue_center[1] + random.randint(-50, 50)
    rot = 3/2 * math.pi
    blue_ant = Ant(battle, "blue", 
                   stats_dict=BASIC_ANT_STATS,
                   init_position=(x,y,rot), 
                   antgorithm=attacking_ant.antgorithm)

green_center = (50, 400)
green_antgorithm = marching_ant.antgorithm
for _ in range(N_ANTS):
    x = green_center[0] + random.randint(-50, 50)
    y = green_center[1] + random.randint(-50, 50)
    rot = random.random() * 2 * math.pi
    green_ant = Ant(battle, "green", 
                    stats_dict=BASIC_ANT_STATS,
                    init_position=(x,y,rot), 
                    antgorithm=marching_ant.antgorithm)
    
black_center = (750, 400)
black_antgorithm = scared_ant.antgorithm
for _ in range(N_ANTS):
    x = black_center[0] + random.randint(-50, 50)
    y = black_center[1] + random.randint(-50, 50)
    rot = random.random() * 2 * math.pi
    yellow_ant = Ant(battle, "black", 
                     stats_dict=BASIC_ANT_STATS,
                     init_position=(x,y,rot), 
                     antgorithm=scared_ant.antgorithm)


# Draw the ants
def draw_ants(screen, battle):
    """Draw the ants on the screen."""

    # Draw the arena and a border around it
    screen.blit(arena, (0, 0))
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, battle.bounds[0], battle.bounds[1]), 1)

    # Draw the ants
    for ant in battle.ants:
        if ant.alive:
            # Rotate the ant's surface to match its rotation
            rotated_ant = pygame.transform.rotate(ant.body_surf, -ant.rotation*180/math.pi - 90 % 360)
            rotated_ant.set_colorkey((255, 255, 255))
            # Draw the ant's surface (centered at the ant's position)
            screen.blit(rotated_ant, (ant.x - rotated_ant.get_width()/2, ant.y - rotated_ant.get_height()/2))
            
            # Draw the ant's hitbox
            # pygame.draw.circle(screen, (255, 0, 0), (int(ant.x), int(ant.y)), ant.size, 1)

    # List the population counts
    red_count = len([ant for ant in battle.ants if ant.alive and ant.team == "red"])
    blue_count = len([ant for ant in battle.ants if ant.alive and ant.team == "blue"])

    # Draw the population counts
    font = pygame.font.SysFont("Comic Sans", 24)
    red_count_surf = font.render(f"Red: {red_count}", True, (255, 0, 0))
    blue_count_surf = font.render(f"Blue: {blue_count}", True, (0, 0, 255))
    green_count_surf = font.render(f"Green: {blue_count}", True, (0, 255, 0))
    black_count_surf = font.render(f"Black: {blue_count}", True, (0, 0, 0))
    screen.blit(red_count_surf, (battle.bounds[0] + 10, 10))
    screen.blit(blue_count_surf, (battle.bounds[0] + 10, 40))
    screen.blit(green_count_surf, (battle.bounds[0] + 10, 70))
    screen.blit(black_count_surf, (battle.bounds[0] + 10, 100))

def execute_antgorithm(ant):
    """Wrapper to execute the ant's antgorithm."""
    # ant_copy = ant.copy() # Ant is not allowed to be modified :)
    # new_memory = ant_copy.memory.copy() # Memory is allowed to be modified :)
    if (ant.team == "blue"):
        method_name, kwargs_dict = blue_antgorithm(ant)
    elif (ant.team == "red"):
        method_name, kwargs_dict = red_antgorithm(ant)
    elif (ant.team == "green"):
        method_name, kwargs_dict = green_antgorithm(ant)
    elif (ant.team == "black"):
        method_name, kwargs_dict = black_antgorithm(ant)
    return(method_name, kwargs_dict)

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
    #     for ant, instruction in zip(battle.ants, instructions):
    #         battle.instruction_queue[ant.id] = instruction

    for ant in battle.ants:
        if ant.alive:
            # Execute the ant's antgorithm, update memory, and log the instruction
            method_name, kwargs_dict = execute_antgorithm(ant)
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
