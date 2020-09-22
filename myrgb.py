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
WHITE = RGBColor(255, 255, 255)
RED = RGBColor(255, 0, 0)
GREEN = RGBColor(0, 255, 0)
BLUE = RGBColor(0, 0, 255)
YELLOW = RGBColor(255, 255, 0)

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
    runBreathing(client)
    # runClock(client)

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
    # Pick a color
    MIN_SAT = 80
    MAX_SAT = 100
    hue = random.randrange(360)
    sat = random.randrange(MAX_SAT - MIN_SAT) + MIN_SAT

    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    cpus = client.get_devices_by_type(DeviceType.COOLER)
    rams = client.get_devices_by_type(DeviceType.DRAM)
    gpus = client.get_devices_by_type(DeviceType.GPU)
    ledStrip = mobo[0].zones[1]

    running = True
    while running:
        t = time.time()

        # Pick a new color
        val = breathValue(t, [0])
        if (val < 0.01):
            hue = random.randrange(360)
            sat = random.randrange(MAX_SAT - MIN_SAT) + MIN_SAT

        drawOneColor(cpus[0], breathColor(t, [0], hue, sat), 1, 2)
        drawOneColor(cpus[0], breathColor(t, [20], hue, sat), 2, 3)
        cpus[0].show()

        drawOneColor(rams[0], breathColor(t, [30], hue, sat))
        rams[0].show()
        drawOneColor(rams[1], breathColor(t, [40], hue, sat))
        rams[1].show()

        drawOneColor(gpus[0], breathColor(t, [50], hue, sat))
        gpus[0].show()

        drawOneColor(ledStrip, breathColor(t, [60], hue, sat, 0.2), 0, 21)
        drawOneColor(ledStrip, breathColor(t, [100], hue, sat, 0.2), 21, 42)
        ledStrip.show()

        limitFPS()

def runClock(client):
    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    ledStrip = mobo[0].zones[1]

    drawOneColor(ledStrip, BLUE)
    ledStrip.show()

    running = True
    prevPos = 0
    while running:
        t = time.time()
        currPos = -6 * (t - 16 % 60.0) 
        drawPos(ledStrip, prevPos, BLUE)
        drawPos(ledStrip, currPos, YELLOW)
        ledStrip.show()
        
        prevPos = currPos

        limitFPS()

# Returns a random color.
# Does not depend on time or position
def randomColor():
    hue = random.randrange(360)
    sat = 100
    val = random.randrange(100)
    return RGBColor.fromHSV(hue, sat, val)

# Return rainbow color.
# Colors change at COLOR_SPEED (degrees hue per second), offset by the position.
# t: time in seconds.
# pos[0]: color offset in degrees 0..360
# value: value component of an hsv color
def rainbowColor(t, pos, value = 100):
    hue = ((t * COLOR_SPEED) + (pos[0] * COLOR_CYCLE)) % 360
    sat = 100
    val = min(value, 100)
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
#  pos  1.0  1.5  0.0  0.5 (time in pi radians)
#    0    0  100  100  100  
#   50    0   50  100   50
#  100    0    0  100    0
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

# Return LED number based on position 0..360
# This is specific to my installation of two 21 LED strips
def mapPosToLed(pos):
    pos %= 360
    num = None
    if pos < 135:
        num = int(21 * (pos / 135.0))
    elif (pos >= 180) and (pos < 315):
        num = 21 + int(21 * ((pos - 180) / 135.0))
    return num

pause = PAUSE_DELTA  # start with some delay
frames = 0
startTime = None
# Limit frame rate to about MAX_FPS
# TODO: Refactor this as a class
def limitFPS():
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
        diff = (1.0 / MAX_FPS) - (1.0 / fps)
        if (diff > PAUSE_DELTA):
            pause += PAUSE_DELTA
    if pause > 0:
        time.sleep(pause)

main()
print('DONE')
