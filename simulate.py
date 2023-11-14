"""Run the battle simulation using a pygame window.

This is the main file to be run to simulate a battle. 
It instantiates the ants and manages them using provided pre-programmed .py files.
It also manages the pygame window and displays the ants on the screen.
"""

import math
import pygame
from models import Battle, Ant

# Import the antgorithms form ./antgorithms .py files
from antgorithms import wandering_ant, attacking_ant, scared_ant

# Let's set up two test ants
battle = Battle()
battle.bounds = (800, 800)


BASIC_ANT_STATS = {
    "health": 100,
    "speed": 1,
    "damage": 50,
    "attack_range": 10,
    "sense_range": 50
}

for i in range(100):
    x = i*5 + 50
    y = 50
    rot = 0
    blue_ant = Ant(battle, "blue", 
                   stats_dict=BASIC_ANT_STATS,
                   init_position=(x,y,rot), 
                   antgorithm=scared_ant.antgorithm)

for i in range(100):
    x = i*5 + 50
    y = 750
    rot = 1.75*math.pi
    red_ant = Ant(battle, "red",
                  stats_dict=BASIC_ANT_STATS,
                  init_position=(x,y,rot),
                  antgorithm=scared_ant.antgorithm)

pygame.init()

# Set up the drawing window
screen = pygame.display.set_mode([battle.bounds[0], battle.bounds[1]])

# Run until the user asks to quit
running = True

# Draw the ants
def draw_ants(screen, battle):
    """Draw the ants on the screen."""
    for ant in battle.ants:
        if ant.alive:
            if ant.team == "blue":
                # Draw a triangle pointing in the direction of the ant
                pygame.draw.polygon(screen, (0, 0, 255), [(ant.x, ant.y), (ant.x + 10 * math.cos(ant.rotation + 2 * math.pi / 3), ant.y + 10 * math.sin(ant.rotation + 2 * math.pi / 3)), (ant.x + 10 * math.cos(ant.rotation - 2 * math.pi / 3), ant.y + 10 * math.sin(ant.rotation - 2 * math.pi / 3))])
            elif ant.team == "red":
                pygame.draw.polygon(screen, (255, 0, 0), [(ant.x, ant.y), (ant.x + 10 * math.cos(ant.rotation + 2 * math.pi / 3), ant.y + 10 * math.sin(ant.rotation + 2 * math.pi / 3)), (ant.x + 10 * math.cos(ant.rotation - 2 * math.pi / 3), ant.y + 10 * math.sin(ant.rotation - 2 * math.pi / 3))])
            # Draw a sensing range circle
            # pygame.draw.circle(screen, (0, 0, 0), (int(ant.x), int(ant.y)), ant.sense_range, 1)

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

    # Execute the ants' programs
    for ant in battle.ants:
        if ant.alive:
            method, kwargs = ant.antgorithm(ant)
            # Each antgorithm returns an ant method and a dictionary of keyword arguments
            callable_method = getattr(ant, method)
            callable_method(**kwargs)

    # End of tick housekeeping
    battle.resolve_attacks()
    battle.game_tick += 1

    # Wait 10 ms
    pygame.time.wait(1)

# Done! Time to quit.
pygame.quit()
