"""
Author: CZMoodyDev
Usage:
-This bot is for use with Desktop Dungeons Enhanced Edition (Steam)
-Set prep_cost to preparation cost to accurately record profit
-Use a Goblin Tinker
-So far this has only been tested using Den of Danger
-Used with 1.5 Windowed mod on a 1920x1080 screen
"""

from PIL import ImageGrab, ImageOps, Image
import win32api, win32con
import pytesseract
from numpy import *
import numpy as np
import cv2
import time
from ScreenCaster import screenCast
from threading import Thread
from pynput import keyboard

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'

# User-set Globals
# -----------
x_pad = 8 #Pixels from left side of screen to first top-left pixel of game window
y_pad = 29 #Pixels from top of screen to first top-left pixel
number_of_runs = 0
prep_cost = 0
gold_brought_in = 27
bwThresh = 128 #Threshold for Black/White conversion of Gold counter

# Bot Globals
# ------------
tileIndex = {} #Keeps bad coordinates from being processed
queue = [] #Keeps coordinates to be processed
seen = {} #Manages coordinates already processed
wasSteppable = {} #Manages tiles stepped on for next phase of the run
wallList = {} #Manages walls seen
allowedClicks = [24445, 24335, 24480, 24590, 24661, 24801, 24806, 25556] #This is the image averages of a subsection of the conversion bar
gameFailureAverage = 2552
firstMove = True
blackSpaceAvg = 900
original_spot = '' #Starting point
running_avg = 0
run_num = 1
gold_sum = 0
escaped = 0
reporting = ''
transmute_scroll_count = 2
subdungeon_start = ''
subdungeon_tileIndex = {}
subdungeon_seen = {}
subQueue = []

# Image box constants
# ------------
gameScreen = (x_pad + 1, y_pad + 1, x_pad + 1199, y_pad + 899)
gameScreenSansSide = (x_pad + 1, y_pad + 1, x_pad + 871, y_pad + 899)
goldHundreds = (x_pad + 907, y_pad + 165, x_pad + 921, y_pad + 191)
goldTens = (x_pad + 921, y_pad + 165, x_pad + 935, y_pad + 191)
goldOnes = (x_pad + 935, y_pad + 165, x_pad + 950, y_pad + 191)
conversionBar = (x_pad + 969, y_pad + 775,x_pad + 1085, y_pad + 797)
priceTag = (x_pad + 993, y_pad + 564, x_pad + 1014, y_pad + 581)

# Screen point constants
# ------------
retireTab = (x_pad + 1095, y_pad + 845)
retireButton = (x_pad + 1071, y_pad + 782)
continueButton = (x_pad + 1009, y_pad + 840)
mainTab = (x_pad + 998, y_pad + 840)
nodeTavern = (x_pad + 579, y_pad + 543)
offPrompts = (x_pad + 43, y_pad + 459)
denOfDanger = (x_pad + 279, y_pad + 363)
shiftingPassages = (x_pad + 564, y_pad + 257)
selectDenOfDanger = (x_pad + 1055, y_pad + 744)
raceChooseGoblin = (x_pad + 696, y_pad + 141)
classChooseTinker = (x_pad + 249, y_pad + 523)
playButton = (x_pad + 1116, y_pad + 738)
firstTransmute = (x_pad + 1036, y_pad + 458)
secondScroll = (x_pad + 1090, y_pad + 458)
thirdScroll = (x_pad + 1150, y_pad + 458)
bigslotsix = (x_pad + 1036, y_pad + 730)
bigslotfive = (x_pad + 1036, y_pad + 675)
bigslotfour = (x_pad + 1036, y_pad + 618)
bigslotthree = (x_pad + 1036, y_pad + 566)
littleSlot = (x_pad + 1036, y_pad + 511)


def findChar():
    simpleSaveGrab(gameScreen, 'main.png')
    starting_location = findImage('Images/GoblinTinker.png', 'main.png')

    arrayX = starting_location[1]
    arrayY = starting_location[0]

    try:
        r_string = 'x' + str(int(floor(arrayX[0] / 45))) + 'y' + str(int(floor(arrayY[0] / 45)))
    except IndexError:
        r_string = 'Could not locate character'
        print(r_string)
    return r_string

