"""Define the classes for the battle and the ants.

"""

import pygame # For drawing the ants
import math
import random
import uuid
from copy import copy, deepcopy

class Battle():
    def __init__(self):
        self.ants = []
        self.bounds = (500, 500)

        self.game_tick = 0

        # Instructions to be resolved at the end of the tick
        self.instruction_queue = {} # {ant_id: (instruction, kwargs)}

        # Attacks and blocks to be resolved at the end of the tick
        self.attack_queue = {}
        self.damage_queue = {}
        self.block_queue = {}

        # Messages to be added to the list of messages at the end of the tick
        self.message_queue = []
        self.messages = [] # List of (x, y, team, message, game_tick)

    def new_message(self, ant, content):
        """Add a message to the message queue."""
        self.message_queue.append(Message(ant, content))

    def attack(self, attacker, damage):
        """Add an attack to the attack queue to be resolved at the end of the tick."""
        self.attack_queue[attacker] = damage # An ant should only exist once in the attack queue (at most)
        return(True)
    
    def block(self, blocker, damage):
        """Add a block to the block queue to be resolved at the end of the tick."""
        self.block_queue[blocker] = damage # An ant should only exist once in the block queue (at most)
        return(True)
    
    def resolve_instructions(self):
        """Resolve all instructions."""
        # Order doesn't really matter -- it's so antgorithms don't run on new tick information
        for ant_id, instruction in self.instruction_queue.items():
            ant = Ant.get_ant_by_id(self, ant_id)
            method, kwargs = instruction
            callable_method = getattr(ant, method)
            callable_method(**kwargs)
        self.instruction_queue = {} # Clear the instruction queue
    
    def resolve_attacks(self):
        """Resolve attacks and blocks, then deal damage that occurred during this tick."""
        # Resolve the attacks after all ants have executed their antgorithms
        for attacker, damage in self.attack_queue.items():
            ants_in_range = attacker.attackable(return_objects=True)
            ants_in_range = [ant for ant in ants_in_range if ant.team != attacker.team]
            if len(ants_in_range) > 0:
                # # Pick a random ant to attack (prefer opponents)
                # ant_to_attack = ants_in_range[random.randint(0, len(ants_in_range)-1)]
                # opponents_in_range = [ant for ant in ants_in_range if ant.team != attacker.team]
                ant_to_attack = ants_in_range[0] # Just attack the first ant in the list
                # Add the damage to the damage queue
                if ant_to_attack in self.damage_queue.keys():
                    self.damage_queue[ant_to_attack] += damage
                else:
                    self.damage_queue[ant_to_attack] = damage
        self.attack_queue = {} # Clear the attack queue

        # Now resolve the damage
        for ant, damage in self.damage_queue.items():
            # Subtract any blocked damage
            blocked_damage = self.block_queue[ant] if ant in self.block_queue.keys() else 0
            damage -= blocked_damage
            ant.suffer(damage)
        self.damage_queue = {} # Clear the damage queue

    def resolve_messages(self):
        """Add the message queue to the list of messages and remove old messages."""
        self.messages += self.message_queue
        for m in self.messages:
            m.age += 1
        self.messages = [m for m in self.messages if m.age < 10]
        self.message_queue = []

class Message():
    def __init__(self, ant, content):
        self.team = ant.team # We don't want the full ant object in the message!
        self.x = ant.x
        self.y = ant.y
        self.content = content
        self.age = 0

