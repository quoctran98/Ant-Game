"""Define the classes for the battle and the ants.

"""

import random
import math
import uuid

class Battle():
    def __init__(self):
        self.ants = []
        self.bounds = (500, 500)

        self.game_tick = 0

        # Attacks and blocks to be resolved at the end of the tick
        self.attack_queue = []
        self.block_queue = []

        # Messages to be added to the list of messages at the end of the tick
        self.message_queue = []
        self.messages = [] # List of (x, y, team, message, game_tick)

    def new_message(self, ant, message):
        """Add a message to the message queue."""
        self.message_queue.append((ant, message, self.game_tick))

    def attack(self, attacker, damage, attack_range):
        """Add an attack to the attack queue to be resolved at the end of the tick."""
        self.attack_queue.append((attacker, damage, attack_range))
        return(True)
    
    def block(self, blocker, damage):
        """Add a block to the block queue to be resolved at the end of the tick."""
        self.block_queue.append((blocker, damage))
        return(True)
    
    def resolve_attacks(self):
        # Resolve the attacks after all ants have executed their antgorithms
        while len(self.attack_queue) > 0:
            attacker, damage, attack_range = self.attack_queue.pop(0)
            for ant in self.ants:
                if ant == attacker: # Make sure the ant isn't the attacker...
                    continue
                if (ant.x - attacker.x)**2 + (ant.y - attacker.y)**2 < attack_range**2:
                    # Check if this ant is in the block_queue
                    for blocker, block_damage in self.block_queue:
                        if blocker == ant:
                            # If the ant is blocking, the damage is reduced
                            damage -= block_damage
                            break
                    ant.suffer(damage, attacker.x, attacker.y)
        # Clear the block and attack queues (just to be safe)
        self.attack_queue = []
        self.block_queue = []

    def resolve_messages(self):
        """Add the message queue to the list of messages and remove old messages."""
        self.messages += self.message_queue
        self.message_queue = []
        # Messages expire after 10 ticks?
        self.messages = [m for m in self.messages if self.game_tick - m[2] < 10]

class Ant():
    def __init__(self, battle, team, 
                 stats_dict, init_position, antgorithm):
        
        # Basic ant info
        self.id = uuid.uuid4()
        self.team = team # blue or red
        self.alive = True

        # Combat and movement stats
        required_stats = ["health", "speed", "damage", "attack_range", "sense_range"]
        for s in required_stats:
            if s not in stats_dict:
                raise ValueError("Ant stats must include " + s)
            setattr(self, s, stats_dict[s])

        # Position and rotation
        self.x = init_position[0]
        self.y = init_position[1]
        self.rotation = init_position[2]

        # Attach the antgorithm
        self.antgorithm = antgorithm

        # Add the ant to the battle
        self.battle = battle
        battle.ants.append(self)

    def sense(self):
        """Return the position of all ants nearby."""
        ants_nearby = []
        for ant in self.battle.ants:
            # Make sure the ant isn't this ant...
            if ant == self:
                continue
            if (ant.x - self.x)**2 + (ant.y - self.y)**2 < self.sense_range**2:
                ants_nearby.append((ant.x, ant.y, ant.team))
        return(ants_nearby)
    
    def broadcast(self, message):
        """Broadcast a message to all nearby ants."""
        self.battle.new_message(ant=self, message=message)

    def walk(self, distance=None):
        """Move the ant forward in the direction it is facing."""
        # Default to moving the full speed
        if distance is None:
            distance = self.speed
        if distance > self.speed:
            distance = self.speed
        
        # Calculate the ant's new x and y positions
        new_x = self.x + distance * math.cos(self.rotation)
        new_y = self.y + distance * math.sin(self.rotation)

        # Make sure the ant doesn't walk off the screen
        if (new_x < 0) or (new_y < 0):
            return(False)
        elif (new_x > self.battle.bounds[0]) or (new_y > self.battle.bounds[1]):
            return(False)

        self.x = new_x
        self.y = new_y
        return(True)
    
    def turn(self, rel_angle):
        """Turn the ant by the given relative angle in radians."""
        self.rotation += rel_angle
        self.rotation %= 2 * math.pi
        return(True)
    
    def strafe(self, rel_angle, distance=None):
        """Strafe the ant toward the given relative angle in radians (at half speed)."""

        # Default to moving the half speed (can't strafe at full speed)
        if distance is None:
            distance = self.speed/2
        if distance > self.speed/2:
            distance = self.speed/2

        # Calculate the ant's new x and y positions
        self.x += distance * math.cos(self.rotation + rel_angle) / 2
        self.y += distance * math.sin(self.rotation + rel_angle) / 2
        return(True)
    
    def bite(self):
        """Bite any ants in front of the ant."""
        self.battle.attack(self, self.damage, self.attack_range)
        return(True)    
    
    def suffer(self, damage, attacker_x, attacker_y):
        """Take damage from an attack."""
        self.health -= abs(damage) # Just in case damage is negative
        if self.health <= 0:
            self.die()

        # Knock the ant back (unless it is already at the edge of the screen)
        new_x = self.x + 2 * (self.x - attacker_x)
        new_y = self.y + 2 * (self.y - attacker_y)
        if (new_x < 0) or (new_y < 0):
            self.x = self.x
        elif (new_x > self.battle.bounds[0]) or (new_y > self.battle.bounds[1]):
            self.y = self.y
        else:
            self.x = new_x
            self.y = new_y

        return(True)
    
    def die(self):
        """Kill the ant."""
        self.alive = False
        self.battle.ants.remove(self)
        return(True)
    
    def antgorithm(self):
        """The ant's antgorithm to be attached to the ant and run every tick."""
        return()
                