def findImage(needle, haystack):
    img_rgb = cv2.imread(haystack)
    template = cv2.imread(needle)

    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .6
    loc = np.where(res >= threshold)
    return (loc[0], loc[1])

def simpleSaveGrab(box, imgName):
    im = ImageGrab.grab(box)
    im.save(imgName)

def simpleBWGrab(box, imgName):
    im = ImageGrab.grab(box)
    gray = im.convert('L')
    bw = np.asarray(gray).copy()

    bw[bw < 128] = 0  # Black
    bw[bw >= 128] = 255  # White
    imfile = Image.fromarray(bw)
    imfile.save(imgName)

def readGold():
    simpleBWGrab(goldHundreds, 'goldHundreds.png')
    simpleBWGrab(goldTens, 'goldTens.png')
    simpleBWGrab(goldOnes, 'goldOnes.png')
    try:
        ones = readGoldNumber('goldOnes.png')
        tens = readGoldNumber('goldTens.png') * 10
        hundreds = readGoldNumber('goldHundreds.png', limit=True) * 100
        goldCount = ones + tens + hundreds
    except TypeError:
        print("Failure to read Gold")
        goldCount = 27

    return goldCount

def readGoldNumber(im, limit=False):
    if limit:
        res = findImage('Images/gold1.png', im)
        arrayX = res[1]
        if len(arrayX) == 0:
            return 0
        else:
            return 1
    else:
        for i in range(0, 10):
            res = findImage('Images/gold' + str(i) + '.png', im)
            arrayX = res[1]
            if len(arrayX > 0):
                return i

def exit(gold):
    global running_avg
    global gold_sum
    global run_num

    clickStart()

    try:
        t_gold = int(gold) - (prep_cost + gold_brought_in)
        running_avg += 1
        gold_sum += t_gold
        avg = gold_sum / running_avg
        print('Run#' + str(run_num) + ' Haul = ' + str(t_gold) + ' Sum = ' + str(gold_sum) + ' Average = ' + str(avg))
    except ValueError:
        print("No gold added to average")

    run_num += 1
    time.sleep(0.5)
    quickExit(1)

def clickStart():
    starting_point = original_spot

    coordinates = processCoordinate(starting_point)
    x = coordinates[0]
    y = coordinates[1]

    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    leftClick()
    time.sleep(.1)

def quickExit(reporting):
    if reporting == 0:
        clickStart()
    clickElement(retireTab, .1)
    clickElement(retireButton, 3)
    clickElement(continueButton, 3)

def clickElement(element, delay):
    mousePos(element)
    leftClick()
    time.sleep(delay)

def processCoordinate(p):
    try:
        #p is formatted as x8y8
        p = p.split('y') #p is now (x8, 8)
        x = p[0].split('x') #x is now (x, 8)
        x = int(x[1]) #x is now 8
        y = int(p[1]) #y is now 8
    except IndexError:
        x = 0
        y = 0
    return (x, y)

def grab():
    box = conversionBar
    im = ImageOps.grayscale(ImageGrab.grab(box))
    a = array(im.getcolors())
    a = a.sum()
    return a

def makeMap():
    temp_map = {}
    for i in range(0, 20):
        for j in range(0, 20):
            temp_map['x' + str(i) + 'y' + str(j)] = ''

    return temp_map

def processCords():
    global firstMove
    global escaped

    cord = queue.pop()
    seen[cord] = 'y'

    coordinates = processCoordinate(cord)
    x = coordinates[0]
    y = coordinates[1]

    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    time.sleep(.15)

    if isClickable():
        firstMove = False
        leftClick()
        time.sleep(.05)
        clickElement(mainTab, .11)
        wallList["x" + str(x) + "y" + str(y)] = ""
        if lookForChar(x, y):
            wasSteppable["x" + str(x) + "y" + str(y)] = ""
            wallList.pop("x" + str(x) + "y" + str(y), None)
            clickElement(mainTab, .1)  # In case of boss discovery
            cord_n = 'x' + str(x) + 'y' + str(y - 1)
            cord_ne = 'x' + str(x + 1) + 'y' + str(y - 1)
            cord_e = 'x' + str(x + 1) + 'y' + str(y)
            cord_se = 'x' + str(x + 1) + 'y' + str(y + 1)
            cord_s = 'x' + str(x) + 'y' + str(y + 1)
            cord_sw = 'x' + str(x - 1) + 'y' + str(y + 1)
            cord_w  = 'x' + str(x - 1) + 'y' + str(y)
            cord_nw = 'x' + str(x - 1) + 'y' + str(y - 1)

            cords_to_check = [cord_n, cord_ne, cord_e, cord_se, cord_s, cord_sw, cord_w, cord_nw]

            for i in cords_to_check:
                if i not in seen:
                    if i in tileIndex:
                        if i not in queue:
                            queue.append(i)

