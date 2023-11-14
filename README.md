# Ant-Game

# Antgorithm API (Ant Programming Interface) Guide

## Introduction

To play each player will write an antgorithm to be implemented by each ant in their army. Each antgorithm is, at its core, just a function run every game tick that returns an instruction for that ant. 

Antgorithms can access various properties and methods of the ant class. They can sense other ants, broadcast messages, recieve messages, know their location, and return instructions to move or attack.

## Turn Structure

Each game tick, the following steps are performed:

1. Each ant runs its antgorithm and returns an instruction. Movement instructions are executed immediately, while combat instructions are queued for later.

2. Once, all ants have run their antgorithms, combat instructions are executed. Ants take damage if they are attacked, unless they are blocking the attack.

3. Ants that have died are removed from the game.

4. 

## `Ant` Attributes

### Basic Information

`battle` **(Battle)**: the battle that the ant is a part of (see `Battle` below)

`team` **(string)**: the name (color) of the team that the ant is a part of

`alive` **(boolean)**: whether or not the ant is alive

### Position

`x` **(float)**: the x coordinate of the ant in pixels (0 is the left side of the screen)

`y` **(float)**: the y coordinate of the ant in pixels (0 is the top of the screen)

`rotation` **(float)**: the rotation of the ant in radians (0 is facing right)

### Combat Stats

`health` *(float)*: the current health of the ant

`speed` *(float)*: the speed of the ant in pixels per tick

`attack` *(float)*: the amount of damage the ant deals when attacking

`attack_range` *(float)*: the range of the ant's attack in pixels

`sense_range` *(float)*: the range that the ant can use the `sense` method in pixels

## `Ant` Methods

### Sensing and Messaging

*Ants can't see very well! Their primary method of sensing is by feeling ants next to them. They can also communicate with nearby ants by secreting pheromones that other ants can sense, but this message can be dectected by enemy ants as well!*

*These are the ants' only methods of communication, but they can be called upon as many times as needed during the ant's turn.*

`sense()` *(list of (float: x, float: y, str: team))*: returns a list of all ants within the ant's `sense_range` that are alive. Each tuple in the list contains the x and y coordinates of the ant, as well as the team that the ant is on.

`broadcast(str: message)` *(bool)*: broadcasts a message at the ant's current location. The message remains for a certain number of game ticks before disappearing. Returns `True` if the message was successfully broadcasted, and `False` otherwise.

`receive()` *(list of (float: x, float: y, str: team, str: message))*: returns a list of all messages within the ant's `sense_range`. Each tuple in the list contains the x and y coordinates of the message, the team of the ant that broadcasted the message, and the message itself.

### Movement and Combat

*The goal of each antgorithm is to provide an instruction for the ant to move or to fight! Instead of calling these methods directly, the antgorithm should return a method name (and a kwargs dictionary if necessary) that will be called by the game engine.*

`walk(float: distance=None)` *(bool)*: moves the ant forward by the specified distance (in pixels), up to the ant's `speed`. If no distance is specified, the ant will move forward by its `speed`.

`turn(float: rel_angle)` *(bool)*: turns the ant by the specified angle (in radians) (0 is forward, positive is counterclockwise).

`strafe(float: rel_angle, float: distance=None)` *(bool)*: moves the ant toward the specified angle (in radians) (0 is forward, positive is counterclockwise) by the specified distance (in pixels), up to *half* the ant's `speed`. If no distance is specified, the ant will move forward by half its `speed`.

`bite()` *(bool)*: attacks any ants within the ant's `attack_range` and deals the ant's `attack` damage to them.

`block()` *(bool)*: blocks any attacks that hit the ant this turn.