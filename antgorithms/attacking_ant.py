import math
import random

def antgorithm(self):
    
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
        # Find the nearest enemy ant
        angle_to_nearest_ant = self.angle_toward(self.nearest(enemies_nearby))

        # Bite if an enemy ant is in attackble range
        attackable_ants = self.attackable(include_teammates=False)
        if len(attackable_ants) > 0:
            return("bite", {})
        
        # Walk towards the nearest ant, if the angle is close enough
        if abs(angle_to_nearest_ant - self.rotation) < math.pi/2:
            return("walk", {})
        
        # Turn towards the nearest ant
        return("turn", {"rel_angle": angle_to_nearest_ant - self.rotation})

    # Do a random-ish walk if no ants are nearby
    if (random.random() < 0.1):
        return("turn", {"rel_angle": ((random.random()-0.5)/8) * 2 * math.pi})
    else:
        return("walk", {})