def lootSubdungeons():
    exploredDungeons = 0
    openHiddenSubdungeons()
    visibleSubs = locateSubdungeons('images/subDungeon.png')
    while exploredDungeons < len(visibleSubs):
        enterSubdungeon(visibleSubs[exploredDungeons])

        exploredDungeons = exploredDungeons + 1

def enterSubdungeon(cord):
    global subdungeon_start
    global subdungeon_tileIndex
    global subdungeon_seen
    global subQueue

    coordinates = processCoordinate(cord)
    x = coordinates[0]
    y = coordinates[1]

    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    leftClick()
    time.sleep(.01)
    leftClick()
    time.sleep(.5)

    clickElement(mainTab, .11)

    subdungeon_start = findChar()
    subdungeon_tileIndex = makeMap()
    subdungeon_seen = {}
    subQueue = []

    if subdungeon_start == 'Could not locate character':
        while subdungeon_start == 'Could not locate character':
            subdungeon_start = findChar()

    if lookForGold('images/goldpile1.png') or lookForGold('images/goldpile2.png'):
        subQueue.append(subdungeon_start)

        while len(subQueue) != 0:
            time.sleep(.01)
            processSubCords()
        time.sleep(.5)

    exitSubdungeon()

def exitSubdungeon():
    coordinates = processCoordinate(subdungeon_start)
    x = coordinates[0]
    y = coordinates[1]

    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    leftClick()
    time.sleep(.01)
    leftClick()
    time.sleep(.5)


def processSubCords():
    cord = subQueue.pop()
    subdungeon_seen[cord] = 'y'

    coordinates = processCoordinate(cord)
    x = coordinates[0]
    y = coordinates[1]

    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    time.sleep(.15)

    if isClickable():
        leftClick()
        time.sleep(.05)
        clickElement(mainTab, .11)
        if lookForChar(x, y):
            clickElement(mainTab, .1)  # In case of sign discovery
            cord_n = 'x' + str(x) + 'y' + str(y - 1)
            cord_ne = 'x' + str(x + 1) + 'y' + str(y - 1)
            cord_e = 'x' + str(x + 1) + 'y' + str(y)
            cord_se = 'x' + str(x + 1) + 'y' + str(y + 1)
            cord_s = 'x' + str(x) + 'y' + str(y + 1)
            cord_sw = 'x' + str(x - 1) + 'y' + str(y + 1)
            cord_w  = 'x' + str(x - 1) + 'y' + str(y)
            cord_nw = 'x' + str(x - 1) + 'y' + str(y - 1)

            cords_to_check = [cord_n, cord_ne, cord_e, cord_se, cord_s, cord_sw, cord_w, cord_nw]

            for i in cords_to_check:
                if i not in subdungeon_seen:
                    if i in subdungeon_tileIndex:
                        if i not in subQueue:
                            subQueue.append(i)

def openHiddenSubdungeons():
    hiddenSubs = locateSubdungeons('images/hiddenDungeon.png')
    tryCounter = 0

    if len(hiddenSubs) > 0:
        while not tryCounter == len(hiddenSubs):
            hiddenCords = processCoordinate(hiddenSubs[tryCounter])

            tryCounter = tryCounter + 1
            x = hiddenCords[0]
            y = hiddenCords[1]
            cord_n = 'x' + str(x) + 'y' + str(y - 1)
            cord_ne = 'x' + str(x + 1) + 'y' + str(y - 1)
            cord_e = 'x' + str(x + 1) + 'y' + str(y)
            cord_se = 'x' + str(x + 1) + 'y' + str(y + 1)
            cord_s = 'x' + str(x) + 'y' + str(y + 1)
            cord_sw = 'x' + str(x - 1) + 'y' + str(y + 1)
            cord_w = 'x' + str(x - 1) + 'y' + str(y)
            cord_nw = 'x' + str(x - 1) + 'y' + str(y - 1)

            cords_to_check = [cord_n, cord_ne, cord_e, cord_se, cord_s, cord_sw, cord_w, cord_nw]

            for i in cords_to_check:
                if i in seen:
                    if i in wallList:
                        tryCounter = len(hiddenSubs)
                        transmuteWall(i)
                        time.sleep(1) #Sleep needed or the search for a subdungeon is too fast
                        break;



