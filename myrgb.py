import time
import random
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType

DURATION = 300  # Total time in seconds
MAX_FREQ = 30  # Changes per second
COLOR_CYCLE = 1 # number of color cycles
COLOR_SPEED = 30  # degrees of hue per second

WAIT = 1.0  # Duration in seconds to wait for OpenRGB.  Seems to crash on some calls without it.
PAUSE_DELTA = 0.015  # Increments of 15ms.

BLACK = RGBColor(0, 0, 0)
WHITE = RGBColor(255, 255, 255)
RED = RGBColor(255, 0, 0)
GREEN = RGBColor(0, 255, 0)
BLUE = RGBColor(0, 0, 255)

def main():
    client = OpenRGBClient()
    printInfo(client.devices)
    client.clear()
    time.sleep(WAIT)

    # client.load_profile('basic.orp')
    # client.show()

    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    ledStrip = mobo[0].zones[1]
    ledStrip.resize(42)
    # time.sleep(PAUSE)

    runRainbow(client)
    # runRandom(client)
    # runRacer(client)

def runRainbow(client):
    for device in client.devices:
        device.set_mode('Direct')
    time.sleep(WAIT)

    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    rams = client.get_devices_by_type(DeviceType.DRAM)
    gpus = client.get_devices_by_type(DeviceType.GPU)
    cpus = client.get_devices_by_type(DeviceType.COOLER)

    gpus[0].set_color(WHITE)

#    chase = cpus[0].modes[5]
#    chase.speed = 1
#    cpus[0].set_mode(chase)
#    time.sleep(PAUSE)
    
    hue = 0
    startTime = time.time()
    frames = 0
    fps = MAX_FREQ
    pause = 0.0
    running = True
    while running:
        ledStrip = mobo[0].zones[1]
        rainbow(ledStrip, hue, hue + 135, 0, 21, value = 20)
        rainbow(ledStrip, hue + 180, hue + 315, 21, 42, value = 20)
        ledStrip.show()

        mbZone = mobo[0].zones[2]
        oneColor(mbZone, hue + 140, 0, 1)
        mbZone.show()

        oneColor(cpus[0], hue + 110, 1, 3, value = 75)
        cpus[0].show()

        rainbow(rams[0], hue + 80, hue - 5)
        rams[0].show()
        rainbow(rams[1], hue + 75, hue - 10)
        rams[1].show()

        frames += 1
        now = time.time()
        if now > startTime + 1.0:
            fps = frames / (now - startTime)
            print('FPS: {:.4}, time: {:.4}ms'.format(fps, 1000 / fps))
            startTime = now
            frames = 0
            diff = (1.0 / MAX_FREQ) - (1.0 / fps)
            if (fps > MAX_FREQ) and (diff > PAUSE_DELTA):
                pause += PAUSE_DELTA

        time.sleep(pause)

        hue += COLOR_SPEED / fps
        hue %= 360

def runRandom(client):
    for device in client.devices:
        device.set_mode('Direct')

    numDevices = len(client.devices)
    running = True
    while running:
        device = client.devices[random.randrange(numDevices)]
        randomColor(device)
        device.show()

        time.sleep(1.0 / MAX_FREQ)

def runRacer(client):
    # FREQ = 50
    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)

    for device in mobo:
        device.set_mode('Direct')

    ledStrip = mobo[0].zones[1]
    oneColor(ledStrip, WHITE)
    ledStrip.show()

    SPEED = 180
    pos = 0
    running = True
    while running:
        paintPos(ledStrip, pos, WHITE)
        pos += SPEED / MAX_FREQ
        pos %= 360
        paintPos(ledStrip, pos, RED)
        ledStrip.show()
        time.sleep(1.0 / MAX_FREQ)

def printInfo(devices):
    for device in devices:
        print('Device[{}]'.format(device.device_id))
        print(device.name)
        for zone in device.zones:
            print('  zone[{}] {}, leds: {}'.format(zone.id, zone.name, len(zone.leds)))
        print()

def oneColor(obj, color, startLed = 0, endLed = None, value = 100):
    if endLed == None:
        endLed = len(obj.leds)
    for i in range(startLed, endLed):
        if isinstance(color, (int, float)):
            color *= COLOR_CYCLE
            obj.colors[i] = RGBColor.fromHSV(color, 100, value)
        elif isinstance(color, RGBColor):
            obj.colors[i] = color

# startLed: inclusive
# endLed: exclusive
def rainbow(obj, startHue, endHue, startLed = 0, endLed = None, value = 100):
    if endLed == None:
        endLed = len(obj.leds)
    numLed = endLed - startLed
    for i in range(startLed, endLed):
        hue = (endHue - startHue) * ((i - startLed) / numLed) + startHue
        hue *= COLOR_CYCLE
        obj.colors[i] = RGBColor.fromHSV(hue, 100, value)

def randomColor(obj):
    hue = random.randrange(360)
    sat = 100
    val = random.randrange(100)
    color = RGBColor.fromHSV(hue, sat, val)
    i = random.randrange(len(obj.colors))
    obj.colors[i] = color

def paintPos(obj, pos, color):
    i = mapPosToLed(pos)
    if i != None:
        obj.colors[i] = color

# This is specific to my installation of two 21 LED strips
def mapPosToLed(pos):
    pos %= 360
    value = None
    if pos < 135:
        value = int(21 * (pos / 135))
    elif pos > 180 and pos < 315:
        value = 21 + int(21 * ((pos - 180) / 135))
    return value

main()
print('DONE')
