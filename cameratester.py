from time import sleep
from pulse_measure import PulseWidth
from machine import Pin, SPI, PWM
#from enum import Enum
import ssd1306

SHUTTER_SPEED = 0
EV_SOURCE = 1
MENU = 2
LINE = 10



def menu_screen():
    display.fill(0)
    display.text("MENU",12,0,1)
    display.text("1) Shutter Speed",0,LINE,1)
    display.text("2) Light Meter",0,LINE*2,1)
    display.show()

spi = SPI(0, baudrate=20_000_000, polarity=0, phase=0, sck=Pin(2), mosi=Pin(3))

# Control Pins
dc = Pin(4)    # Data/Command
rst = Pin(0)   # Reset
cs = Pin(1)    # Chip Select
display = ssd1306.SSD1306_SPI(128, 64, spi, dc, rst, cs)
display.rotate(True)
display.fill(0)                         # Clear screen (0=black, 1=white)
display.show()

BX = 0
BY = 0
BW = 90
BH = 30

sensor1=PulseWidth(13)
sensor2=PulseWidth(12)

# Set up PWM Pin
panel_pin = machine.Pin(20)
pwm = PWM(panel_pin)
frequency = 5000
pwm.freq(frequency)

btn_up = Pin(21, Pin.IN, Pin.PULL_UP)
btn_dn = Pin(22, Pin.IN, Pin.PULL_UP)
btn_sw = Pin(18, Pin.IN, Pin.PULL_UP)

dimming_level = 30000

global state
#state = EV_SOURCE
#state = SHUTTER_SPEED
state = MENU
menu_screen()


while True:
    if state == SHUTTER_SPEED:
            
        #SET LED PANEL TO FULL ON--NO PWM

        #THE FOLLOWING LINE IS BLOCKING
        period = sensor1.pulse_width()
        
        speed = period /1000000
        speed = 1/speed
        
        display.fill_rect(0, LINE, 100, LINE*3, 0)
        display.text("TI: " + str(period) +"us",0,LINE,1)
        display.text("SS: 1/" + str(int(speed)), 0,LINE*2,1) #ROUND SPEED
        display.text("1) Restart", 0,LINE*3,1)
        display.show()
        state = MENU
        #display.fill_rect(0, 20, 120, 8, 0)  
        #display.text("Press Next",0,20,1)
        #display.show()
            
    elif state == EV_SOURCE:
        pwm.duty_u16(dimming_level)
        display.fill_rect(0, 0, 100, 8, 0)
        display.text("EV: " + str(dimming_level), 0, 0,1)
        display.show()
        if btn_up.value() == 0:
            dimming_level += 10
            if dimming_level > 0xFFFF:
                dimming_level = 0xFFFF
                
        if btn_dn.value() == 0:
            dimming_level -= 10
            if dimming_level < 0:
                dimming_level = 0
            
        if btn_sw.value() == 0:
            state = MENU
            display.fill_rect(0, 20, 120, 8, 0)  
            display.text("Press Next",0,20,1)
            display.show()
                    
    elif state == MENU:
        if btn_up.value() == 0:
            state = SHUTTER_SPEED
            #display.fill_rect(0, 20, 120, 8, 0)
            display.fill(0)
            display.text("SHUTTER SPEED",15,0,1)
            display.text("(Ready)",24,10,1)
            display.show()
            
        if btn_dn.value() == 0:
            state = EV_SOURCE
            display.fill_rect(0, 20, 120, 8, 0)  
            display.text("Exposure Value",0,20,1)
            display.show()
                    
   
    