def transmuteWall(cord):
    global transmute_scroll_count
    global wallList
    transmute_scroll_count = transmute_scroll_count - 1

    #clickElement(firstTransmute, 1)

    coordinates = processCoordinate(cord)
    x = coordinates[0]
    y = coordinates[1]

    wallList.pop("x" + str(x) + "y" + str(y), None)
    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    dragUp((x_pad + (x * 45), y_pad + (y * 45)))
    time.sleep(.5)
    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    leftClick()
    time.sleep(.1)

def locateSubdungeons(img):
    dungeonLocations = {}

    simpleSaveGrab(gameScreen, 'main.png')
    img_rgb = cv2.imread('main.png')
    template = cv2.imread(img)

    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .95
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch collumns and rows
        r_string = 'x' + str(int(floor((pt[0] + 15) / 45))) + 'y' + str(int(floor((pt[1] + 15) / 45)))
        dungeonLocations[r_string] = 0

    return_cords = []

    for key in dungeonLocations:
        return_cords.append(key)

    return return_cords

def lookForGold(img):
    found = False
    simpleSaveGrab(gameScreenSansSide, 'main.png')
    img_rgb = cv2.imread('main.png')
    template = cv2.imread(img)

    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .9
    loc = np.where(res >= threshold)
    for pt in zip(*loc[::-1]):  # Switch columns and rows
        found = True

    return found

def findShops():

    shop_queue = locateSubdungeons('images/shop.png')

    if len(shop_queue) > 0:
        best_shop_cords = ''
        best_shop_price = 0

        while len(shop_queue) > 0:
            shop_check = shop_queue.pop()

            coordinates = processCoordinate(shop_check)
            x = coordinates[0]
            y = coordinates[1]

            mousePos((x_pad + (x * 45), y_pad + (y * 45)))
            leftClick()
            time.sleep(.5)

            try:
                price = int(readPriceTag())
            except ValueError:
                price = 0

            if price > 10:
                if price > best_shop_price:
                    best_shop_cords = shop_check
                    best_shop_price = price

            time.sleep(1)

        if best_shop_cords != '':
            stealItem(best_shop_cords)


    clickElement(mainTab, .2)



def stealItem(cords):
    global transmute_scroll_count
    coordinates = processCoordinate(cords)
    x = coordinates[0]
    y = coordinates[1]

    clickStart()
    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    dragUp((x_pad + (x * 45), y_pad + (y * 45)))

    #leftClick()
    #time.sleep(.1)
    clickElement(mainTab, .2)

    #if transmute_scroll_count == 2:
    #    scrollspot = thirdScroll
    #else:
    #    scrollspot = secondScroll

    #clickElement(scrollspot, .3)

    #mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    #leftClick()
    #time.sleep(.3)

    clickElement(firstTransmute, .2)
    transmute_scroll_count = transmute_scroll_count - 1
    clickElement(bigslotsix, .1)
    clickElement(bigslotfive, .1)
    clickElement(bigslotfour, .1)
    clickElement(bigslotthree, .1)
    clickElement(littleSlot, .1)
    if transmute_scroll_count == 0:
        clickElement(thirdScroll, .1)
    if transmute_scroll_count == 1:
        clickElement(secondScroll, .1)
    rightClick()
    time.sleep(.1)


def readPriceTag():
    simpleSaveGrab(priceTag, 'priceTag.png')

    text = pytesseract.image_to_string(Image.open('priceTag.png'))

    return text


def lookForChar(x, y):
    x_n = x_pad + (x * 45)
    y_n = y_pad + (y * 45)
    box = (x_n, y_n, x_n + 45,y_n + 45)
    simpleSaveGrab(box, 'dstTile.png')
    dst_location = findImage('Images/GoblinTinker.png', 'dstTile.png')

    arrayX = dst_location[1]

    if len(arrayX) == 0:
        return False
    else:
        return True

