"""
Author: CZMoodyDev
Usage:
-This bot is for use with Desktop Dungeons Enhanced Edition (Steam)
-Set prep_cost to preparation cost to accurately record profit
-Use a Goblin Tinker
-So far this has only been tested using Den of Danger
-Used with 1.5 Windowed mod on a 1920x1080 screen
"""

from PIL import Image, ImageChops, ImageGrab, ImageOps, ImageFilter
import win32api, win32con
import pytesseract
from numpy import *
import numpy as np
import cv2
import time

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'

# User-set Globals
# -----------
x_pad = 8 #Pixels from left side of screen to first top-left pixel of game window
y_pad = 29 #Pixels from top of screen to first top-left pixel
number_of_runs = 10
prep_cost = 0
gold_brought_in = 27
bwThresh = 128 #Threshold for Black/White conversion of Gold counter

# Bot Globals
# ------------
tileIndex = {} #Keeps bad coordinates from being processed
queue = [] #Keeps coordinates to be processed
seen = {} #Manages coordinates already processed
allowedClicks = [24445, 24335, 24590, 24661, 24801, 24806] #This is the image averages of a subsection of the conversion bar
firstMove = True
blackSpaceAvg = 900
original_spot = '' #Starting point
running_avg = 0
run_num = 1
gold_sum = 0

# Image box constants
# ------------
gameScreen = (x_pad + 1, y_pad + 1, x_pad + 1199, y_pad + 899)
goldHundreds = (x_pad + 907, y_pad + 165, x_pad + 921, y_pad + 191)
goldTens = (x_pad + 921, y_pad + 165, x_pad + 935, y_pad + 191)
goldOnes = (x_pad + 935, y_pad + 165, x_pad + 950, y_pad + 191)
conversionBar = (x_pad + 969, y_pad + 775,x_pad + 1085, y_pad + 797)


# Screen point constants
# ------------
retireTab = (x_pad + 1095, y_pad + 845)
retireButton = (x_pad + 1071, y_pad + 782)
restartButton = (x_pad + 814, y_pad + 818)
mainTab = (x_pad + 998, y_pad + 840)

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
    threshold = .8
    loc = np.where(res >= threshold)
    return (loc[0], loc[1])

def simpleSaveGrab(box, imgName):
    im = ImageGrab.grab(box)
    im.save(imgName)

def readGold():
    simpleSaveGrab(goldHundreds, 'goldHundreds.png')
    simpleSaveGrab(goldTens, 'goldTens.png')
    simpleSaveGrab(goldOnes, 'goldOnes.png')

    ones = readGoldNumber('goldOnes.png')
    tens = readGoldNumber('goldTens.png') * 10
    hundreds = readGoldNumber('goldHundreds.png', limit=True) * 100

    return ones + tens + hundreds

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

def trim(im):
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        return im.crop(bbox)

def exit(gold):
    global running_avg
    global gold_sum
    global run_num

    starting_point = original_spot
    print('Going back to ' + starting_point)

    coordinates = processCoordinate(starting_point)
    x = coordinates[0]
    y = coordinates[1]

    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    leftClick()

    running_avg += 1
    try:
        t_gold = int(gold) - (prep_cost + gold_brought_in)
    except ValueError:
        t_gold = 0 #Sometimes Tesseract doesn't read well

    gold_sum += t_gold
    avg = gold_sum / running_avg
    print('Run#' + str(run_num) + ' Haul = ' + str(t_gold) + ' Sum = ' + str(gold_sum) + ' Average = ' + str(avg))

    run_num += 1
    time.sleep(0.5)

    clickElement(retireTab, .1)
    clickElement(retireButton, 3)
    clickElement(restartButton, 3)

def clickElement(element, delay):
    mousePos(element)
    leftClick()
    time.sleep(delay)

def processCoordinate(p):
    #p is formatted as x8y8
    p = p.split('y') #p is now (x8, 8)
    x = p[0].split('x') #x is now (x, 8)
    x = int(x[1]) #x is now 8
    y = int(p[1]) #y is now 8
    return (x, y)

def grab():
    box = conversionBar
    im = ImageOps.grayscale(ImageGrab.grab(box))
    a = array(im.getcolors())
    a = a.sum()
    return a

def makeMap():
    for i in range(0, 20):
        for j in range(0, 20):
            tileIndex['x' + str(i) + 'y' + str(j)] = ''

def processCords():
    global firstMove
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
        clickElement(mainTab, .1)

        if lookForChar(x, y):
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
    firstMove = True

    makeMap()
    seen = {}
    time.sleep(1)

    original_spot = findChar()
    queue.append(original_spot)

    while len(queue) != 0:
        time.sleep(.01)
        processCords()
    gold = readGold()
    time.sleep(.5)
    exit(gold)

def reportEarnings(total):
    total_str = str(ceil(total))
    print('Done in ' + total_str + 's')
    print('Average run: ' + str(ceil(total / number_of_runs)) + 's')
    total_min = total / 60
    gold_per_min = gold_sum / total_min
    print('Gold per minute = ' + str(floor(gold_per_min)))

def main():
    t0 = time.time() #Start Time

    while (run_num != number_of_runs + 1):
        fullSingleRun()
        time.sleep(3) #Maybe a 3 second sleep between runs will prevent issues

    t1 = time.time() #End Time
    total = t1 - t0
    reportEarnings(total)
    pass


if __name__ == '__main__':
    main()