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
from antgorithms import wandering_ant, attacking_ant, scared_ant, circle_ant, test_ant, marching_ant, squadron_ant, super_squad_ant


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

N_ANTS = 100

def add_ants(battle, team, center, n_ants, antgorithm, stats=BASIC_ANT_STATS, rotation=None):
    """Add a number of ants to the Battle object."""
    for _ in range(n_ants):
        x = center[0] + random.randint(-40, 40)
        y = center[1] + random.randint(-40, 40)
        rot = random.random() * 2 * math.pi if rotation is None else rotation
        ant = Ant(battle, team, stats_dict=stats,
                    init_position=(x,y,rot),
                    antgorithm=antgorithm)

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

def draw_stats(screen, battle):
    # List the population counts
    red_count = len([ant for ant in battle.ants if ant.alive and ant.team == "red"])
    blue_count = len([ant for ant in battle.ants if ant.alive and ant.team == "blue"])
    green_count = len([ant for ant in battle.ants if ant.alive and ant.team == "green"])
    black_count = len([ant for ant in battle.ants if ant.alive and ant.team == "black"])

    # Draw the population counts
    font = pygame.font.SysFont("Comic Sans", 24)
    red_count_surf = font.render(f"Red: {red_count}", True, (255, 0, 0))
    blue_count_surf = font.render(f"Blue: {blue_count}", True, (0, 0, 255))
    green_count_surf = font.render(f"Green: {green_count}", True, (0, 255, 0))
    black_count_surf = font.render(f"Black: {black_count}", True, (0, 0, 0))
    screen.blit(red_count_surf, (battle.bounds[0] + 10, 10))
    screen.blit(blue_count_surf, (battle.bounds[0] + 10, 40))
    screen.blit(green_count_surf, (battle.bounds[0] + 10, 70))
    screen.blit(black_count_surf, (battle.bounds[0] + 10, 100))

def execute_antgorithm(ant):
    """Wrapper to execute the ant's antgorithm."""
    return(ant.antgorithm(ant))

if __name__ == "__main__":

    # Initialize pygame
    pygame.init()
    running = True

    # Set up the battle
    battle = Battle()
    battle.bounds = (800, 800)

    # Draw the screen
    screen = pygame.display.set_mode([battle.bounds[0] + 400, battle.bounds[1]])
    screen.fill((255, 255, 255))

    # Draw the arena
    arena = pygame.Surface(battle.bounds)
    arena.fill((255, 255, 255))
    screen.blit(arena, (0, 0))

    # Add the ants to the battle
    add_ants(battle, "red", (400, 50), 100, squadron_ant.antgorithm)
    add_ants(battle, "blue", (400, 750), 100, super_squad_ant.antgorithm)
    add_ants(battle, "green", (50, 400), 100, attacking_ant.antgorithm)
    add_ants(battle, "black", (750, 400), 100, scared_ant.antgorithm)

    # Draw a border around the arena
    pygame.draw.rect(screen, (0, 0, 0), (0, 0, battle.bounds[0], battle.bounds[1]), 1)

    # Start the pygame loop
    while running:

        # Quit if the window is closed
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # # Save and remove the ants' surfaces (to avoid pickling errors)
        # ant_surfaces = [a.body_surf for a in battle.ants]
        # battle.ants = [a._replace(body_surf=None) for a in battle.ants]

        # # Execute the ants' programs (using multiprocessing)
        # with multiprocessing.Pool() as pool:
        #     instructions = pool.map(execute_antgorithm, battle.ants)
        #     for ant, instruction in zip(battle.ants, instructions):
        #         battle.instruction_queue[ant.id] = instruction

        # # Restore the ants' surfaces
        # battle.ants = [a._replace(body_surf=surf) for a, surf in zip(battle.ants, ant_surfaces)]

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

        # Check if the battle is over
        if (len(set([ant.team for ant in battle.ants if ant.alive])) == 1):
            font = pygame.font.SysFont("Comic Sans", 100)
            message = font.render(f"{battle.ants[0].team} team wins!", True, (0, 0, 0))
            screen.blit(message, (battle.bounds[0]/2 - message.get_width()/2, battle.bounds[1]/2 - message.get_height()/2))
            pygame.display.flip()

            # Wait for input
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                        break
                    if event.type == pygame.KEYDOWN:
                        running = False
                        break
                if not running:
                    break

        # Update the screen
        screen.fill((255, 255, 255))
        draw_ants(screen, battle)
        draw_stats(screen, battle)
        pygame.display.flip()

        # Wait 10 ms
        # pygame.time.wait(10)

