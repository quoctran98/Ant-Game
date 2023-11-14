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
        
    # Do a random-ish walk
    if (random.random() < 0.1):
        return("turn", 
                {"rel_angle": ((random.random()-0.5)/8) * 2 * math.pi})
    else:
        return("walk", {})