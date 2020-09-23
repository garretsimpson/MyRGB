# MyRBG - My prototype RGB scripts.

Project: https://gitlab.com/FatCatX/myrgb

## Projects Used

- OpenRGB server: https://gitlab.com/CalcProgrammer1/OpenRGB
- OpenRGB python: https://github.com/jath03/openrgb-python

## RGB hardware

    Device[0]
    ASUS Aura DRAM
    zone[0] Unknown, leds: 8

    Device[1]
    ASUS Aura DRAM
    zone[0] Unknown, leds: 8

    Device[2]
    Gigabyte GPU
    zone[0] GPU Zone, leds: 1

    Device[3]
    AMD Wraith Prism
    zone[0] Logo, leds: 1
    zone[1] Fan, leds: 1
    zone[2] Ring, leds: 1

    Device[4]
    X570 AORUS ELITE WIFI
    zone[0] D_LED1 Bottom, leds: 0
    zone[1] D_LED2 Top, leds: 42
    zone[2] Motherboard, leds: 8

## Notes

- Case: Fractal Design Meshify C Black, Dark Tint Tempered Glass Window
- The inside demensions of the case are 300mm x 300mm.
- D_LED2 has two LED strips, each has 21 LEDs: Airgoo NEON Digital RGB
- The strips are located around the inner edge of the case, 0 to 120 degrees and 180 to 300 degrees.
- The LEDs on the strips are 20mm apart, or 60 (virtual) LEDs.  This makes displays like clock simple.
- The rainbow effect uses standard polar coordinates (0 at 3 o'clock, incrementing counter-clockwise).
- The methods use time (in seconds) and speed constants rather than incrementing counters. This make the displays always run at the same rate, no mater the refresh rate.
- The limitFPS() method is used to reduce the refresh rate.  This helps reduce CPU usage.

## Ideas

- Use configuration files (data driven).
- Map physical devices to a virtual canvas.
- Drive display with image files (e.g. animatged GIFs).
