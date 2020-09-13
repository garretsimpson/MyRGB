import time
import random
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor, DeviceType

DURATION = 300  # Total time in seconds
FREQ = 20  # Changes per second
COLOR_CYCLE = 1 # number of color cycles
COLOR_SPEED = 60  # degrees of hue per second

PAUSE = 0.5  # Duration in seconds to wait for OpenRGB.  Seems to crash on some calls without it.

BLACK = RGBColor(0, 0, 0)
WHITE = RGBColor(255, 255, 255)
RED = RGBColor(255, 0, 0)
GREEN = RGBColor(0, 255, 0)
BLUE = RGBColor(0, 0, 255)

def main():
    client = OpenRGBClient()
    printInfo(client.devices)
    client.clear()
    time.sleep(PAUSE)

    # client.load_profile('basic.orp')
    # client.show()

    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    ledStrip = mobo[0].zones[1]
    ledStrip.resize(42)
    time.sleep(PAUSE)

    runRainbow(client)
    # runRandom(client)
    # runRacer(client)

def runRainbow(client):
    for device in client.devices:
        device.set_mode('Direct')

    mobo = client.get_devices_by_type(DeviceType.MOTHERBOARD)
    rams = client.get_devices_by_type(DeviceType.DRAM)
    gpus = client.get_devices_by_type(DeviceType.GPU)
    cpus = client.get_devices_by_type(DeviceType.COOLER)

    cpus[0].zones[0].set_color(BLACK)  # Logo

#    chase = cpus[0].modes[5]
#    chase.speed = 1
#    cpus[0].set_mode(chase)
#    time.sleep(PAUSE)
    
    hue = 0
    running = True
    # startTime = time.time()
    # endTime = startTime + DURATION
    while running:
        ledStrip = mobo[0].zones[1]
        rainbow(ledStrip, hue, hue + 135, 0, 21, value = 20)
        rainbow(ledStrip, hue + 180, hue + 315, 21, 42, value = 20)
        ledStrip.show()

        mbZone = mobo[0].zones[2]
        oneColor(mbZone, hue + 140, 0, 1)
        oneColor(mbZone, hue + 235, 3, 4)
        mbZone.show()

        cpuFan = cpus[0].zones[1]
        oneColor(cpuFan, hue + 110, value = 75)
        cpuFan.show()
        cpuRing = cpus[0].zones[2]
        oneColor(cpuRing, hue + 110, value = 75)
        cpuRing.show()

        ram0 = rams[0].zones[0]
        rainbow(ram0, hue + 80, hue - 5)
        ram0.show()
        ram1 = rams[1].zones[0]
        rainbow(ram1, hue + 75, hue - 10)
        ram1.show()

        gpuLed = gpus[0].zones[0]
        oneColor(gpuLed, hue + 270)
        gpuLed.show()

        time.sleep(1.0 / FREQ)

        hue += COLOR_SPEED / FREQ
        hue %= 360

        # if time.time() > endTime:
        #     running = False


def runRandom(client):
    for device in client.devices:
        device.set_mode('Direct')

    numDevices = len(client.devices)
    running = True
    while running:
        device = client.devices[random.randrange(numDevices)]
        randomColor(device)
        device.show()

        time.sleep(1.0 / FREQ)

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
        pos += SPEED / FREQ
        pos %= 360
        paintPos(ledStrip, pos, RED)
        ledStrip.show()
        time.sleep(1.0 / FREQ)

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
