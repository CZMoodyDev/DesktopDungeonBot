from PIL import ImageGrab
import os
import time

# Globals
# -----------
x_pad = 7
y_pad = 28

def screenGrab():
    box = (x_pad+1, y_pad+1, x_pad+1199, y_pad+899)
    im = ImageGrab.grab(box)
    im.save(os.getcwd() + '\\full_snap__' + str(int(time.time())) +
'.png', 'PNG')

def main():
    screenGrab()

if __name__ == '__main__':
    main()