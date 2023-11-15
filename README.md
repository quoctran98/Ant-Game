# Ant-Game

# Antgorithm API (Ant Programming Interface) Guide

## Introduction

To play each player will write an antgorithm to be implemented by each ant in their army. Each antgorithm is, at its core, just a function run every game tick that returns an instruction for that ant. 

Antgorithms can access various properties and methods of the ant class. They can sense other ants, broadcast messages, recieve messages, know their location, and return instructions to move or attack.

## Turn Structure

Each game tick, the following steps are performed:

1. Each ant runs its antgorithm and returns an instruction (an `Ant` method name and a kwargs dictionary). These instructions are stored in a queue.

2. All instructions are resolved. Movement instructions are executed in the order they were received, and combat instructions (`bite` and `block`) are stored in a queue.

3. Combat instructions are resolved. Damage for each `bite` instruction is calculated (an ant can be attacked by multiple ants in a single turn). Damage for each `block` instruction executed by a defending ant is subtracted from the total damage dealt to that ant.

4. Ants take damage and die if their health reaches 0.

## `Ant` Attributes

### Basic Information

`battle` *(Battle)*: the battle that the ant is a part of (see `Battle` below)

`team` *(string)*: the name (color) of the team that the ant is a part of

`alive` *(boolean)*: whether or not the ant is alive

### Position

`x` *(float)*: the x coordinate of the ant in pixels (0 is the left side of the screen)

`y` *(float)*: the y coordinate of the ant in pixels (0 is the top of the screen)

`rotation` *(float)*: the rotation of the ant in radians (0 is facing right)

### General Stats

`size` *(float)*: the radius of the ant's circular hitbox in pixels

`health` *(float)*: the current health of the ant

`speed` *(float)*: the speed of the ant in pixels per tick

`block_damage` *(float)*: the amount of damage the ant negates when blocking

`bite_damage` *(float)*: the amount of damage the ant deals when biting

`bite_range` *(float)*: the range of the ant's bite in pixels

`bite_angle` *(float)*: the angle of the ant's bite in radiants (centered on the ant's rotation)

`smell_range` *(float)*: the range that the ant can use the `sense` method in pixels

### Memory

`memory` *(dict)*: a dictionary that can be used to store information between turns

## `Ant` Methods

### Sensing and Messaging

*Ants can't see very well! Their primary method of sensing is by feeling ants next to them. They can also communicate with nearby ants by secreting pheromones that other ants can sense, but this message can be dectected by enemy ants as well!*

*These are the ants' only methods of communication, but they can be called upon as many times as needed during the ant's turn.*

`attackable(bool: include_teammates=False, include_enemies=True)` *(list of (float: x, float: y, str: team))*: returns a list of all ants within the ant's `bite_range` and `bite_angle` that are alive. Each tuple in the list contains the x and y coordinates of the ant, as well as the team that the ant is on.

`sense(float: range=None, bool: include_teammates=False, include_enemies=True)` *(list of (float: x, float: y, str: team))*: returns a list of all ants within `range` (defaults to the maximum of `smell_range`). Each tuple in the list contains the x and y coordinates of the ant, as well as the team that the ant is on.

`broadcast(str: message)` *(bool)*: broadcasts a message at the ant's current location. The message remains for a certain number of game ticks before disappearing. Returns `True` if the message was successfully broadcasted, and `False` otherwise.

`receive(float: range=None)` *(Message)*: returns a list of all messages within `range` (defaults to the maximum of `smell_range`). Each tuple in the list contains the x and y coordinates of the message, the team of the ant that broadcasted the message, and the message itself.

### Movement and Combat

*The goal of each antgorithm is to provide an instruction for the ant to move or to fight! Instead of calling these methods directly, the antgorithm should return a method name (and a kwargs dictionary) that will be called by the game engine.*

`walk(float: distance=None)` *(bool)*: moves the ant forward by the specified distance (in pixels), up to the ant's `speed`. If no distance is specified, the ant will move forward by its `speed`.

`turn(float: rel_angle)` *(bool)*: turns the ant by the specified angle (in radians) (0 is forward, positive is counterclockwise).

`strafe(float: rel_angle, float: distance=None)` *(bool)*: moves the ant toward the specified angle (in radians) (0 is forward, positive is counterclockwise) by the specified distance (in pixels), up to *half* the ant's `speed`. If no distance is specified, the ant will move forward by half its `speed`.

`bite()` *(bool)*: attacks any ants within the ant's `attack_range` and deals the ant's `attack` damage to them.

`block()` *(bool)*: blocks any attacks that hit the ant this turn.

### Helper Methods

*These methods are provided to make writing antgorithms easier, but they are not required.*

`nearest(list of tuple of (float: x, float: y): list_of_coords)` *(tuple of (float: x, float: y))*: returns the coordinates of the target that is closest to the ant. Outputs of `sense` and `receive` can be used as the input.

`distance_to(tuple of (float: x, float: y): target)` *(float)*: returns the distance between the ant and the specified point (in pixels)

`angle_toward(tuple of (float: x, float: y): target)` *(float)*: returns the absolute angle between the ant and the specified point (in radians)

`near_bounds(float: buffer=None)` *(bool)*: returns `True` if the ant is within the specified buffer (in pixels) of the edge of the screen, and `False` otherwise. If no buffer is specified, the default buffer is the ant's `size`.
