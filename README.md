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

#### Plans to Address Cons
The bot comes with some reporting tools built in. Namely, the most intuitive way to evaluate its effectiveness is gold-per-minute (gpm). Right now it nabs about 5 - 6 gpm. To put that into perspective, I can get about 650 gold in about 2 - 3 minutes of play time. Needless to say, Version 1 is the bare minimum for a passably profitable bot.

1. It's mostly the rampant time.sleeps() and image scans that cause the time hang-ups.
    1. Image scans in the readGold() function might be avoidable if I can ever get tesseract to learn the gold counter font properly
    2. As for some of the sleeps...if a click doesn't sleep long enough, a fail condition can sneak up on the bot. I'll have to do more testing to mitigate the sleeps.
2. The Tinker has 2 transmutation seals. One of which can be used to open up a subdungeon and another that can convert an item or wall into gold. The subdungeon with all the gold piles + the black market preparation (maybe) could make for some pretty coin. It also has a translocation seal so the Tinker can steal an expensive item and then transmute it for gold (only worth it if the item exceeds 11 gold in value)
3. I don't plan to address this.
4. I want to find a way to efficiently ignore wall tiles. There don't seem to be too many options here though. I'm toying with 1 idea
    1. One is to do a read of the 9x9 block at the center of a click and image search for tiles to get all tile locations. Then I can just add tile locations into the queue (if they haven't been seen before, of course). That cuts down on imaging a loooot.

### Future Improvements Wishlist
* Speed up map traversal - Version 1.5
* Make use of all resources - Version 1.5
* Reduce lag in between runs - Version 1.5
* Introduce a Den of Danger farming mode that focuses on killing the boss - Version 2

### Version 1 Video
https://www.youtube.com/watch?v=04jKrCTWsSQ

