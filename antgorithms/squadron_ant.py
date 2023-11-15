import math
import random

def antgorithm(self):

    # Have a few ants declare themselves as squad leaders
    if (self.battle.game_tick == 0):
        if (random.random() < 0.05):
            self.memory["squad_leader"] = True
            self.memory["squadron"] = random.randint(100, 999)
        else:
            self.memory["squad_leader"] = False
            self.memory["squadron"] = None

    # # Relay squad-related messages (message will start with "[squad-relay]")
    # messages = self.receive()
    # for message in messages:
    #     if message.startswith("[squad-relay]"):
    #         # Get how many times this message has been relayed (between parentheses)
    #         relay_count = int(message[message.find("(")+1:message.find(")")])
    #         # Relay the message if it's been relayed less than 10 times
    #         if relay_count < 10:
    #             message = message.replace("(" + str(relay_count) + ")", "(" + str(relay_count+1) + ")")
    #             self.broadcast(message)

    # Only squad leaders will broadcast their squadron number
    if (self.memory["squad_leader"]):
        self.broadcast(f"[{self.memory['squadron']}]")

    # Otherwise, join the one with the closest message
    if (self.memory["squadron"] is None):
        messages = self.receive()
        closest_squadron = None
        closest_squadron_dist = math.inf
        for message in messages:
            if (message.content.startswith("[") and message.content.endswith("]")):
                this_squadron = int(message.content[1:-1])
                this_squadron_dist = self.distance_to((message.x, message.y))
                if (this_squadron_dist < closest_squadron_dist):
                    closest_squadron = this_squadron
                    closest_squadron_dist = this_squadron_dist
        if (closest_squadron is not None):
            self.memory["squadron"] = closest_squadron

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
    
    # Prioritize fighting nearby enemies
    if len(enemies_nearby) > 0:
        # Find the nearest enemy ant
        angle_to_nearest_ant = self.angle_toward(self.nearest(enemies_nearby))

        # Squad members will bite!
        attackable_ants = self.attackable(include_teammates=False)
        if (len(attackable_ants) > 0 and (not self.memory["squad_leader"])):
            return("bite", {})
        
        # Squad leaders will block!
        if (len(attackable_ants) > 0 and self.memory["squad_leader"]):
            return("block", {})
        
        # Walk towards the nearest ant, if the angle is close enough
        if abs(angle_to_nearest_ant - self.rotation) < math.pi/2:
            return("walk", {})
        
        # Turn towards the nearest ant
        return("turn", {"rel_angle": angle_to_nearest_ant - self.rotation})

    # If we're in a squadron, find the newest message from that squadron
    if ((self.memory["squadron"] is not None) and (not self.memory["squad_leader"])):
        messages = self.receive()
        newest_message_coords = None
        newest_message_age = math.inf
        for message in messages:
            if (message.content.startswith("[") and message.content.endswith("]")):
                this_squadron = int(message.content[1:-1])
                if (this_squadron == self.memory["squadron"]):
                    if (message.age < newest_message_age):
                        newest_message_coords = (message.x, message.y)
                        newest_message_age = message.age

        # If we have a trail, follow it
        if (newest_message_coords is not None):
            # Turn towards the newest message
            angle_to_message = self.angle_toward(newest_message_coords)
            if abs(angle_to_message - self.rotation) > math.pi/8:
                return("turn", {"rel_angle": angle_to_message - self.rotation})
            else:
                return("walk", {})

    # Do a random-ish walk if no ants are nearby
    if (random.random() < 0.1):
        return("turn", {"rel_angle": ((random.random()-0.5)/8) * 2 * math.pi})
    else:
        return("walk", {})