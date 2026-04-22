#import time
from pulse_measure import PulseWidth
from first_curtain import FirstCurtain
from second_curtain import SecondCurtain
from machine import Pin, SPI, PWM

import ssd1306

SHUTTER_SPEED = 0
EV_SOURCE = 1
MENU = 2
LINE = 10

LED_PIN = 20
BTN_ONE = 21
BTN_TWO = 22
BTN_TRE = 18

TOP_SENSOR = 13
MID_SENSOR = 12
BTM_SENSOR = 11

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

top_sensor=PulseWidth(TOP_SENSOR)
mid_sensor=PulseWidth(MID_SENSOR)
btm_sensor=PulseWidth(BTM_SENSOR)

front_curtain=FirstCurtain(4,BTM_SENSOR,TOP_SENSOR)
rear_curtain=SecondCurtain(3,BTM_SENSOR, TOP_SENSOR)

light = Pin(LED_PIN, Pin.OUT)
# Set up PWM Pin
#panel_pin = machine.Pin(LED_PIN)
#pwm = PWM(panel_pin)
#frequency = 5000
#pwm.freq(frequency)

btn_up = Pin(BTN_ONE, Pin.IN, Pin.PULL_UP)
btn_dn = Pin(BTN_TWO, Pin.IN, Pin.PULL_UP)
btn_sw = Pin(BTN_TRE, Pin.IN, Pin.PULL_UP)

dimming_level = 30000

global state
state = MENU

menu_screen()

ct_1st = False
ct_2nd = False

ss_top = False
ss_mid = False
ss_btm = False

while True:

    if state == SHUTTER_SPEED:
            
        #SET LED PANEL TO FULL ON--NO PWM
        if ct_1st == False:
            period = front_curtain.curtain_speed()
            if period != 0:
                front_curtain_travel = 22.5* period/16
                #front_curtain_travel = period
                ct_1st = True
        
        if ct_2nd == False:
            period = rear_curtain.curtain_speed()
            if period != 0:
                rear_curtain_travel = 25.5* period/16
                #rear_curtain_travel = period
                ct_2nd = True
                
        if ss_top == False:
            period = top_sensor.pulse_width()
            if period != 0:
                speed_top = 1000000/(period-200)
                ss_top = True
                
        if ss_mid == False:
            period = mid_sensor.pulse_width()
            if period != 0:
                speed_mid = 1000000/(period-200)
                ss_mid = True
                
        if ss_btm == False:
            period = btm_sensor.pulse_width()
            if period != 0:
                speed_btm = 1000000/(period-200)
                ss_btm = True

        if (ct_2nd == True) and (ct_1st == True) and (ss_btm == True) and (ss_mid == True) and (ss_top == True):
                display.fill_rect(0, LINE, 100, LINE*3, 0)
                display.text("FC: " + str(front_curtain_travel) +"us",0,LINE,1)
                display.text("RC: " + str(rear_curtain_travel) +"us",0,LINE*2,1)
                display.text("SST: 1/" + str(int(speed_top)), 0,LINE*3,1) #ROUND SPEED
                display.text("SSM: 1/" + str(int(speed_mid)), 0,LINE*4,1) #ROUND SPEED
                display.text("SSB: 1/" + str(int(speed_btm)), 0,LINE*5,1) #ROUND SPEED

                display.text("1) Restart", 0,LINE*6,1)
                display.show()
                ct_1st = False
                ct_2nd = False
                ss_btm = False
                ss_mid = False
                ss_top = False
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
                    
   
    


