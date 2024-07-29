# DesktopDungeonBot
Fun little side project made with Python.

A gold farm bot for Desktop Dungeons Enhanced Edition

## Version 1
======
### Features
* The bot can successfully (usually always) navigate all tiles safely until it can no longer traverse any tiles
* The bot loops the specified number of times (number_of_runs)
* The bot should work with any 1920x1080 screen

### How it works
The bot takes advantage of the side panel changes on hover. Whereas if you hover over an enemy, the side panel will change to show battle calculations. It is only unsafe to click on an enemy (especially since you start at level 1). So the bot checks to see if the image average of a grayscaled box pulled from the middle of the conversion bar is within a set of values (hard-coded, unfortunately). If it is not, the bot determines it is unsafe to click and moves on. For all safe spaces that are not walls, it adds every adjacent tile to a queue and processes them one by one if it has not seen the tile before. The bot determines it clicked on a wall if it is not in the destination tile after it has clicked on it.

#### Implementation Pros
1. It does the job it was designed to do. All profit is incidental from map navigation (i.e. gold piles stepped on)

#### Implementation Cons
1. It's slowwwwwwwwwwww
2. It does not take full advantage of resources
3. It forces you to be a Goblin Tinker (Though I think this is the most profitable choice)
4. It checks every single non-blackspace tile

I have no plans to edit this project in the future, it was fun to work on at the time.
