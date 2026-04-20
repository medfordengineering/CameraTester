#import time
from pulse_measure import PulseWidth
from pulse_gap import FirstCurtain
from pulse_drop import SecondCurtain
from machine import Pin, SPI, PWM

import ssd1306

SHUTTER_SPEED = 0
EV_SOURCE = 1
MENU = 2
LINE = 10

LED_PIN = 20

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

top_frame=PulseWidth(13)
#sensor2=PulseWidth(12)

front_curtain=FirstCurtain(4,12,13)
rear_curtain=SecondCurtain(3,12, 13)

light = Pin(LED_PIN, Pin.OUT)
# Set up PWM Pin
#panel_pin = machine.Pin(LED_PIN)
#pwm = PWM(panel_pin)
#frequency = 5000
#pwm.freq(frequency)

btn_up = Pin(21, Pin.IN, Pin.PULL_UP)
btn_dn = Pin(22, Pin.IN, Pin.PULL_UP)
btn_sw = Pin(18, Pin.IN, Pin.PULL_UP)

dimming_level = 30000

global state
state = MENU

menu_screen()

pulse1 = False
pulse2 = False
pulse3 = False
pulse4 = False

while True:

    if state == SHUTTER_SPEED:
            
        #SET LED PANEL TO FULL ON--NO PWM
        if pulse3 == False:
            period = front_curtain.curtain_speed()
            if period != 0:
                front_curtain_travel = 24* period/16
                pulse3 = True
        
        if pulse4 == False:
            period = rear_curtain.curtain_speed()
            if period != 0:
                rear_curtain_travel = 24* period/16
                pulse4 = True
                
        if pulse2 == False:
            period = top_frame.pulse_width()
            if period != 0:
                speed_top = 1000000/period
                pulse2 = True

        if (pulse3 == True) and (pulse4 == True) and (pulse2 == True):
                display.fill_rect(0, LINE, 100, LINE*3, 0)
                display.text("FC: " + str(front_curtain_travel) +"us",0,LINE,1)
                display.text("RC: " + str(rear_curtain_travel) +"us",0,LINE*2,1)
                display.text("SS1: 1/" + str(int(speed_top)), 0,LINE*3,1) #ROUND SPEED
                display.text("1) Restart", 0,LINE*5,1)
                display.show()
                pulse2 = False
                pulse3 = False
                pulse4 = False
                state = MENU
            
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
            #Turn on light panel
            
            light.value(1)
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
                    
   
    


