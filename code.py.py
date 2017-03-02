from PIL import ImageGrab
import os
import time
import win32api, win32con
from PIL import ImageOps
from numpy import *
import numpy as np
import cv2
import string
import random

# Globals
# -----------
x_pad = 8
y_pad = 29

tileIndex = {}
queue = []
seen = {}
allowedClicks = [24445, 24335, 24590, 24661]

#def findStart():
#    box = (x_pad+1, y_pad+1, x_pad+1199, y_pad+899)
#    im = ImageGrab.grab(box)
#    im.save('main.png')
#    image = cv2.imread('main.png')
#    template = cv2.imread("GoblinTinker.png")
#    result = cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)
#    a = np.unravel_index(result.argmax(), result.shape)
#    return 'x' + str(int(ceil(a[0] % 45))) + 'y' + str(int(ceil(a[1] % 45)))

def findStart():
    box = (x_pad + 1, y_pad + 1, x_pad + 1199, y_pad + 899)
    im = ImageGrab.grab(box)
    im.save('main.png')

    img_rgb = cv2.imread('main.png')
    template = cv2.imread('GoblinTinker.png')
    w, h = template.shape[:-1]

    res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
    threshold = .8
    loc = np.where(res >= threshold)

    arrayY = loc[0]
    arrayX = loc[1]

    r_string = 'error'

    try:
        r_string = 'x' + str(int(floor(arrayX[0] / 45))) + 'y' + str(int(floor(arrayY[0] / 45)))
    except IndexError:
        print('Done early')

    return r_string


def grab():
    box = (977,804,1093,826)
    im = ImageOps.grayscale(ImageGrab.grab(box))
    a = array(im.getcolors())
    a = a.sum()
    return a

def makeMap():
    for i in range(0, 20):
        for j in range(0, 20):
            tileIndex['x' + str(i) + 'y' + str(j)] = ''

def processCord():
    cord = queue.pop()
    wtg = cord
    print('Processing ' + cord)
    seen[cord] = 'y'

    cord = cord.split('y')
    x = cord[0].split('x')
    x = int(x[1])
    y = int(cord[1])

    mousePos((x_pad + (x * 45), y_pad + (y * 45)))
    time.sleep(.1)
    #print(str(x_pad + (x * 45))+ str(y_pad + (y * 45)))
    if isClickable(x, y):
        leftClick()
        time.sleep(.05)
        resetClick()

        if wtg == findStart():
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

def resetClick():
    mousePos((1006, 869))
    leftClick()
    time.sleep(.01)


def isClickable(x, y):
    a = getTile(x, y)
    if a == 900:
        return False
    #print(a)
    print(grab())
    return grab() in allowedClicks

def getTile(x, y):
    x_n = x_pad + (x * 45)
    y_n = y_pad + (y * 45)
    box = (x_n,y_n,x_n + 30,y_n+30)
    im = ImageOps.grayscale(ImageGrab.grab(box))
    a = array(im.getcolors())
    a = a.sum()
    #print(a)
    return a

def leftClick():
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(.1)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    print("Click.") #DEBUG

def doubleClick():
    leftClick()
    leftClick()

def mousePos(cord):
    win32api.SetCursorPos((x_pad + cord[0], y_pad + cord[1]))

def get_cords():
    x, y = win32api.GetCursorPos()
    x = x - x_pad
    y = y - y_pad
    print(x,y)

def startGame():
    #Click Off Menus
    mousePos((42, 406))
    leftClick()
    time.sleep(.1)
    leftClick()
    time.sleep(.1)
    leftClick()
    time.sleep(.1)

    #Tavern
    mousePos((604, 529))
    leftClick()
    time.sleep(.1)

    #Den of Danger
    mousePos((276, 367))
    leftClick()
    time.sleep(1)

    #Select
    mousePos((1039, 743))
    leftClick()
    time.sleep(.1)

    #Tinker
    mousePos((239, 533))
    leftClick()
    time.sleep(.1)

    #Goblin
    mousePos((700, 152))
    leftClick()
    time.sleep(.1)

    #Transmutation Scroll
    #mousePos((111, 278))
    #leftClick()
    #time.sleep(.1)

    #Gold Pile
    mousePos((505, 759))
    leftClick()
    time.sleep(.1)

    #Play
    mousePos((1109, 745))
    leftClick()
    time.sleep(.1)

def main():
    startGame()
    makeMap()
    time.sleep(1)
    queue.append(findStart())
    while len(queue) != 0:
        time.sleep(.01)
        processCord()
    findStart()
    pass

if __name__ == '__main__':
    main()
