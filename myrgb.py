'''
MyRBG - Prototype RGB scripts.

Project: https://gitlab.com/FatCatX/myrgb

Uses
- OpenRGB server: https://gitlab.com/CalcProgrammer1/OpenRGB
- OpenRGB python: https://github.com/jath03/openrgb-python
'''

import time
import math
import random
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType

MAX_FPS = 30  # Maximium changes per second
COLOR_CYCLE = 1 # number of color cycles (positive, can be less than 1)
COLOR_SPEED = 30  # degrees of hue per second (positive or negative)
BREATH_SPEED = math.pi / 3  # radians per second

WAIT = 1.0  # Duration in seconds to wait for OpenRGB.  OpenRGB crashes on some calls without it.
PAUSE_DELTA = 0.015  # Increments of 15ms.

BLACK = RGBColor(0, 0, 0)
RED = RGBColor(255, 0, 0)
GREEN = RGBColor(0, 255, 0)
BLUE = RGBColor(0, 0, 255)
YELLOW = RGBColor(255, 255, 0)
CYAN = RGBColor(0, 255, 255)
MAGENTA = RGBColor(255, 0, 255)
WHITE = RGBColor(255, 255, 255)

def main():
    client = OpenRGBClient()
    printInfo(client.devices)

    for device in client.devices:
       device.set_mode('Direct')
    # time.sleep(WAIT)
    client.clear()
    time.sleep(WAIT)

    # client.load_profile('basic.orp')
    # client.show()

    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    ledStrip = mobo[0].zones[1]
    ledStrip.resize(42)

    # runRandom(client)
    # runRainbow(client)
    # runBreathing(client)
    # runClock(client)
    runSpots(client)

def printInfo(devices):
    for device in devices:
        print('Device[{}]'.format(device.device_id))
        print(device.name)
        for zone in device.zones:
            print('  zone[{}] {}, leds: {}'.format(zone.id, zone.name, len(zone.leds)))
        print()

def runRandom(client):
    running = True
    while running:
        device = client.devices[random.randrange(len(client.devices))]
        i = random.randrange(len(device.colors))
        device.colors[i] = randomColor()
        device.show()
        
        limitFPS()

def runRainbow(client):
    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    rams = client.get_devices_by_type(DeviceType.DRAM)
    gpus = client.get_devices_by_type(DeviceType.GPU)
    cpus = client.get_devices_by_type(DeviceType.COOLER)
    ledStrip = mobo[0].zones[1]
    mbZone = mobo[0].zones[2]

    gpus[0].set_color(WHITE)

#    chase = cpus[0].modes[5]
#    chase.speed = 1
#    cpus[0].set_mode(chase)
#    time.sleep(PAUSE)
    
    running = True
    while running:
        t = time.time()

        drawRainbow(ledStrip, t, 0, 135, 0, 21, value = 20)
        drawRainbow(ledStrip, t, 180, 315, 21, 42, value = 20)
        ledStrip.show()

        drawOneColor(mbZone, rainbowColor(t, [140]), 0, 1)
        mbZone.show()

        drawOneColor(cpus[0], rainbowColor(t, [110], value = 75), 1, 3)
        cpus[0].show()

        drawRainbow(rams[0], t, 80, -5)
        rams[0].show()
        drawRainbow(rams[1], t, 75, -10)
        rams[1].show()

        limitFPS()

def runBreathing(client):
    MIN_SAT = 50
    MAX_SAT = 100

    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    cpus = client.get_devices_by_type(DeviceType.COOLER)
    rams = client.get_devices_by_type(DeviceType.DRAM)
    gpus = client.get_devices_by_type(DeviceType.GPU)
    ledStrip = mobo[0].zones[1]

    hue = None
    running = True
    while running:
        t = time.time()

        # Pick a new color
        val = breathValue(t, [0])
        if (hue == None) or (val < 0.01):
            hue = 360 * random.random()
            sat = random.uniform(MIN_SAT, MAX_SAT)

        drawOneColor(cpus[0], breathColor(t, [0], hue, sat), 1, 2)
        drawOneColor(cpus[0], breathColor(t, [50], hue, sat), 2, 3)
        cpus[0].show()

        drawOneColor(rams[0], breathColor(t, [60], hue, sat))
        rams[0].show()
        drawOneColor(rams[1], breathColor(t, [70], hue, sat))
        rams[1].show()

        drawOneColor(gpus[0], breathColor(t, [80], hue, sat))
        gpus[0].show()

        drawOneColor(ledStrip, breathColor(t, [90], hue, sat, 0.2), 0, 21)
        drawOneColor(ledStrip, breathColor(t, [100], hue, sat, 0.2), 21, 42)
        # drawOneColor(ledStrip, breathColor(t, [180], hue, sat), 21, 42)
        ledStrip.show()

        limitFPS()

