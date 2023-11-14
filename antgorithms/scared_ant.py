import math
import random

def antgorithm(self):
    
    # Detect nearby ants and ignore friendly ants
    ants_nearby = self.sense()
    ants_nearby = [ant for ant in ants_nearby if ant[2] != self.team] 

    # If near the edge of the screen, turn toward the center (unless already doing so)
    # This is really annoying because pygame has an inverted y-axis but a conventional unit circle
    dx = self.x - self.battle.bounds[0]/2
    dy = self.y - self.battle.bounds[1]/2
    angle_to_center = abs(math.atan2(dy, dx) + math.pi % (2*math.pi))
    if self.x < 10 or self.x > self.battle.bounds[0] - 10 or self.y < 10 or self.y > self.battle.bounds[1] - 10:
        if abs(angle_to_center - self.rotation) > math.pi/8:
            return("turn", {"rel_angle": angle_to_center - self.rotation})
        else:
            return("walk", {})

    # If there are nearby ants, run away from the nearest one
    for ant in ants_nearby:
        nearest_ant = min(ants_nearby, key=lambda x: (x[0] - self.x)**2 + (x[1] - self.y)**2)

        # Again with the inverted y-axis
        dx = nearest_ant[0] - self.x
        dy = nearest_ant[1] - self.y
        angle_away_from_nearest_ant = abs(math.atan2(dy, dx) + math.pi % (2*math.pi)) 
        angle_to_nearest_ant = abs(math.atan2(-dy, -dx) + math.pi % (2*math.pi)) 

        # Have a chance of attacking the nearest ant
        if (random.random() < 0): # Attacking

            # Bite if an enemy ant is in range
            if (nearest_ant[0] - self.x)**2 + (nearest_ant[1] - self.y)**2 < self.range**2:
                return("bite", {})
            
            # Walk towards the nearest ant, if the angle is close enough
            if abs(angle_to_nearest_ant - self.rotation) < math.pi/2:
                return("walk", {})
            
            # Turn towards the nearest ant
            return("turn", {"rel_angle": angle_to_nearest_ant - self.rotation})

        else: # Running away
        
            # Walk away from the nearest ant, if the angle is close enough
            if abs(angle_away_from_nearest_ant - self.rotation) < math.pi/2:
                return("walk", {})
            
            # Turn away from the nearest ant
            return("turn", {"rel_angle": angle_away_from_nearest_ant - self.rotation})

    # Do a random-ish walk if no ants are nearby
    if (random.random() < 0.1):
        return("turn", {"rel_angle": ((random.random()-0.5)/8) * 2 * math.pi})
    else:
        return("walk", {})