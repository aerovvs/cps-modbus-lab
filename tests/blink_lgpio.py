#!/usr/bin/env python3
# blink_lgpio.py
import lgpio, time

h = lgpio.gpiochip_open(0)      # open /dev/gpiochip0 / connection to GPIO chip
LED = 17 # uses pin 17
lgpio.gpio_claim_output(h, LED, 0)
""" 0 = starts with led off, gpio_claim_output = send signals out"""

lgpio.gpio_write(h, LED, 1)     # LED ON
time.sleep(1) # wait 1 sec
lgpio.gpio_write(h, LED, 0)     # LED OFF

lgpio.gpiochip_close(h)
print("lgpio test OK")