def runClock(client):
    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    ledStrip = mobo[0].zones[1]

    running = True
    while running:
        t = time.localtime(time.time())
        hour = t[3]
        minute = t[4]
        second = t[5]
        if hour > 12:
            hour -= 12
        BG_COLOR = RGBColor(0, 0, 60)
        drawOneColor(ledStrip, BG_COLOR)
        drawPos(ledStrip, 90 - 30 * hour, MAGENTA)
        drawPos(ledStrip, 90 - 6 * minute, YELLOW)
        drawPos(ledStrip, 90 - 6 * second, CYAN)
        ledStrip.show()
        
        limitFPS(5)

NUM_SPOTS = 6
MIN_SPOT_SIZE = 3
MAX_SPOT_SIZE = 60
MIN_SPOT_SPEED = 200
MAX_SPOT_SPEED = -200
def runSpots(client):
    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    cpus = client.get_devices_by_type(DeviceType.COOLER)
    rams = client.get_devices_by_type(DeviceType.DRAM)
    ledStrip = mobo[0].zones[1]

    spots = [()] * NUM_SPOTS
    for i in range(NUM_SPOTS):
        size = random.uniform(MIN_SPOT_SIZE, MAX_SPOT_SIZE)
        hue = 360 * (i / NUM_SPOTS)
        speed = random.uniform(MIN_SPOT_SPEED, MAX_SPOT_SPEED)
        # ratio = (size - MIN_SPOT_SIZE) / (MAX_SPOT_SIZE - MIN_SPOT_SIZE)
        # speed = (1 - ratio) * (MAX_SPOT_SPEED - MIN_SPOT_SPEED) + MIN_SPOT_SPEED
        spots[i] = (size, hue, speed)

    running = True
    while running:
        t = time.time()
        
        drawOneColor(ledStrip, BLACK)
        for i in range(NUM_SPOTS):
            size = spots[i][0]
            hue = spots[i][1]
            sat = 100
            val = 50
            speed = spots[i][2]
            pos = (speed * t) % 360
            drawSpot(ledStrip, [pos], hue, sat, val, size = size)
        ledStrip.show()

        drawOneColor(cpus[0], blendColors(ledStrip, 15, 19), 1, 3)
        cpus[0].show()
        
        for i in range(len(rams[0].colors)):
            rams[0].colors[i] = ledStrip.colors[13 + i]
            rams[1].colors[i] = ledStrip.colors[12 - i]
        rams[0].show()
        rams[1].show()

        limitFPS()

#NUM_SPOTS = 15
#MIN_SPOT_SIZE = 6
#MAX_SPOT_SIZE = 10
#MIN_SPOT_SPEED = 1
#MAX_SPOT_SPEED = 10
def runSpots2(client):
    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    ledStrip = mobo[0].zones[1]

    spots = [()] * NUM_SPOTS
    for i in range(NUM_SPOTS):
        pos = 360 * random.random()
        hue = 360 * (i / NUM_SPOTS)
        speed = random.uniform(MIN_SPOT_SPEED, MAX_SPOT_SPEED)
        size = random.uniform(MIN_SPOT_SIZE, MAX_SPOT_SIZE)
        spots[i] = (pos, hue, speed, size)

    running = True
    while running:
        t = time.time()
        
        drawOneColor(ledStrip, BLACK)
        for i in range(NUM_SPOTS):
            pos = spots[i][0]
            hue = spots[i][1]
            sat = 100
            val = 50
            speed = spots[i][2]
            size = spots[i][3] * (math.cos(t * speed) + 1) / 2
            drawSpot(ledStrip, [pos], hue, sat, val, size = size)

            if size < 0.1:
                pos = 360 * random.random()
                size = random.uniform(MIN_SPOT_SIZE, MAX_SPOT_SIZE)
                spots[i] = (pos, hue, speed, size)

        ledStrip.show()

        limitFPS()

# Returns a random color.
# Does not depend on time or position
def randomColor():
    hue = 360 * random.random()
    sat = 100
    val = 100 * random.random()
    return RGBColor.fromHSV(hue, sat, val)

# Return rainbow hue
# Colors change at COLOR_SPEED (degrees hue per second), offset by the position.
# t: time in seconds.
# pos[0]: color offset in degrees 0..360
def rainbowHue(t, pos):
    hue = ((t * COLOR_SPEED) + (pos[0] * COLOR_CYCLE)) % 360
    return hue    

# Return rainbow color.
# t: time in seconds.
# pos[0]: color offset in degrees 0..360
# value: value component of an hsv color
def rainbowColor(t, pos, value = 100):
    hue = rainbowHue(t, pos)
    sat = 100
    val = min(value, 100)
    # val = min(value, breathValue(t, [100 * pos[0] / 360]))
    return RGBColor.fromHSV(hue, sat, val)