class Ant(pygame.sprite.Sprite):
    def __init__(self, battle, team, 
                 stats_dict, init_position, antgorithm):
        
        # Basic ant info
        self.id = uuid.uuid4()
        self.team = team # blue or red
        self.alive = True

        # Combat and movement stats
        required_stats = ["size", "health", "speed", "block_damage", "bite_damage", "bite_range", "bite_angle", "smell_range"]
        for s in required_stats:
            if s not in stats_dict:
                raise ValueError("Ant stats must include " + s)
            setattr(self, s, stats_dict[s])

        # Position and rotation
        self.x = init_position[0]
        self.y = init_position[1]
        self.rotation = init_position[2]

        # Memory
        self.memory = {}

        # Attach the antgorithm
        self.update = antgorithm

        # Add the ant to the battle
        self.battle = battle
        battle.ants.append(self)

        # Now let's deal with pygame stuff
        super(Ant, self).__init__()

        # Import and display the ant's body
        image_path = "./assets/" + team + "_ant.png"
        self.body_surf = pygame.image.load(image_path).convert_alpha()
        # Scale the ant to the hitbox size (maintain 3:5 aspect ratio)
        _hitbox_angle = math.atan(3/5)
        _surf_height = int(self.size * math.cos(_hitbox_angle)) * 2
        _surf_width = int(self.size * math.sin(_hitbox_angle)) * 2
        self.body_surf = pygame.transform.scale(self.body_surf, (_surf_width, _surf_height))

    @classmethod
    def get_ant_by_id(self, battle, id):
        this_ant = [ant for ant in battle.ants if ant.id == id]
        if len(this_ant) == 0:
            return(None)
        else:
            return(this_ant[0])
        
    def copy(self):
        """Return a copy of the ant."""
        return(copy(self))

    def attackable(self, include_teammates=False, include_enemies=True, return_objects=False):
        """Return a list of all ants that can be attacked (within bite_range and bite_angle)."""
        ants_attackable = []
        for ant in self.battle.ants:
            # Make sure the ant isn't this ant...
            if ant == self:
                continue
            if (ant.x - self.x)**2 + (ant.y - self.y)**2 < self.bite_range**2:
                # Check if the ant is in front of this ant
                angle_to_ant = math.atan2(self.x - ant.x, self.y - ant.y) % (2*math.pi)
                if abs(angle_to_ant - self.rotation) < self.bite_angle/2: # Divide by 2 b/c it's centered on the ant's rotation
                    ants_attackable.append(ant)
                # Give a tiny circle around the ant's center as a buffer (doesn't work well otherwise...)
                elif (ant.x - self.x)**2 + (ant.y - self.y)**2 < 1:
                    ants_attackable.append(ant)

        # Remove teammates or enemies if specified
        if not include_teammates:
            ants_attackable = [ant for ant in ants_attackable if ant.team != self.team]
        if not include_enemies:
            ants_attackable = [ant for ant in ants_attackable if ant.team == self.team]
        
        # Return list of Ant objects or (x, y, team) tuples
        if (return_objects):
            return(ants_attackable)
        else:
            return([(ant.x, ant.y, ant.team) for ant in ants_attackable])

    def sense(self, range=None, include_teammates=True, include_enemies=True, return_objects=False):
        """Return the position of all ants within a range (defaults to smell_range)."""
        
        # Default to sensing the full smell range
        if range is None:
            range = self.smell_range
        if range > self.smell_range:
            range = self.smell_range

        ants_nearby = []
        for ant in self.battle.ants:
            # Make sure the ant isn't this ant...
            if ant == self:
                continue
            if (ant.x - self.x)**2 + (ant.y - self.y)**2 < range**2:
                ants_nearby.append(ant)

        # Remove teammates or enemies if specified
        if not include_teammates:
            ants_nearby = [ant for ant in ants_nearby if ant.team != self.team]
        if not include_enemies:
            ants_nearby = [ant for ant in ants_nearby if ant.team == self.team]

        # Return list of Ant objects or (x, y, team) tuples
        if (return_objects):
            return(ants_nearby)
        else:
            return([(ant.x, ant.y, ant.team) for ant in ants_nearby])
    
    def broadcast(self, message):
        """Broadcast a message to all nearby ants."""
        self.battle.new_message(ant=self, content=message)

    def receive(self, range=None):
        """Receive all messages within range."""

        # Default to receiving in the full smell range
        if range is None:
            range = self.smell_range
        if range > self.smell_range:
            range = self.smell_range

        # I don't like this because you can cheat, but who cares!
        messages = [m for m in self.battle.messages if self.distance_to((m.x, m.y)) < range]
        return(messages)

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
        # Add to the queue so combat instructions are resolved at the end of the tick
        self.battle.attack(self, self.bite_damage)
        return(True)
    
    def block(self):
        """Block incoming attacks."""
        # Add to the queue so combat instructions are resolved at the end of the tick
        self.battle.block(self, self.block_damage)
        return(True)
    
    def suffer(self, damage):
        """Take damage from an attack."""
        self.health -= abs(damage) # Just in case damage is negative
        if self.health <= 0:
            self.die()

        # # Knock the ant back (unless it is already at the edge of the screen)
        # new_x = self.x + 2 * (self.x - attacker_x)
        # new_y = self.y + 2 * (self.y - attacker_y)
        # if (new_x < 0) or (new_y < 0):
        #     self.x = self.x
        # elif (new_x > self.battle.bounds[0]) or (new_y > self.battle.bounds[1]):
        #     self.y = self.y
        # else:
        #     self.x = new_x
        #     self.y = new_y

        return(True)
    
    def die(self):
        """Kill the ant."""
        self.alive = False
        self.battle.ants.remove(self)
        return(True)
    
    def update(self):
        """The ant's antgorithm to be attached to the ant and run every tick."""
        return()
                
    # Helper functions to make writng antgorithms easier!
    def nearest(self, list_of_coords):
        """Return the coordinates of the nearest ant from a list of coordinates (output of self.sense())."""
        nearest_ant = min(list_of_coords, key=lambda x: (x[0] - self.x)**2 + (x[1] - self.y)**2)
        return(nearest_ant)
    
    def distance_to(self, target):
        """Return the distance to the given target (x,y)."""
        dx = self.x - target[0]
        dy = self.y - target[1]
        distance = math.sqrt(dx**2 + dy**2)
        return(distance) 

    def angle_toward(self, target):
        """Return the absulte angle toward the given target (x,y)."""
        dx = self.x - target[0]
        dy = self.y - target[1]
        angle = math.atan2(dy, dx) + math.pi % (2*math.pi) # Weird pygame coordinate system stuff...
        return(angle)
    
    def near_bounds(self, buffer=None):
        """Return True if the ant is within the given buffer of the edge of the battle. Defaults to self.size."""
        if buffer is None:
            buffer = self.size
        return(self.x < buffer or self.x > self.battle.bounds[0] - buffer or self.y < buffer or self.y > self.battle.bounds[1] - buffer)
