import math
import random

def antgorithm(self):

    # Determine if this ant will be a blocking ant or a running ant
    if (self.battle.game_tick == 0):
        self.memory["blocking_ant"] = random.random() < 0.5
    
    # Detect nearby ants
    enemies_nearby = self.sense(include_teammates=False)
    friends_nearby = self.sense(include_enemies=False)

    # If we're near the edge of the battle, turn and walk towards the center
    if self.near_bounds(buffer=10):
        center = (self.battle.bounds[0]/2, self.battle.bounds[1]/2)
        angle_to_center = self.angle_toward(center)
        if abs(angle_to_center - self.rotation) > math.pi/8:
            return("turn", {"rel_angle": angle_to_center - self.rotation})
        else:
            return("walk", {})

    if len(enemies_nearby) > 0:

        # If it's a blocking ant, block (if they got too close)
        nearest_enemy = self.nearest(enemies_nearby)
        if self.memory["blocking_ant"] and self.distance_to(nearest_enemy) < self.bite_range:
            return("block", {})

        # Run away from the average angle of the enemies
        angles_away_from_enemies = [self.angle_toward(enemy) + math.pi % (2*math.pi) for enemy in enemies_nearby]
        avg_angle_away = sum(angles_away_from_enemies)/len(angles_away_from_enemies) % (2*math.pi)
        if abs(avg_angle_away - self.rotation) > math.pi/8:
            return("turn", {"rel_angle": avg_angle_away - self.rotation})
        else:
            return("walk", {})

    # Do a random-ish walk if no ants are nearby
    if (random.random() < 0.1):
        return("turn", {"rel_angle": ((random.random()-0.5)/8) * 2 * math.pi})
    else:
        return("walk", {})