# Draw a rainbow on device obj startLed...endLed, using t and startPos..endPos
# obj: device or zone
# t: time in seconds
# startLed: inclusive
# endLed: exclusive
# value: value component of an hsv color
def drawRainbow(obj, t, startPos, endPos, startLed = 0, endLed = None, value = 100):
    if endLed == None:
        endLed = len(obj.leds)
    numLed = endLed - startLed
    for i in range(startLed, endLed):
        pos = ((i - startLed) / numLed) * (endPos - startPos) + startPos
        obj.colors[i] = rainbowColor(t, [pos], value)

# Draw one color on device obj startLed..endLed
# obj: device or zone
# startLed: inclusive
# endLed: exclusive
def drawOneColor(obj, color, startLed = 0, endLed = None):
    if endLed == None:
        endLed = len(obj.leds)
    for i in range(startLed, endLed):
        obj.colors[i] = color

# Compute breath value 0..100
# Cycles at BREATH_SPEED (radians per second)
#  pos  1.0  1.5  0.0  0.5  1.0 (time in pi radians)
#  100    0    0  100    0    0
#   50    0   50  100   50    0
#    0    0  100  100  100    0
# t: time in seconds
# pos[0]: position offset 0..100
def breathValue(t, pos):
    a = (BREATH_SPEED * t) % (2.0 * math.pi)
    value = 100.0 * math.cos(a) + 100 - pos[0]
    value = max(0.0, value)
    value = min(value, 100.0)
    return value

# Return breath color
def breathColor(t, pos, hue, sat, valScale = 1.0):
    val = breathValue(t, pos) * valScale
    return RGBColor.fromHSV(hue, sat, val)

# Draw color at postion 0..360
def drawPos(obj, pos, color):
    i = mapPosToLed(pos)
    if i != None:
        obj.colors[i] = color

# Convert postion 0..360 to virtual LED number
# LED0     0 ..   6 (exclusive)
# LED1     6 ..  12
# LED59  354 .. 360
def mapPosToVLed(pos):
    pos %= 360
    vLed = int(pos / 6)
    return vLed

# Convert virtual LED to physical LED number
# This is specific to my installation of two 21 LED strips
def mapVLedToLed(vLed):
    led = None
    if vLed <= 20:
        led = vLed
    elif (vLed >= 30) and (vLed <= 50):
        led = vLed - 9
    return led

def mapPosToLed(pos):
    return mapVLedToLed(mapPosToVLed(pos))

# Draw a spot on the device.
# Uses the device's color array as a virtual canvas.  Colors are additive.
# obj: device or zone
# pos[0]: position in degrees
# hue, sat, val: color in HSV
# size: size of spot in degrees
def drawSpot(obj, pos, hue, sat, val, size = 6):
    pos = (pos[0] - size / 2) % 360
    while size > 0:
        vLed = mapPosToVLed(pos)
        len = min(6.0 * vLed + 6 - pos, size)
        i = mapVLedToLed(vLed)
        if i != None:
            scale = len / 6
            obj.colors[i] = addColors(obj.colors[i], RGBColor.fromHSV(hue, sat, val * scale))
        pos = (pos + len) % 360
        size -= len

def addColors(color1, color2):
    red = min(color1.red + color2.red, 255)
    grn = min(color1.green + color2.green, 255)
    blu = min(color1.blue + color2.blue, 255)
    return RGBColor(red, grn, blu)

# startLed, endLed: inclusive
def blendColors(obj, startLed, endLed):
    endLed += 1
    red, grn, blu = 0, 0, 0
    for i in range(startLed, endLed):
        red += obj.colors[i].red
        grn += obj.colors[i].green
        blu += obj.colors[i].blue
    len = abs(endLed - startLed)
    red = min(int(red / len), 255)
    grn = min(int(grn / len), 255)
    blu = min(int(blu / len), 255)
    return RGBColor(red, grn, blu)

frames = 0
startTime = None
pause = PAUSE_DELTA  # start with some delay
# Limit frame rate to about maxFPS
# TODO: Refactor this as a class
def limitFPS(maxFPS = MAX_FPS):
    global pause
    global frames
    global startTime

    frames += 1
    now = time.time()
    if startTime == None:
        startTime = now
        return
    if now > startTime + 1.0:
        fps = frames / (now - startTime)
        print('FPS: {:.4}, time: {:.4}ms'.format(fps, 1000 / fps))
        startTime = now
        frames = 0
        diff = (1.0 / maxFPS) - (1.0 / fps)
        if (diff > PAUSE_DELTA):
            pause += PAUSE_DELTA
    if pause > 0:
        time.sleep(pause)

main()
print('DONE')