def isClickable():
    if grab() in allowedClicks:
        return True
    else:
        if firstMove == True:
            print('CRITICAL FAILURE')
            print(grab())
        return False

def getTileAvg(x, y):
    x_n = x_pad + (x * 45)
    y_n = y_pad + (y * 45)
    box = (x_n,y_n,x_n + 30,y_n+30)
    im = ImageOps.grayscale(ImageGrab.grab(box))
    a = array(im.getcolors())
    a = a.sum()
    return a

def leftClick():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

def rightClick():
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
    time.sleep(.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

def dragUp(cord):
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(2)

    win32api.SetCursorPos((cord[0], max(cord[1] - 80, 30)))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    time.sleep(.1)

def mousePos(cord):
    win32api.SetCursorPos((x_pad + cord[0], y_pad + cord[1]))

def get_cords():
    x, y = win32api.GetCursorPos()
    x = x - x_pad
    y = y - y_pad
    print(x,y)

def fullSingleRun():
    global original_spot
    global firstMove
    global seen
    global tileIndex
    global transmute_scroll_count
    global wallList
    transmute_scroll_count = 2
    firstMove = True

    tileIndex = makeMap()
    seen = {}
    time.sleep(1)
    wallList = {}

    original_spot = findChar()
    queue.append(original_spot)

    while len(queue) != 0:
        time.sleep(.01)
        processCords()
    time.sleep(.5)

    lootSubdungeons()
    time.sleep(.1)
    findShops()
    useUpTransmutes()
    time.sleep(2)
    rightClick()
    time.sleep(.1)
    if reporting == 'y':
        exit(readGold())
    else:
        quickExit(0)

def useUpTransmutes():
    wall_queue = []
    for i in wallList:
        if len(wall_queue) < transmute_scroll_count:
            wall_queue.append(i)
        else:
            break;

    for x in wall_queue:
        transmuteWall(x)
        time.sleep(1)

def setupRun():
    #Click off prompts
    clickElement(offPrompts, .1)
    clickElement(offPrompts, .1)
    clickElement(offPrompts, .1)

    #Tavern
    clickElement(nodeTavern, .1)

    #Den of Danger
    clickElement(denOfDanger, 2)

    #Select
    clickElement(selectDenOfDanger, .1)

    # Goblin
    clickElement(raceChooseGoblin, .1)

    # Tinker
    clickElement(classChooseTinker, .1)

    # Play
    clickElement(playButton, 3)


def reportEarnings(total):
    total_str = str(ceil(total))
    print('Done in ' + total_str + 's')
    print('Average run: ' + str(ceil(total / run_num)) + 's')
    total_min = total / 60
    gold_per_min = gold_sum / total_min
    print('Gold per minute = ' + str(floor(gold_per_min)))

def captureScreenVideo():
    dt = time.strftime("%Y%m%d-%H%M%S")
    screenCast.screenCast(dt, gameScreen[2], gameScreen[3], 10, gameScreen)

def keyboardListenerInit():
    # Collect events until released
    with keyboard.Listener(
            on_press=on_press,
            on_release=on_release) as listener:
        listener.join()

def main():
    global number_of_runs
    global reporting
    castScreen = input('Capture video? [y/n]: ')
    perpetual = input('Perpetual runs? [y/n]: ')
    reporting = input('Reporting? [y/n]: ')
    run_time = 1

    if perpetual == 'y':
        print("Press any key to interrupt run...")
        run_time = 100
        listener_thread = Thread(target=keyboardListenerInit)
        listener_thread.start()
    else:
        number_of_runs = int(input('How many runs?: '))

    if castScreen == 'y':
        thread = Thread(target = captureScreenVideo)
        thread.start()
    t0 = time.time() #Start Time

    while run_time:
        if not escaped:
            setupRun()
            fullSingleRun()
            time.sleep(3) #Maybe a 3 second sleep between runs will prevent issues
            number_of_runs = max(number_of_runs - 1, 0)
            if (number_of_runs == 0 and run_time == 1):
                run_time = 0
        else:
            break

    if reporting == 'y':
        t1 = time.time()  # End Time
        total = t1 - t0
        reportEarnings(total)

    pass

def on_press(key):
    global escaped
    try:
        escaped = 1
        print("Run interrupted. Finishing current run before ending...")
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    if escaped == 1:
        return False

if __name__ == '__main__':
    main()
    pass
